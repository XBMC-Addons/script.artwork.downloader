import re
import urllib2
import utils

class Provider:

    """
    Creates general structure for all fanart providers.  This will allow us to
    very easily add multiple providers for the same media type.
    """

    def __init__(self):
        self.name = ''
        self.api_key = ''
        self.url = ''
        self.re_pattern = ''
        self.url_prefix = ''
        self.get_filename = lambda url: url.rsplit('/', 1)[1]

    def _get_xml(self, url):
        client = urllib2.urlopen(url)
        data = client.read()
        client.close()
        return data

    def get_image_list(self, media_id):
        utils._log(self.url % (self.api_key, media_id))
        image_list = []
        for i in re.finditer(self.re_pattern, self._get_xml(self.url % (self.api_key, media_id))):
            image_list.append(self.url_prefix + i.group(1))
        return image_list
