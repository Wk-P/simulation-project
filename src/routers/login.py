from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from src.db.session import get_db
from src.repositories.user import UserRepository
from src.schemas.user.login import LoginUserRequest, LoginUserResponse
from src.services.user.login import user_login_svc

router = APIRouter(prefix="/login")

def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post('/user')
def user_login(user: LoginUserRequest, repo: UserRepository = Depends(get_user_repo)) -> LoginUserResponse:
    return user_login_svc(user, repo)