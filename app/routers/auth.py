from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.request_bodies import LoginRequest, NewUser
from app.utils.utils import generate_hash
from app.dependencies.jwt_management import generate_jwt_token
from app.models.user import User


router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: NewUser,  db: Session = Depends(get_db)):
    try:
        existing_user = db.execute(select(User).filter(User.email == user.email)).scalar()
        if existing_user is None:
            hashed_password = generate_hash(user.password)
            new_user = User(email=user.email, hashed_password=hashed_password, user_name=user.name)

            db.add(new_user)
            db.commit()

            response = {"message": "User created successfully",
                        "token": generate_jwt_token(user_email=user.email),
                        "success": True}
            return response
        else:
            print("Hello")
            return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already in use")

    except Exception as e:
        db.rollback()
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    hashed_password = generate_hash(login_request.password)

    stmt = (
        select(User)
        .where(User.email == login_request.email)
        .where(User.hashed_password == hashed_password)
    )

    result = db.execute(stmt)
    user_exists = result.scalar()

    if user_exists is not None:
        response = {"message": "User logged in successfully",
                    "token": generate_jwt_token(user_email=login_request.email),
                    "success": True}
        return response

    else:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User doesn't exist")
