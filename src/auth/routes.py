from fastapi import APIRouter,Depends , status
from .schemas import UserCreateModel,UserModel,UserLoginModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from fastapi.exceptions import HTTPException
from .utils import create_access_token , decode_token ,verify_password
from datetime import timedelta,datetime
from fastapi.responses import JSONResponse
from .dependencies import AccessTokenBearer,RefreshTokenBearer,revoked_tokens
# from src.db.redis import add_jti_to_blocklist

auth_router = APIRouter()
user_service=UserService()
REFRESH_TOKEN_EXPIRY=2

@auth_router.post('/signup' , response_model=UserModel)
async def create_user_Account(user_data : UserCreateModel ,session:AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email,session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "User with this email already exists")
    
    new_user = await user_service.create_user(user_data,session)
    return new_user

@auth_router.post('/login')
async def login_users(login_data : UserLoginModel ,session:AsyncSession = Depends(get_session)):
    email=login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email,session)
    if user is not None:
        if verify_password(password,user.password_hash):

            access_token = create_access_token(
                user_data ={
                    'email' : user.email,
                    'user_id' : str(user.uid)
                }
            )

            refresh_token = create_access_token(
                user_data ={
                    'email' : user.email,
                    'user_id' : str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )  

            return JSONResponse(
                content={
                    "message":"Login Succesful",
                    "access_token" : access_token,
                    "refresh_token" : refresh_token,
                    "user" : {
                        "email":user.email,
                        "uid":str(user.uid)
                    }
                }
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid Email or password"
    )
@auth_router.get('/refresh_token')
async def get_new_access_token(token_details:dict = Depends(RefreshTokenBearer())):

    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp)>datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(content={
            "access_token" : new_access_token
        })

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="invalid or expired token")

@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']

    # Add the token's jti to the revoked tokens set
    revoked_tokens.add(jti)
    
    return JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=status.HTTP_200_OK
    )