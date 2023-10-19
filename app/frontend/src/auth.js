import Keycloak from 'keycloak-js';

const _kc = new Keycloak('./keycloak.json');

const initAuth = (onAuthenticatedCallback) => {
    _kc.init({ onLoad: 'login-required', checkLoginIframe: false }).then(
        (authenticated) => {
            if (authenticated) {
                onAuthenticatedCallback();
            } else {
                doLogin();
            }
        }
    );
};

const doLogin = _kc.login;

const doLogout = _kc.logout;

const getToken = () => _kc.token;

const updateToken = (successCallback) => {
    return _kc.updateToken(5).then(successCallback).catch(doLogin);
};

const getUsername = () => _kc.tokenParsed.preferred_username;

const getGivenName = () => _kc.tokenParsed.given_name;

const getUserEmail = () => _kc.tokenParsed.email;

const isAuthenticated = () => _kc.authenticated;

const isAdmin = () => _kc.hasRealmRole('admin');

const isSupervisor = () => _kc.hasRealmRole('supervisor') || isAdmin();

const isUser = () => _kc.hasRealmRole('user') || isSupervisor();

export default {
    initAuth,
    doLogin,
    doLogout,
    getToken,
    updateToken,
    getUsername,
    getGivenName,
    getUserEmail,
    isAuthenticated,
    isAdmin,
    isSupervisor,
    isUser,
};
