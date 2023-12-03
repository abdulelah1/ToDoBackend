from app.utils.utils import generate_hash
from app.config.settings import settings
import jwt

ALGORITHM = "HS256"

def generate_jwt_token(user_email: str):

    """

    - In the payload we can add expiry date if we want the token to be expired after some period of time,
    but since this is not a production code, we will not do that.

    - It is better to generate a random key to encrypt the payload, and you have to consider a key rotation policy.

    - Also the key should be saved in a secure environment such as .env file or Vault server.

    :param user_email:
    :return token:
    """

    payload = {"email": user_email}

    token = jwt.encode(payload, settings.ENCRYPTION_KEY, algorithm=settings.ENCRYPTION_ALGO)

    return token


def get_current_user_email(token: str):

    """
    :param token:
    :return user_email:
    """
    payload = jwt.decode(token, settings.ENCRYPTION_KEY, settings.ENCRYPTION_ALGO)
    user_email: str = payload.get("email")

    return user_email