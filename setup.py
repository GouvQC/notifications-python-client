# this restructured text docstring is displayed on https://pypi.org/project/notifications-python-client/
"""
Python API client for PGN - see https://admin.notification.gouv.qc.ca/ for more information.
"""

import ast
import os
import re

from setuptools import find_packages, setup
#from setuptools.command.test import test as TestCommand

# can't just import notifications_python_client.version as requirements may not be installed yet and imports will fail
_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("notifications_python_client/__init__.py", "rb") as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))


# class IntegrationTestCommand(TestCommand):
#     user_options = []
#
#     def initialize_options(self):
#         TestCommand.initialize_options(self)
#         self.pytest_args = ""
#
#     def run_tests(self):
#         import shlex
#         import sys
#
#         import pytest
#
#         errno = pytest.main(shlex.split(self.pytest_args) + ["integration_test/integration_tests.py"])
#         sys.exit(errno)


setup(
    name="notification-python-client",
    version=os.environ.get("PROJECT_VERSION", version),
    url="https://github.com/GouvQC/notifications-python-client",
    license="LiLiQ-Rplus-1.1",
    author="Ministère de la Cybersécurité et du numérique (MCN)",
    description="Python API client for La Plateforme gouvernementale de notification.",
    long_description=__doc__,
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="pgn gouvqc notification",
    packages=find_packages(include=["notifications_python_client"]),
    include_package_data=True,
    # only support actively patched versions of python (https://devguide.python.org/versions/)
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.0.0",
        "PyJWT>=1.5.1",
        "docopt>=0.3.0",
    ],
    # for running pytest as `python setup.py test`, see
    # http://doc.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner
    setup_requires=["pytest-runner"],
)
