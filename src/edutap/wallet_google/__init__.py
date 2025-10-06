# import to enable direct usage from parent namespace
# models import registers the models in the registry
from . import models  # noqa: F401

# Exceptions are always available (no optional dependencies)
from .exceptions import ObjectAlreadyExistsException  # noqa: F401
from .exceptions import QuotaExceededException  # noqa: F401
from .exceptions import WalletException  # noqa: F401


# Optional: Import sync API if google-auth is available
try:
    from . import api  # noqa: F401
except ImportError:
    pass

# Optional: Import async API if authlib and httpx are available
try:
    from . import api_async  # noqa: F401
except ImportError:
    pass
