from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.models.base import Base


class SharedList(Base):

    __tablename__ = "shared_lists"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    owner_email = Column(String, ForeignKey("users.email"))
    invited_user_email = Column(String, ForeignKey("users.email"))

    owner = relationship("User", foreign_keys=[owner_email], back_populates="owned_shared_lists")
    invited_user = relationship("User", foreign_keys=[invited_user_email], back_populates="invited_shared_lists")