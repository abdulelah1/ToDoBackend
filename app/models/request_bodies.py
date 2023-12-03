from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
import re



class NewUser(BaseModel):

    email: EmailStr
    password: str
    name: str

    @field_validator("email")
    def validate_email(value):
        try:
            emailInfp = validate_email(value, check_deliverability=True)
        except EmailNotValidError as e:
            raise e

        return emailInfp.normalized

    @field_validator("password")
    def validate_password(value):
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')
        if password_pattern.match(value):
            return value
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Password must have at least 1 Capital, 1 Small, 1 Number, and minimum length "
                                       "of 8 Characters.")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TaskTitle(BaseModel):
    title: str


class TaskPriority(BaseModel):
    priority: int


class UserInvitation(BaseModel):
    invited_user_email: EmailStr