# Version numbering follows Semantic Versionning:
#
# Given a version number MAJOR.MINOR.PATCH, increment the:
# - MAJOR version when you make incompatible API changes,
# - MINOR version when you add functionality in a backwards-compatible manner, and
# - PATCH version when you make backwards-compatible bug fixes.
#
# -- http://semver.org/

__version__ = "0.0.0+pre.local"

from notifications_python_client.errors import (  # noqa
    REQUEST_ERROR_MESSAGE,
    REQUEST_ERROR_STATUS_CODE,
)
from notifications_python_client.notifications import NotificationsAPIClient  # noqa
