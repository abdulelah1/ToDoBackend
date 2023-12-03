from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.request_bodies import UserInvitation
from app.models.user import User
from app.models.shared_list import SharedList
from app.models.task import Task
from app.dependencies.jwt_management import get_current_user_email
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer
from email_validator import validate_email, EmailNotValidError

router = APIRouter()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/", status_code=status.HTTP_200_OK)
def get_shared_lists(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    names_query = (
        db.query(User.user_name, User.email)
        .join(SharedList, User.email == SharedList.owner_email)
        .filter(SharedList.invited_user_email == user_email)
        .all()
    )

    if len(names_query) == 0:
        response_data = {'message': "User doesn't have any shared lists", "success": True}
        return JSONResponse(status_code=204, content=response_data)
    else:
        names_dict = {email: {"name": name, "tasks": []} for name, email in names_query}

        tasks_query = (
            db.query(Task)
            .join(SharedList, Task.owner_email == SharedList.owner_email)
            .filter(SharedList.invited_user_email == user_email)
            .all()
        )

        for row in tasks_query:
            owner_email = row.owner_email
            task_dict = {
                "title": row.title,
            }
            names_dict[owner_email]["tasks"].append(task_dict)

        result_list = list(names_dict.values())

        response = {'data': result_list, "success": True}
        return response




@router.post("/", status_code=status.HTTP_201_CREATED)
async def share_list(req_body: UserInvitation, token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if user_email == req_body.invited_user_email:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User can not invite himself")
    else:

        try:
            emailInfo = validate_email(req_body.invited_user_email, check_deliverability=False)
        except EmailNotValidError as e:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")

        stmt = (
            select(User)
            .where(User.email == emailInfo.normalized)
        )

        result = db.execute(stmt)
        user_existing = result.scalar()

        if user_existing is not None:
            new_shared_list = SharedList(owner_email=user_email, invited_user_email=req_body.invited_user_email)
            db.add(new_shared_list)

            try:
                db.commit()
                db.refresh(new_shared_list)

                if new_shared_list.id is not None:
                    response = {"message": "List shared successfully", "success": True}
                    return response

            except Exception as e:
                db.rollback()
                return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invited user does not exist")


@router.delete("/", status_code=status.HTTP_200_OK)
async def stop_sharing(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        db.query(SharedList).filter(SharedList.owner_email == user_email).delete()
        db.commit()

        response = {"message": "List sharing stopped successfully", "success": True}
        return response
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


