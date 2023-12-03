from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.shared_list import SharedList
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    user_name = Column(String)

    tasks = relationship("Task", back_populates="owner")

    owned_shared_lists = relationship("SharedList", foreign_keys=[SharedList.owner_email], back_populates="owner")
    invited_shared_lists = relationship("SharedList", foreign_keys=[SharedList.invited_user_email],
                                        back_populates="invited_user")
