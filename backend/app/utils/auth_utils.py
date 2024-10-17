import logging

import bcrypt

logger = logging.getLogger(__name__)

def get_password_hash(password):
    try:
        salt = bcrypt.gensalt(14)
        hashed = bcrypt.hashpw(password=password.encode(), salt=salt)
        return hashed.decode()
    except Exception as e:
        logger.error(f"Error during get password hash: {e}")
