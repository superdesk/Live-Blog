
SERVER_URL = "https://master.lb-test.sourcefabric.org/resources/"
DEFAULT_BLOG = 1

ADMIN_LOGIN = "admin"
ADMIN_PASS = "a"

PRINT_PAYLOAD = False
PRINT_URL = False
PRINT_HEADERS = False

try:
    from settings_local import *
except Exception:
    pass
