import asyncio
import contextlib
import json
from typing import Callable, Dict, Optional
import redis.asyncio as redis
from app.core.config import settings


class RedisPubSubBroker:
    """Redis-based pub/sub broker for scalable fanout.

    Channels:
      - ticket:<ticket_id>:message  (payload is JSON message to broadcast)
    """

    def __init__(self) -> None:
        self._redis: Optional[redis.Redis] = None
        self._pub: Optional[redis.Redis] = None
        self._sub_task: Optional[asyncio.Task] = None
        self._callbacks: Dict[str, Callable[[dict], asyncio.Future]] = {}

    async def start(self) -> None:
        if self._redis is not None:
            return
        self._redis = redis.from_url(settings.redis_url, decode_responses=True)
        self._pub = self._redis

    async def stop(self) -> None:
        if self._sub_task:
            self._sub_task.cancel()
            with contextlib.suppress(Exception):
                await self._sub_task
            self._sub_task = None
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
            self._pub = None

    async def publish_ticket_message(self, ticket_id: str, message: dict) -> None:
        if not self._pub:
            await self.start()
        channel = f"ticket:{ticket_id}:message"
        await self._pub.publish(channel, json.dumps(message))

    async def subscribe_ticket(self, ticket_id: str, on_message: Callable[[dict], asyncio.Future]) -> None:
        # Register callback by channel
        channel = f"ticket:{ticket_id}:message"
        self._callbacks[channel] = on_message
        if self._sub_task is None:
            self._sub_task = asyncio.create_task(self._listen_loop())

    async def unsubscribe_ticket(self, ticket_id: str) -> None:
        channel = f"ticket:{ticket_id}:message"
        self._callbacks.pop(channel, None)

    async def _listen_loop(self) -> None:
        assert self._redis is not None
        pubsub = self._redis.pubsub()
        # subscribe to patterns for tickets and notifications
        await pubsub.psubscribe("ticket:*:message")
        await pubsub.psubscribe("notif:user:*")
        async for msg in pubsub.listen():
            if msg is None:
                await asyncio.sleep(0)
                continue
            if msg.get("type") not in {"pmessage", "message"}:
                continue
            channel = msg.get("channel")
            data = msg.get("data")
            try:
                payload = json.loads(data) if isinstance(data, str) else data
            except Exception:
                continue
            cb = self._callbacks.get(channel)
            if cb:
                try:
                    await cb(payload)
                except Exception:
                    # swallow to keep loop alive
                    pass

    async def publish_notification(self, user_id: str, message: dict) -> None:
        if not self._pub:
            await self.start()
        channel = f"notif:user:{user_id}"
        await self._pub.publish(channel, json.dumps(message))

    async def subscribe_user_notifications(self, user_id: str, on_message: Callable[[dict], asyncio.Future]) -> None:
        channel = f"notif:user:{user_id}"
        self._callbacks[channel] = on_message
        if self._sub_task is None:
            self._sub_task = asyncio.create_task(self._listen_loop())

    async def unsubscribe_user_notifications(self, user_id: str) -> None:
        channel = f"notif:user:{user_id}"
        self._callbacks.pop(channel, None)


broker = RedisPubSubBroker()



