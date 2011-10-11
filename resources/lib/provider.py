import re
from urllib2 import URLError, urlopen
from utils import _log as log
from script_exceptions import HTTP404Error, DownloadError

class Provider:

    """
    Creates general structure for all fanart providers.  This will allow us to
    very easily add multiple providers for the same media type.
    """

    def __init__(self):
        self.name = ''
        self.api_key = ''
        self.api_limits = False
        self.url = ''
        self.re_pattern = ''
        self.url_prefix = ''
        self.get_filename = lambda url: url.rsplit('/', 1)[1]

    def _get_xml(self, url):
        try:
            client = urlopen(url)
            data = client.read()
            client.close()
            return data
        except URLError, e:
            if e.code == 404:
                raise HTTP404Error(url)
            else:
                raise DownloadError(url)

    def get_image_list(self, media_id):
        log(self.url % (self.api_key, media_id))
        image_list = []
        for i in re.finditer(self.re_pattern, self._get_xml(self.url % (self.api_key, media_id))):
            image_list.append(self.url_prefix + i.group(1))
        return image_list
