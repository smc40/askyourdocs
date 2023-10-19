from keycloak import KeycloakOpenID
import logging

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    tika_url: str = "http://127.0.0.1:9998" 
    translation_url: str = "http://127.0.0.1:5000"
    
    keycloak_url: str = "http://localhost:8080/auth/"
    keycloak_realm: str = "ayd"
    keycloak_client_id: str = "ayd-backend"
    keycloak_client_secret: str = "1Rsg18pXc2UXOWqXM9D5EwOejglFmOO6"

settings = Settings()
keycloak_openid = KeycloakOpenID(server_url=settings.keycloak_url,
                                 realm_name=settings.keycloak_realm,
                                 client_id=settings.keycloak_client_id,
                                 client_secret_key=settings.keycloak_client_secret)


def get_user_info(token):
    if token is None:
        return None

    try:
        # check if the token is valid & user is active
        authorization_info = keycloak_openid.introspect(token)
    except Exception as e:
        logging.error("Error raised from keycloak: ", e)
        return None

    if authorization_info.get("active") is not True:
        return None

    return {
        "id": authorization_info['sub'],
        "name": authorization_info.get("name", None),
        "username": authorization_info['preferred_username'],
        "email": authorization_info['email'],
        "roles": authorization_info['realm_access']['roles'],
    }