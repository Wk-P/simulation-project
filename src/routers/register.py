from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.repositories.user import UserRepository
from src.schemas.user.register import RegisterNormalUserResponse, RegisterNormalUserRequest, RegisterStaffUserRequest, RegisterStaffUserResponse, RegisterAdminUserRequest, RegisterAdminUserResponse
from src.services.user.register import user_register_svc, staff_register_svc, admin_register_svc

router = APIRouter(prefix="/register")


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post('/user')
def user_register(user: RegisterNormalUserRequest, repo: UserRepository = Depends(get_user_repo)) -> RegisterNormalUserResponse:
    return user_register_svc(user, repo)


@router.post('/staff')
def staff_register(user: RegisterStaffUserRequest, repo: UserRepository = Depends(get_user_repo)) -> RegisterStaffUserResponse:
    return staff_register_svc(user, repo)


@router.post('/admin')
def admin_register(user: RegisterAdminUserRequest, repo: UserRepository = Depends(get_user_repo)) -> RegisterAdminUserResponse:
    return admin_register_svc(user, repo)
