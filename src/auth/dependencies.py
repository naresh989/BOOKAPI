import logging
from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
# from src.db.redis import token_in_blocklist

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)  
logger = logging.getLogger(__name__)
revoked_tokens = set()
# TokenBearer class with added logging
class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        
        logger.debug(f"Token received: {token}")

        token_data = decode_token(token)
        logger.debug(f"Decoded token data: {token_data}")

        if not self.token_valid(token):
            logger.error(f"Invalid or expired token: {token}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token"
                }
            )

        logger.debug(f"Token is valid, verifying token data")
        
        if token_data and token_data['jti'] in revoked_tokens:
            logger.error("Token has been revoked")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token has been revoked",
                    "resolution": "Please login again to obtain a new token"
                }
            )
        
        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        logger.debug(f"Validating token: {token}")
        token_data = decode_token(token)
    
        if token_data:
            logger.debug(f"Token is valid: {token_data}")
            return True
        else:
            logger.error(f"Token is invalid or could not be decoded: {token}")
            return False


    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes")

class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:
        logger.debug(f"Verifying access token: {token_data}")
        if token_data and token_data.get("refresh"):
            logger.error("Access token cannot be a refresh token")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )
        logger.debug("Access token verification passed")


# RefreshTokenBearer class with added logging
class RefreshTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:
        logger.debug(f"Verifying refresh token: {token_data}")
        if token_data and not token_data.get("refresh"):
            logger.error("Refresh token is required, but access token provided")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )
        logger.debug("Refresh token verification passed")
