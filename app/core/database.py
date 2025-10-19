from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Ensure we use the synchronous PostgreSQL driver
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    # Keep the URL as is for psycopg2
    pass
elif database_url.startswith("postgres://"):
    # Convert postgres:// to postgresql:// for psycopg2
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Create database engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Import models to register metadata before create_all
    try:
        import app.models.user  # noqa: F401
        import app.models.project  # noqa: F401
        import app.models.investment  # noqa: F401
        import app.models.payment  # noqa: F401
        import app.models.session  # noqa: F401
        import app.models.support  # noqa: F401
        import app.models.notification  # noqa: F401
        import app.models.kyc  # noqa: F401
        import app.models.docsign  # noqa: F401
    except Exception:
        # Best-effort; continue to create_all
        pass
    Base.metadata.create_all(bind=engine) 