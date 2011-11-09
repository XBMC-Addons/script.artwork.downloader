import xbmc
import xbmcaddon
from resources.lib.fileops import fileops
from resources.lib import utils

__addon__ = xbmcaddon.Addon('script.extrafanartdownloader')

log = utils._log

class apply_filters:

    def __init__(self):
        self.limit_artwork = __addon__.getSetting("limit_artwork") == 'true'
        self.limit_extrafanart_max = int(__addon__.getSetting("limit_extrafanart_max").rstrip('0').rstrip('.'))
        self.limit_extrafanart_rating = int(__addon__.getSetting("limit_extrafanart_rating").rstrip('0').rstrip('.'))
        self.limit_size_moviefanart = int(__addon__.getSetting("limit_size_moviefanart"))
        self.limit_size_tvshowfanart = int(__addon__.getSetting("limit_size_tvshowfanart"))
        self.limit_extrathumbs = self.limit_artwork
        self.limit_extrathumbs_max = 4
        self.limit_language = __addon__.getSetting("limit_language") == 'true'
        self.limit_notext = __addon__.getSetting("limit_notext") == 'true'

    def do_filter(self, art_type, artwork, downloaded_artwork):
        if art_type == 'fanart':
            return self.fanart(artwork, downloaded_artwork)
        elif art_type == 'extrathumbs':
            return self.extrathumbs(artwork, downloaded_artwork)

    def fanart(self, fanart, downloaded_artwork):
        limited = False
        if self.limit_artwork and downloaded_artwork >= self.limit_extrafanart_max:
            reason = 'Max number fanart reached: %s' % self.limit_extrafanart_max
            limited = True
        elif self.limit_artwork and 'height' in fanart and (self.mediatype == 'movie' and fanart['height'] < self.limit_size_moviefanart) or (self.mediatype == 'tvshow' and fanart['height'] < self.limit_size_tvshowfanart):
            reason = 'Size was to small: %s' % fanart['height'] 
            limited = True
        elif self.limit_artwork and 'rating' in fanart and fanart['rating'] < self.limit_extrafanart_rating:
            reason = 'Rating too low: %s' % fanart['rating']
            limited = True
        elif self.limit_artwork and 'series_name' in fanart and self.limit_notext and fanart['series_name']:
            reason = 'Has text'
            limited = True
        elif self.limit_artwork and self.limit_language and 'language' in fanart and fanart['language'] != __language__:
            reason = "Doesn't match current language: %s" % xbmc.getLanguage()
            limited = True
        return [limited, reason]

    def extrathumbs(self, extrathumbs, downloaded_artwork):
        limited = False
        if downloaded_artwork >= self.limit_extrathumbs_max:
            reason = 'Max number extrathumbs reached: %s' % self.downloaded_artwork
            limited = True
        elif self.limit_extrathumbs and 'height' in extrathumbs and extrathumbs['height'] < int('169'):
            reason = 'Size was to small: %s' % extrathumbs['height']
            limited = True
        return [limited, reason]
