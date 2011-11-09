import xbmc
import xbmcaddon
from resources.lib.fileops import fileops
from resources.lib import language

__addon__ = xbmcaddon.Addon('script.extrafanartdownloader')
__language__ = language.get_abbrev()

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

    def do_filter(self, art_type, mediatype, artwork, downloaded_artwork):
        if art_type == 'extrafanart':
            return self.extrafanart(mediatype, artwork, downloaded_artwork)
        elif art_type == 'extrathumbs':
            return self.extrathumbs(mediatype, artwork, downloaded_artwork)

    def extrafanart(self, mediatype, artwork, downloaded_artwork):
        limited = False
        reason = ''
        if self.limit_artwork and downloaded_artwork >= self.limit_extrafanart_max:
            reason = 'Max number extrafanart reached: %s' % self.limit_extrafanart_max
            limited = True
        elif self.limit_artwork and 'height' in artwork and (mediatype == 'movie' and artwork['height'] < self.limit_size_moviefanart) or (mediatype == 'tvshow' and artwork['height'] < self.limit_size_tvshowfanart):
            reason = 'Size was to small: %s' % artwork['height'] 
            limited = True
        elif self.limit_artwork and 'rating' in artwork and artwork['rating'] < self.limit_extrafanart_rating:
            reason = 'Rating too low: %s' % artwork['rating']
            limited = True
        elif self.limit_artwork and 'series_name' in artwork and self.limit_notext and artwork['series_name']:
            reason = 'Has text'
            limited = True
        elif self.limit_artwork and self.limit_language and 'language' in artwork and artwork['language'] != __language__:
            reason = "Doesn't match current language: %s" % xbmc.getLanguage()
            limited = True
        return [limited, reason]

    def extrathumbs(self, mediatype, artwork, downloaded_artwork):
        limited = False
        reason = ''
        if downloaded_artwork >= self.limit_extrathumbs_max:
            reason = 'Max number extrathumbs reached: %s' % downloaded_artwork
            limited = True
        elif self.limit_extrathumbs and 'height' in artwork and artwork['height'] < int('169'):
            reason = 'Size was to small: %s' % artwork['height']
            limited = True
        return [limited, reason]
