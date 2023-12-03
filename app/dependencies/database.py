from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base


from app.config.settings import settings

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        yield db
    finally:
        db.close()