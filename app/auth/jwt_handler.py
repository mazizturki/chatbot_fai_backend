import jwt
import uuid 
import datetime

SECRET_KEY = 'vBlqpm0aTLskf0UtDGqCgFJXH3NUrSzOvwGtTbgLphq9AZ'  
ALGORITHM = 'HS256'  

def create_jwt_token():
    """
    Create a JWT token with a unique identifier and expiration time.
    
    Returns:
        str: The encoded JWT token.
    """
    session_id = str(uuid.uuid4())
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    
    payload = {
        'jti': session_id,  # JWT ID (unique identifier for the token)
        'iat': datetime.datetime.utcnow(),  # Issued at time
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload["jti"])  # récupère l'id unique
        return payload  
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")