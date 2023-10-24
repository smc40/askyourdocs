from keycloak import KeycloakOpenID
from askyourdocs.settings import SETTINGS as settings

import logging

keycloak_openid = KeycloakOpenID(server_url=settings['app']['keycloak_url'],
                                 realm_name=settings['app']['keycloak_realm'],
                                 client_id=settings['app']['keycloak_client_id'],
                                 client_secret_key=settings['app']['keycloak_client_secret'])


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
    }
