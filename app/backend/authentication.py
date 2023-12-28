from keycloak import KeycloakOpenID
from askyourdocs.settings import SETTINGS as settings

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import logging

keycloak_openid = KeycloakOpenID(server_url="http://thunder.local:8080",
                                 realm_name="ayd",
                                 client_id="ayd-backend",
                                 client_secret_key="bQwuuesYTIfcJmOxI4t4fltV48OQsAQq")

class AuthenticationMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith('/uploads') | request.url.path.startswith('/app'):
            response = await call_next(request)
            return response

        logging.error("Request Path")
        logging.error(request.url.path)
        
        
        logging.error("request")
        logging.error(request)

        token = request.headers.get('Authorization')
        logging.error("token")
        logging.error(token)

        if not token:
            return JSONResponse({"error": "Unauthorized"}, 401)
        
        try:
            authorization_info = keycloak_openid.introspect(token)

            logging.error("authorization_info")
            logging.error(authorization_info)


            logging.error("KeycloakOpenID Settings:")
            logging.error(f"Client ID: {keycloak_openid.client_id}")
            logging.error(f"Realm Name: {keycloak_openid.realm_name}")
            logging.error(f"Client Secret Key: {keycloak_openid.client_secret_key}")
            logging.error(f"connection: {keycloak_openid.connection}")
            logging.error(f"authorization: {keycloak_openid.authorization}")
            # logging.error(f"authorization: {keycloak_openid.}")

            logging.error(settings['app']['keycloak_url'])

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

        response = await call_next(request)
        return response