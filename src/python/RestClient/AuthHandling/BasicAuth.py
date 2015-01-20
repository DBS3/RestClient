from getpass import getpass
from RestClient.ErrorHandling.RestClientExceptions import ClientAuthException

import pycurl
import sys

class BasicAuth(object):
    def __init__(self, username=None, password=None):
        self._username = username
        self._password = password

        if sys.stdin.isatty() and not self._username:
            self._username = raw_input('User:')

        if sys.stdin.isatty() and not self._password:
            self._password = getpass("Password:")

        if not (self._username and self._password):
            raise ClientAuthException("No valid user or password specified for BasicAuth")

    def configure_auth(self):
        return {pycurl.HTTPAUTH: pycurl.HTTPAUTH_BASIC,
                pycurl.USERPWD: "%s:%s" % self.userpwd}

    @property
    def userpwd(self):
        return self._username, self._password
