from urlparse import urlparse

import pycurl

class Socks5Proxy(object):
    """Socks5 Proxy Plugin for pycurl
    proxy_url format socks5://username:passwd@hostname:port"""
    def __init__(self, proxy_url):
        parsed_url = urlparse(proxy_url)
        self._proxy_hostname = parsed_url.hostname
        self._proxy_port = parsed_url.port
        self._proxy_user = parsed_url.username
        self._proxy_passwd = parsed_url.password

    def configure_proxy(self):
        """configure pycurl proxy settings"""
        configuration = {pycurl.PROXY: self._proxy_hostname,
                         pycurl.PROXYPORT: self._proxy_port,
                         pycurl.PROXYTYPE: pycurl.PROXYTYPE_SOCKS5}

        if self._proxy_user and self._proxy_passwd:
            configuration[pycurl.PROXYUSERPWD] = '%s:%s' % (self._proxy_user, self._proxy_port)

        return configuration
