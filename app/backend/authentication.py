from keycloak import KeycloakOpenID
from askyourdocs.settings import SETTINGS as settings

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import logging

keycloak_openid = KeycloakOpenID(server_url=settings['app']['keycloak_url'],
                                 realm_name=settings['app']['keycloak_realm'],
                                 client_id=settings['app']['keycloak_client_id'],
                                 client_secret_key=settings['app']['keycloak_client_secret'])

class AuthenticationMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        
        logging.info(f"Request url: {str(request.url)}")
        print(f"Request url: {str(request.url)}")
        
        if request.url.path.startswith('/uploads') | request.url.path.startswith('/app') | request.url.path.startswith('/public') or request.url.path =="/" :
            response = await call_next(request)
            return response

        token = request.headers.get('Authorization')

        if not token:
            return JSONResponse({"error": "Unauthorized"}, 401)
        
        logging.info(f"Received token: {token}")
        print(f"Received token: {token}")
        
        try:
            actual_token = token.split(' ')[1] if 'Bearer' in token else token
            logging.info(f"Actual token used for introspection: {actual_token}")
            print(f"Actual token used for introspection: {actual_token}")
            authorization_info = keycloak_openid.introspect(token)

        except Exception as e:
            logging.error("Error raised from keycloak: ", e)
            return JSONResponse({"error": "Unauthorized"}, 401)

        if authorization_info.get("active") is not True:
            return JSONResponse({"error": "Unauthorized"}, 401)
        
        request.state.userinfo = {
            "id": authorization_info['sub'],
            "name": authorization_info.get("name", None),
            "username": authorization_info['preferred_username'],
            "email": authorization_info.get("email"),
        }
        
        print(authorization_info['sub'])
        print(authorization_info.get("name", None))
        print(authorization_info['preferred_username'])
        print(authorization_info.get("email"))  

        response = await call_next(request)
        return response