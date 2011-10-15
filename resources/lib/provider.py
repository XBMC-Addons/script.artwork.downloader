import socket
import os
import sys
import xbmc
import xbmcaddon
from urllib2 import URLError, urlopen
from utils import get_short_language
from script_exceptions import HTTP404Error, HTTP503Error, DownloadError, NoFanartError

__addon__ = xbmcaddon.Addon('script.extrafanartdownloader')

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources'))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))

import ElementTree as ET

### adjust default timeout to stop script hanging
timeout = 20
socket.setdefaulttimeout(timeout)

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
        self.data = {}
        self.re_pattern = ''
        self.fanart_element = ''
        self.fanart_root = ''
        self.url_prefix = ''
        self.get_filename = lambda url: url.rsplit('/', 1)[1]

    def _get_xml(self, url):
        try:
            print url
            client = urlopen(url)
            data = client.read()
            client.close()
            return data
        except URLError, e:
            try:
                if e.code == 404:
                    raise HTTP404Error(url)
                if e.code == 503:
                    raise HTTP503Error(url)
                else:
                    raise DownloadError(url)
            except:
                raise DownloadError(url)

    def get_image_list(self, media_id):
        pass


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
    tmdb.url = "http://api.themoviedb.org/2.1/Movie.imdbLookup/" + get_short_language() + "/xml/%s/%s"
    tmdb.xml_root = 'movies'
    tmdb.get_filename = lambda url: url.split('backdrops', 1)[1].replace('/', '-').lstrip('-')
    
    def _temp(media_id):
        log('API: %s ' % tmdb.url % (tmdb.api_key, media_id))
        image_list = []
        data = tmdb._get_xml(tmdb.url % (tmdb.api_key, media_id))
        tree = ET.fromstring(data)
        tree = tree.findall('movies')[0]
        tree = tree.findall('movie')[0]
        tree = tree.findall('images')[0]
        for image in tree.findall('image'):
            info = {}
            if image.get('type') == 'backdrop' and image.get('size') == 'original' and image.get('url'):
                info['url'] = image.get('url')
                info['height'] = int(image.get('height'))
                info['width'] = int(image.get('width'))
            if info:            
                image_list.append(info) 
        if image_list == []:
            raise NoFanartError(media_id)
        else:
            return image_list 
    
    tmdb.get_image_list = _temp

    movie_providers.append(tmdb)

    """
    Setup provider for TheTVDB.com
    """
    tvdb = Provider()
    tvdb.name = 'TVDB'
    tvdb.api_key = '1A41A145E2DA0053'
    tvdb.url = 'http://www.thetvdb.com/api/%s/series/%s/banners.xml'
    tvdb.url_prefix = 'http://www.thetvdb.com/banners/'
    tvdb.xml_root = 'Banner'
    
    def _temp2(media_id):
        log('API: %s ' % tvdb.url % (tvdb.api_key, media_id))
        image_list = []
        data = tvdb._get_xml(tvdb.url % (tvdb.api_key, media_id))
        tree = ET.fromstring(data)
        for image in tree.findall(tvdb.xml_root):
            info = {}
            if image.findtext('BannerType') == 'fanart' and image.findtext('BannerPath'):
                info['url'] = tvdb.url_prefix + image.findtext('BannerPath')
                info['language'] = image.findtext('Language')
                if image.findtext('BannerType2'):
                    x,y = image.findtext('BannerType2').split('x')
                    info['height'] = int(x)
                    info['width'] = int(y)
                info['series_name'] = image.findtext('SeriesName') == 'true'
                if image.findtext('RatingCount') and int(image.findtext('RatingCount')) >= 1:
                    info['rating'] = float(image.findtext('Rating'))
                else:
                    info['rating'] = 0
            if info:            
                image_list.append(info) 
        if image_list == []:
            raise NoFanartError(media_id)
        else:
            return image_list   
    
    tvdb.get_image_list = _temp2

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
