#import modules
import xbmc
import xbmcaddon
import os
import xbmcgui
import sys

### get addon info
__addon__       = xbmcaddon.Addon('script.artwork.downloader')
__addonid__     = ( sys.modules[ "__main__" ].__addonid__ )
__addonname__   = ( sys.modules[ "__main__" ].__addonname__ )
__author__      = ( sys.modules[ "__main__" ].__author__ )
__version__     = ( sys.modules[ "__main__" ].__version__ )
__localize__    = ( sys.modules[ "__main__" ].__localize__ )
__addonprofile__= ( sys.modules[ "__main__" ].__addonprofile__ )

#import libraries
from resources.lib.utils import *
from resources.lib import language

### Get settings from settings.xml
class settings:
    ### Initial artwork vars
    def _get_artwork(self):
        self.movie_enable           = __addon__.getSetting("movie_enable")          == 'true'
        self.movie_poster           = __addon__.getSetting("movie_poster")          == 'true'
        self.movie_fanart           = __addon__.getSetting("movie_fanart")          == 'true'
        self.movie_extrafanart      = __addon__.getSetting("movie_extrafanart")     == 'true'
        self.movie_extrathumbs      = __addon__.getSetting("movie_extrathumbs")     == 'true'
        self.movie_logo             = __addon__.getSetting("movie_logo")            == 'true'
        self.movie_clearart         = __addon__.getSetting("movie_clearart")        == 'true'
        self.movie_discart          = __addon__.getSetting("movie_discart")         == 'true'
        self.movie_landscape        = __addon__.getSetting("movie_landscape")       == 'true'
        self.movie_banner           = __addon__.getSetting("movie_banner")          == 'true'
        
        self.tvshow_enable          = __addon__.getSetting("tvshow_enable")         == 'true'
        self.tvshow_poster          = __addon__.getSetting("tvshow_poster")         == 'true'
        self.tvshow_seasonposter    = __addon__.getSetting("tvshow_seasonposter")   == 'true'
        self.tvshow_fanart          = __addon__.getSetting("tvshow_fanart")         == 'true'
        self.tvshow_extrafanart     = __addon__.getSetting("tvshow_extrafanart")    == 'true'
        self.tvshow_clearart        = __addon__.getSetting("tvshow_clearart")       == 'true'
        self.tvshow_logo            = __addon__.getSetting("tvshow_logo")           == 'true'
        self.tvshow_landscape       = __addon__.getSetting("tvshow_landscape")      == 'true'
        self.tvshow_seasonlandscape = __addon__.getSetting("tvshow_seasonlandscape")== 'true'
        self.tvshow_showbanner      = __addon__.getSetting("tvshow_showbanner")     == 'true'
        self.tvshow_seasonbanner    = __addon__.getSetting("tvshow_seasonbanner")   == 'true'
        self.tvshow_characterart    = __addon__.getSetting("tvshow_characterart")   == 'true'

        self.musicvideo_enable      = __addon__.getSetting("musicvideo_enable")     == 'true'
        self.musicvideo_poster      = __addon__.getSetting("musicvideo_poster")     == 'true'
        self.musicvideo_fanart      = __addon__.getSetting("musicvideo_fanart")     == 'true'
        self.musicvideo_extrafanart = __addon__.getSetting("musicvideo_extrafanart")== 'true'
        self.musicvideo_extrathumbs = __addon__.getSetting("musicvideo_extrathumbs")== 'true'
        self.musicvideo_logo        = __addon__.getSetting("musicvideo_logo")       == 'true'
        self.musicvideo_clearart    = __addon__.getSetting("musicvideo_clearart")   == 'true'
        self.musicvideo_discart     = __addon__.getSetting("musicvideo_discart")    == 'true'

    ### Initial genral vars
    def _get_general(self):
        self.centralize_enable      = __addon__.getSetting("centralize_enable")     == 'true'
        self.centralfolder_movies   = __addon__.getSetting("centralfolder_movies")
        self.centralfolder_tvshows  = __addon__.getSetting("centralfolder_tvshows")

    ### Check for faulty setting combinations
    def _check(self):
        settings_faulty = True
        while settings_faulty:
            settings_faulty = True
            check_movie = check_tvshow = check_musicvideo = check_centralize = True
            # re-check settings after posible change
            self._get_general()
            self._get_artwork()
            # Check if faulty setting in movie section
            if self.movie_enable:
                if not self.movie_poster and not self.movie_fanart and not self.movie_extrafanart and not self.movie_extrathumbs and not self.movie_logo and not self.movie_clearart and not self.movie_discart and not self.movie_landscape and not self.movie_banner:
                    check_movie = False
                    log('Setting check: No subsetting of movies enabled')
                else: check_movie = True
            # Check if faulty setting in tvshow section
            if self.tvshow_enable:
                if not self.tvshow_poster and not self.tvshow_seasonposter and not self.tvshow_fanart and not self.tvshow_extrafanart and not self.tvshow_clearart and not self.tvshow_characterart and not self.tvshow_logo and not self.tvshow_showbanner and not self.tvshow_seasonbanner and not self.tvshow_landscape and not self.tvshow_seasonlandscape:
                    check_tvshow = False
                    log('Setting check: No subsetting of tv shows enabled')
                else: check_tvshow = True
            # Check if faulty setting in musicvideo section
            if self.musicvideo_enable:
                if not self.musicvideo_poster and not self.musicvideo_fanart and not self.musicvideo_extrafanart and not self.musicvideo_extrathumbs and not self.musicvideo_logo and not self.musicvideo_clearart and not self.musicvideo_discart:
                    check_musicvideo = False
                    log('Setting check: No subsetting of musicvideo enabled')
                else: check_musicvideo = True
            # Check if faulty setting in centralize section
            if self.centralize_enable:
                if self.centralfolder_movies == '' and self.centralfolder_tvshows == '':
                    check_centralize = False
                    log('Setting check: No centralized folder chosen')
                else: check_centralize = True
            # Compare all setting check
            if check_movie and check_tvshow and check_musicvideo and check_centralize:
                settings_faulty = False
            else: settings_faulty = True
            # Faulty setting found
            if settings_faulty:
                log('Faulty setting combination found')
                # when faulty setting detected ask to open the settings window
                if dialog_msg('yesno', line1 = __localize__(32003), line2 = __localize__(32004), background = False, nolabel = __localize__(32026), yeslabel = __localize__(32025)):
                    __addon__.openSettings()
                # if not cancel the script
                else:
                    xbmc.abortRequested = True
                    break