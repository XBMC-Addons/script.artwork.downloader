import xbmc
import xbmcaddon
import os
from resources.lib.utils import _log as log
from resources.lib import language
from resources.lib.utils import _dialog as dialog
### get addon info
__addon__ = xbmcaddon.Addon('script.extrafanartdownloader')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__localize__ = __addon__.getLocalizedString
__language__ = language.get_abbrev()

addondir = xbmc.translatePath( __addon__.getAddonInfo('profile') )
settings_file = os.path.join(addondir, "settings.xml")


class _settings:

    ### Get settings from settings.xml
    def _get(self):
        self.movie_enable = __addon__.getSetting("movie_enable") == 'true'
        self.movie_poster = __addon__.getSetting("movie_poster") == 'true'
        self.movie_fanart = __addon__.getSetting("movie_fanart") == 'true'
        self.movie_extrafanart = __addon__.getSetting("movie_extrafanart") == 'true'
        self.movie_extrathumbs = __addon__.getSetting("movie_extrathumbs") == 'true'
        self.movie_logo = __addon__.getSetting("movie_logo") == 'true'
        self.movie_discart = __addon__.getSetting("movie_discart") == 'true'
        
        self.tvshow_enable = __addon__.getSetting("tvshow_enable") == 'true'
        self.tvshow_poster = __addon__.getSetting("tvshow_poster") == 'true'
        self.tvshow_fanart = __addon__.getSetting("tvshow_fanart") == 'true'
        self.tvshow_extrafanart = __addon__.getSetting("tvshow_extrafanart") == 'true'
        self.tvshow_clearart = __addon__.getSetting("tvshow_clearart") == 'true'
        self.tvshow_logo = __addon__.getSetting("tvshow_logo") == 'true'
        self.tvshow_thumb = __addon__.getSetting("tvshow_thumb") == 'true'
        self.tvshow_seasonthumbs = __addon__.getSetting("tvshow_seasonthumbs") == 'true'
        self.tvshow_showbanner = __addon__.getSetting("tvshow_showbanner") == 'true'
        self.tvshow_seasonbanner = __addon__.getSetting("tvshow_seasonbanner") == 'true'
        self.tvshow_characterart = __addon__.getSetting("tvshow_characterart") == 'true'
     
        self.centralize_enable = __addon__.getSetting("centralize_enable") == 'true'
        self.centralfolder_split = __addon__.getSetting("centralfolder_split")
        self.centralfolder_movies = __addon__.getSetting("centralfolder_movies")
        self.centralfolder_tvshows = __addon__.getSetting("centralfolder_tvshows")

        self.limit_artwork = __addon__.getSetting("limit_artwork") == 'true'
        self.limit_extrafanart_max = int(__addon__.getSetting("limit_extrafanart_max").rstrip('0').rstrip('.'))
        self.limit_extrafanart_rating = int(__addon__.getSetting("limit_extrafanart_rating").rstrip('0').rstrip('.'))
        self.limit_size_moviefanart = int(__addon__.getSetting("limit_size_moviefanart"))
        self.limit_size_tvshowfanart = int(__addon__.getSetting("limit_size_tvshowfanart"))
        self.limit_extrathumbs = self.limit_artwork
        self.limit_extrathumbs_max = 4
        self.limit_language = __addon__.getSetting("limit_language") == 'true'
        self.limit_notext = __addon__.getSetting("limit_notext") == 'true'

        self.use_cache = __addon__.getSetting("use_cache") == 'true'
        self.cache_directory = __addon__.getSetting("cache_directory")
        self.background = __addon__.getSetting("background") == 'true'
        self.notify = __addon__.getSetting("notify") == 'true'

    ### Initial startup vars
    def _vars(self):
        self.failcount = 0
        self.failthreshold = 3
        self.xmlfailthreshold = 5
        self.limit_artwork_max = 1
        self.mediatype = ''
        self.medianame = ''
        self.count_tvshow_extrafanart = 0
        self.count_movie_extrafanart = 0
        self.count_movie_extrathumbs = 0
        self.artworkfile_poster = 'poster.jpg'
        self.artworkfile_fanart = 'fanart.jpg'
        self.artworkfile_banner = 'banner.jpg'
        self.artworkfile_logo = 'logo.png'
        self.artworkfile_clearart = 'clearart.png'
        self.artworkfile_tvthumb = 'landscape.jpg'
        self.artworkfile_seasonthumbs = 'seasonthumbxx.jpg'
        self.artworkfile_characterart = 'character.png'

    ### Log settings in debug mode
    def _initiallog(self):
        log("## Settings...")
        log('## Language Used = %s' % str(__language__))
        log('## Background Run = %s' % str(self.background))
        log('## - Notify when finished/error = %s' % str(self.notify))
        
        log('## Download Movie Artwork= %s' % str(self.movie_enable))
        log('## - Movie Poster= %s' % str(self.movie_poster))
        log('## - Movie Fanart= %s' % str(self.movie_fanart))
        log('## - Movie ExtraFanart= %s' % str(self.movie_extrafanart))
        log('## - Movie ExtraThumbs= %s' % str(self.movie_extrathumbs))
        log('## - Movie Logo= %s' % str(self.movie_logo))
        log('## - Movie DiscArt= %s' % str(self.movie_discart))
        
        log('## Download TV Show Artwork = %s' % str(self.tvshow_enable))
        log('## - TV Show Poster = %s' % str(self.tvshow_poster))
        log('## - TV Show Fanart = %s' % str(self.tvshow_fanart))
        log('## - TV Show ExtraFanart = %s' % str(self.tvshow_extrafanart))
        log('## - TV Show Clearart = %s' % str(self.tvshow_clearart))
        log('## - TV Show Logo = %s' % str(self.tvshow_logo))
        log('## - TV Show Showbanner = %s' % str(self.tvshow_showbanner))
        log('## - TV Show Seasonbanner = %s' % str(self.tvshow_seasonbanner))
        log('## - TV Show Thumb = %s' % str(self.tvshow_thumb))
        log('## - TV Show Seasonthumbs = %s' % str(self.tvshow_seasonthumbs))
        log('## - TV Show Characterart = %s' % str(self.tvshow_characterart))
        
        log('## Centralize Extrafanart = %s' % str(self.centralize_enable))
        log('## Central Movies Folder = %s' % str(self.centralfolder_movies))
        log('## Central TV Shows Folder = %s' % str(self.centralfolder_tvshows))
        
        log('## Limit Artwork = %s' % str(self.limit_artwork))
        log('## - Extrafanart Max = %s' % str(self.limit_extrafanart_max))
        log('## - Fanart Rating = %s' % str(self.limit_extrafanart_rating))
        log('## - Movie Fanart Size = %s' % str(self.limit_size_moviefanart))
        log('## - TV Show Fanart Size = %s' % str(self.limit_size_tvshowfanart))
        log('## - Extrathumbs = %s' % str(self.limit_extrathumbs))
        log('## - Extrathumbs Max = %s' % str(self.limit_extrathumbs_max))
        log('## - Language = %s' % str(self.limit_language))
        log('## - Fanart with no text = %s' % str(self.limit_notext))
        
        log('## Backup downloaded fanart= %s' % str(self.use_cache))
        log('## Backup folder = %s' % str(self.cache_directory))
        log("## End of Settings...")

    ### Check if settings.xml exist and version check
    def _exist(self):
        first_run = True
        while first_run:
            # no settings.xml found
            if not os.path.isfile(settings_file):
                dialog('okdialog', line1 = __localize__(36037), line2 = __localize__(36038))
                log('## Settings.xml file not found. Opening settings window.')
                __addon__.openSettings()
                __addon__.setSetting(id="addon_version", value=__addonversion__)
            # different version settings.xml found
            if os.path.isfile(settings_file) and __addon__.getSetting("addon_version") <> __addonversion__:
                dialog('okdialog', line1 = __localize__(36003), line2 = __localize__(36038))
                log('## Addon version is different. Opening settings window.')
                __addon__.openSettings()
                __addon__.setSetting(id="addon_version", value=__addonversion__)
            else:
                first_run = False
        __addon__.setSetting(id="addon_version", value=__addonversion__)
        log('## Correct version of settings.xml file found. Continue with initializing.')
        
    ### Check for faulty setting combinations
    def _check(self):    
        settings_faulty = True
        check_sections = check_movie = check_tvshow = check_centralize = check_cache = True
        while settings_faulty:
            # re-check settings after posible change
            self._get()        
            # Check if artwork section enabled
            if not (self.movie_enable or self.tvshow_enable):
                check_sections = False
                log('Setting check: No artwork section enabled')
            else: check_sections = True
            # Check if faulty setting in movie section
            if self.movie_enable:
                if not self.movie_fanart and not self.movie_extrafanart and not self.movie_extrathumbs and not self.movie_poster:
                    check_movie = False
                    log('Setting check: No subsetting of movies enabled')
                else: check_movie = True
            # Check if faulty setting in tvshow section
            if self.tvshow_enable:
                if not self.tvshow_poster and not self.tvshow_fanart and not self.tvshow_extrafanart  and not self.tvshow_showbanner and not self.tvshow_clearart and not self.tvshow_logo and not self.tvshow_showbanner and not self.tvshow_seasonbanner and not self.tvshow_thumb and not self.tvshow_seasonthumbs and not self.tvshow_characterart:
                    check_tvshow = False
                    log('Setting check: No subsetting of tv shows enabled')
                else: check_tvshow = True
            # Check if faulty setting in centralize section
            if self.centralize_enable:
                if self.centralfolder_movies == '' and self.centralfolder_tvshows == '':
                    check_centralize = False
                    log('Setting check: No centralized folder chosen')
                else: check_centralize = True
            # Check if faulty setting in cache section
            if self.use_cache:
                if self.cache_directory == '':
                    check_cache = False
                    log('Setting check: No cache folder chosen')
                else: check_cache = True
            # Compare all setting check
            if check_sections and check_movie and check_tvshow and check_centralize and check_cache:
                settings_faulty = False
            else: settings_faulty = True
            # Faulty setting found
            if settings_faulty:
                log('Faulty setting combination found')
                dialog('okdialog', line1 = __localize__(36020), line2 = __localize__(36019))
                __addon__.openSettings()        