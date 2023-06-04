import jwt, sys
from flask import request
from functools import wraps
from app import app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #if "Authorization" in request.headers:
        if "X-Auth-Key" in request.headers:
            token = request.headers["X-Auth-Key"]#.split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            user_data=jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"], options={"require": ["user_id", "user_role", "iat", "exp"]})
            if user_data["user_id"] is None or user_data["user_role"] is None :
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except jwt.ExpiredSignatureError as error:
            return {
                "message": "Token is expired",
                "data": None,
                "error": "Session Expired"
            }, 401

        except jwt.exceptions.InvalidTokenError as error:
                return {
                "message": "Invalid Token",
                "data": None,
                "error": "Invalid Token"
            }, 401
        except jwt.exceptions.InvalidSignatureError:
                return {
                "message": "Invalid Token Signature",
                "data": None,
                "error": "Invalid Token Signature"
            }, 401
        except Exception as e:
            print(f"Error occured while Decoding Data {e}", file=sys.stderr)
            return {
                "message": "Internal Server Error",
                "data": None,
                "error": str(e)
            }, 500
        
        return f(user_data, *args, **kwargs)

    return decorated