from sqlalchemy import ForeignKey, Column, DateTime, Integer, func
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.models.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    owner_email = Column(String, ForeignKey("users.email"))
    priority = Column(Integer, nullable=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="tasks")
