API_PREFIX = '/api/v1'
ROLE_URL = '/api/v1/roles'

REGISTER_URL = f'{API_PREFIX}/auth/register'
LOGIN_URL = f'{API_PREFIX}/auth/login'
REFRESH_URL = f'{API_PREFIX}/auth/refresh'
CHANGE_CREDENTIALS_URL = f'{API_PREFIX}/auth/me/change'

ASSIGN_URL = f'{ROLE_URL}/assign'
REMOVE_URL = f'{ROLE_URL}/remove'

USER_LOGIN_HISTORY_URL = f'{API_PREFIX}/user/login-history'
USER_LOGOUT_URL = f'{API_PREFIX}/user/logout'
