class Socks5Proxy(object):
    """Socks5 Proxy Plugin for pycurl"""
    def __init__(self, proxy_hostname, proxy_port, proxy_user=None, proxy_passwd=None):
        self._proxy_hostname = proxy_hostname
        self._proxy_port = proxy_port
        self._proxy_user = proxy_user
        self._proxy_passwd = proxy_passwd

    def configure_proxy(self, curl_object):
        """configure pycurl proxy settings"""
        curl_object.setopt(curl_object.PROXY, self._proxy_hostname)
        curl_object.setopt(curl_object.PROXYPORT, self._proxy_port)
        curl_object.setopt(curl_object.PROXYTYPE, curl_object.PROXYTYPE_SOCKS5)
        if self._proxy_user and self._proxy_passwd:
            curl_object.setopt(curl_object.PROXYUSERPWD, '%s:%s' % (self._proxy_user, self._proxy_port)) 
