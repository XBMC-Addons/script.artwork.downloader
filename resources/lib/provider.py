import re
import xbmc
from urllib2 import URLError, urlopen
from script_exceptions import HTTP404Error, DownloadError

def log(txt, severity=xbmc.LOGDEBUG):
    """Log to txt xbmc.log at specified severity"""
    message = 'script.extrafanartdownloader: %s' % txt
    xbmc.log(msg=message, level=severity)

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



def _setup_providers():
    movie_providers = []
    tv_providers = []
    music_providers = []
    providers = {}

    """
    Setup provider for TheMovieDB.org
    """
    tmdb = Provider()
    tmdb.name = 'TMDB'
    tmdb.api_key = '4be68d7eab1fbd1b6fd8a3b80a65a95e'
    tmdb.api_limits = True
    tmdb.url = "http://api.themoviedb.org/2.1/Movie.imdbLookup/en/xml/%s/%s"
    tmdb.re_pattern = '<image type="backdrop" url="(.*?)" size="original"'
    tmdb.get_filename = lambda url: url.split('backdrops', 1)[1].replace('/', '-').lstrip('-')

    movie_providers.append(tmdb)

    """
    Setup provider for TheTVDB.com
    """
    tvdb = Provider()
    tvdb.name = 'TVDB'
    tvdb.api_key = '1A41A145E2DA0053'
    tvdb.url = 'http://www.thetvdb.com/api/%s/series/%s/banners.xml'
    tvdb.url_prefix = 'http://www.thetvdb.com/banners/'
    tvdb.re_pattern = '<BannerPath>(?P<url>.*?)</BannerPath>\s+<BannerType>fanart</BannerType>'

    tv_providers.append(tvdb)

    """
    Setup provider for fanart.tv - TV API
    """
    ftvt = Provider()
    ftvt.name = 'fanart.tv - TV API'
    ftvt.url = 'http://fanart.tv/api/fanart.php?id=%s&type=tvthumb'
    ftvt.re_pattern = ''

    #tv_providers.append(ftvt)

    """
    Setup provider for fanart.tv - Music API
    """
    ftvm = Provider()
    ftvm.name = 'fanart.tv - Music API'
    ftvm.url = 'http://fanart.tv/api/music.php?id=%s&type=background'
    ftvm.re_pattern = '<background>(.*?)</background>'

    #music_providers.append(ftvm)

    providers['movie_providers'] = movie_providers
    providers['tv_providers'] = tv_providers
    providers['music_providers'] = music_providers

    return providers
