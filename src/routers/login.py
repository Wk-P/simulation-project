from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from src.db.session import get_db
from src.repositories.user import UserRepository
from src.schemas.user import NormalUserResponse, NormalUserRequest, StaffUserRequest, StaffUserResponse, AdminUserRequest, AdminUserResponse
from src.services.user.login import user_login_svc, staff_login_svc, admin_login_svc

router = APIRouter(prefix="/login")

def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post('/user')
def user_login(user: NormalUserRequest, repo: UserRepository = Depends(get_user_repo)) -> NormalUserResponse:
    return user_login_svc(user, repo)


@router.post('/staff')
def staff_login(user: StaffUserRequest, repo: UserRepository = Depends(get_user_repo)) -> StaffUserResponse:
    return staff_login_svc(user, repo)


@router.post('/admin')
def admin_login(user: AdminUserRequest, repo: UserRepository = Depends(get_user_repo)) -> AdminUserResponse:
    return admin_login_svc(user, repo)