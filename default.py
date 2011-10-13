import re
import os
import time
import sys
import xbmc
import xbmcaddon
import xbmcgui
import platform

### get addon info
__addon__ = xbmcaddon.Addon('script.extrafanartdownloader')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__localize__ = __addon__.getLocalizedString

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources'))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))


import media_setup

__python_version__ = platform.python_version_tuple()
if (int(__python_version__[0]) == 2 and int(__python_version__[1]) > 4):
    __xbmc_version__ = 'Eden'
    Media_listing = media_setup.eden_media_listing
else:
    __xbmc_version__ = 'Dharma'
    Media_listing = media_setup.dharma_media_listing

from provider import _setup_providers
from utils import _log as log
from utils import fileops, get_short_language
from script_exceptions import DownloadError, CreateDirectoryError, HTTP404Error, HTTP503Error, NoFanartError

__language__ = get_short_language()


class Main:
    def __init__(self):
        if self.initialise():
            if not self.mediatype == '':
                if not self.medianame == '':
                    self.solo_mode(self.mediatype, self.medianame)
                else:
                    if self.mediatype == 'tvshow':
                        self.Medialist = Media_listing('TVShows')
                        self.download_fanart(self.Medialist, self.tv_providers)
                    elif self.mediatype == 'movie':
                        self.Medialist = Media_listing('Movies')
                        self.download_fanart(self.Medialist, self.movie_providers)
                    elif self.mediatype == 'artist':
                        log('Music fanart not yet implemented', xbmc.LOGNOTICE)
            else:
                if self.tvfanart:
                    self.Medialist = Media_listing('TVShows')
                    self.mediatype = 'tvshow'
                    self.download_fanart(self.Medialist, self.tv_providers)
                else:
                    log('TV fanart disabled, skipping', xbmc.LOGINFO)
                if self.moviefanart:
                    self.Medialist = Media_listing('Movies')
                    self.mediatype = 'movie'
                    self.download_fanart(self.Medialist, self.movie_providers)
                else:
                    log('Movie fanart disabled, skipping', xbmc.LOGINFO)
        else:
            log('Initialisation error, script aborting', xbmc.LOGERROR)
        self.cleanup()


    ### load settings and initialise needed directories
    def initialise(self):
        providers = _setup_providers()
        self.movie_providers = providers['movie_providers']
        self.tv_providers = providers['tv_providers']
        self.music_providers = providers['music_providers']
        self.failcount = 0
        self.failthreshold = 3
        self.fanart_centralized = 0
        self.moviefanart = __addon__.getSetting("moviefanart") == 'true'
        self.tvfanart = __addon__.getSetting("tvfanart") == 'true'
        self.centralize = __addon__.getSetting("centralize") == 'true'
        self.central_movies = __addon__.getSetting("central_movies")
        self.central_tv = __addon__.getSetting("central_tv")
        self.limit_extrafanart = __addon__.getSetting("limit_extrafanart") == 'true'
        self.limit_extrafanart_max = int(__addon__.getSetting("limit_extrafanart_max").rstrip('0').rstrip('.'))
        self.limit_extrafanart_rating = int(__addon__.getSetting("limit_extrafanart_rating").rstrip('0').rstrip('.'))
        self.limit_language = __addon__.getSetting("limit_language") == 'true'
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create(__addonname__, __localize__(36003))
        self.mediatype = ''
        self.medianame = ''

        # Print out settings to log to help with debugging
        log('Setting: __addonid__ = %s' % str(__addonid__))
        log('Setting: __addonname__ = %s' % str(__addonname__))
        log('Setting: __addonversion__ = %s' % str(__addonversion__))
        log('Setting: __language__ = %s' % str(__language__))
        log('Setting: moviefanart = %s' % str(self.moviefanart))
        log('Setting: tvfanart = %s' % str(self.tvfanart))
        log('Setting: centralize = %s' % str(self.centralize))
        log('Setting: central_movies = %s' % str(self.central_movies))
        log('Setting: central_tv = %s' % str(self.central_tv))
        log('Setting: limit_extrafanart = %s' % str(self.limit_extrafanart))
        log('Setting: limit_extrafanart_max = %s' % str(self.limit_extrafanart_max))
        log('Setting: limit_extrafanart_rating = %s' % str(self.limit_extrafanart_rating))
        log('Setting: limit_language = %s' % str(self.limit_language))


        for item in sys.argv:
            match = re.search("mediatype=(.*)" , item)
            if match:
                self.mediatype = match.group(1)
                if self.mediatype == 'tvshow' or self.mediatype == 'movie' or self.mediatype == 'artist':
                    pass
                else:
                    log('Error: invalid mediatype, must be one of movie, tvshow or artist', xbmc.LOGERROR)
                    return False
            else:
                pass
            match = re.search("medianame=" , item)
            if match:
                self.medianame = item.replace("medianame=" , "")
            else:
                pass
        try:
            self.fileops = fileops()
        except CreateDirectoryError, e:
            log("Could not create directory: %s" % str(e))
            return False
        else:
            return True


    ### clean up and
    def cleanup(self):
        if self.fileops._exists(self.fileops.tempdir):
            self.dialog.update(100, __localize__(36004))
            log('Cleaning up')
            for x in os.listdir(self.fileops.tempdir):
                tempfile = os.path.join(self.fileops.tempdir, x)
                self.fileops._delete(tempfile)
                if self.fileops._exists(tempfile):
                    log('Error deleting temp file: %s' % tempfile, xbmc.LOGERROR)
            self.fileops._rmdir(self.fileops.tempdir)
            if self.fileops._exists(self.fileops.tempdir):
                log('Error deleting temp directory: %s' % self.fileops.tempdir, xbmc.LOGERROR)
            else:
                log('Deleted temp directory: %s' % self.fileops.tempdir, xbmc.LOGNOTICE)
        ### log results and notify user
        log('Finished: %s extrafanart downloaded' % self.fileops.downloadcount, xbmc.LOGNOTICE)
        summary_tmp = __localize__(36009) + ': %s ' % self.fileops.downloadcount
        summary = summary_tmp + __localize__(36010)
        self.dialog.close()
        if not self.failcount < self.failthreshold:
            xbmcgui.Dialog().ok(__addonname__, __localize__(36007), __localize__(36008))
        xbmcgui.Dialog().ok(__addonname__, summary)

    ### solo mode
    def solo_mode(self, itemtype, itemname):
        if itemtype == 'movie':
            self.Medialist = Media_listing('Movies')
        elif itemtype == 'tvshow':
            self.Medialist = Media_listing('TVShows')
        else:
            log("Error: type must be one of 'movie' or 'tvshow', aborting", xbmc.LOGERROR)
            return False
        log('Retrieving fanart for: %s' % itemname)
        for currentitem in self.Medialist:
            if itemname == currentitem["name"]:
                if itemtype == 'movie':
                    self.Medialist = []
                    self.Medialist.append(currentitem)
                    self.download_fanart(self.Medialist, self.movie_providers)
                if itemtype == 'tvshow':
                    self.Medialist = []
                    self.Medialist.append(currentitem)
                    self.download_fanart(self.Medialist, self.tv_providers)
                break

    ### download media fanart
    def download_fanart(self, media_list, providers):
        self.processeditems = 0
        for currentmedia in media_list:
            ### check if XBMC is shutting down
            if xbmc.abortRequested == True:
                log('XBMC shutting down, aborting')
                break
            ### check if script has been cancelled by user
            if self.dialog.iscanceled():
                break
            if not self.failcount < self.failthreshold:
                break
            try:
                self.media_path = os.path.split(currentmedia["path"])[0].rsplit(' , ', 1)[1]
            except:
                self.media_path = os.path.split(currentmedia["path"])[0]
            self.media_id = currentmedia["id"]
            self.media_name = currentmedia["name"]
            self.dialog.update(int(float(self.processeditems) / float(len(media_list)) * 100.0), __localize__(36005), self.media_name, '')
            log('Processing media: %s' % self.media_name, xbmc.LOGNOTICE)
            log('ID: %s' % self.media_id)
            log('Path: %s' % self.media_path)
            targetdirs = []
            extrafanart_dir = os.path.join(self.media_path, 'extrafanart')
            targetdirs.append(extrafanart_dir)
            if self.centralize:
                if self.mediatype == 'tvshow':
                    if not self.central_tv == '':
                        targetdirs.append(self.central_tv)
                    else:
                        log('Error: Central fanart enabled but directory not set, skipping', xbmc.LOGERROR)
                elif self.mediatype == 'movie':
                    if not self.central_movies == '':
                        targetdirs.append(self.central_movies)
                    else:
                        log('Error: Central fanart enabled but directory not set, skipping', xbmc.LOGERROR)
            if self.media_id == '':
                log('%s: No ID found, skipping' % self.media_name, xbmc.LOGNOTICE)
            elif self.mediatype == 'tvshow' and self.media_id.startswith('tt'):
                log('%s: IMDB ID found for TV show, skipping' % self.media_name, xbmc.LOGNOTICE)
            else:
                for provider in providers:
                    got_image_list = False
                    try:
                        backdrops = provider.get_image_list(self.media_id)
                    except HTTP404Error, e:
                        log('Error getting data from %s (404: File not found), skipping' % provider.name, xbmc.LOGERROR)
                    except HTTP503Error, e:
                        log('Error getting data from %s (503: API Limit Exceeded), trying again' % provider.name, xbmc.LOGERROR)
                        time.sleep(3)
                        try:
                            backdrops = provider.get_image_list(self.media_id)
                        except:
                            self.failcount = self.failcount + 1
                            log('Error getting data from %s (Possible network error), skipping' % provider.name, xbmc.LOGERROR)
                        else:
                            got_image_list = True
                    except NoFanartError, e:
                        log('No fanart found on %s, skipping' % provider.name, xbmc.LOGINFO)
                    except:
                        self.failcount = self.failcount + 1
                        log('Error getting data from %s (Possible network error), skipping' % provider.name, xbmc.LOGERROR)
                    else:
                        got_image_list = True
                    if got_image_list:
                        self.failcount = 0
                        self.current_fanart = 0
                        for fanarturl in backdrops:
                            ### check if script has been cancelled by user
                            if self.dialog.iscanceled():
                                self.dialog.close()
                                break
                            if not self.failcount < 3:
                                break
                            fanartfile = provider.get_filename(fanarturl)
                            self.current_fanart = self.current_fanart + 1
                            if self.limit_extrafanart and self.current_fanart > self.limit_extrafanart_max:
                                break
                            try:
                                self.fileops._downloadfile(fanarturl, fanartfile, targetdirs)
                            except HTTP404Error, e:
                                log("File does not exist at URL: %s" % str(e), xbmc.LOGWARNING)
                            except DownloadError, e:
                                log("Error downloading file: %s" % str(e), xbmc.LOGERROR)
                                self.failcount = self.failcount + 1
                            if (self.limit_extrafanart and self.limit_extrafanart_max < len(backdrops)):
                                download_max = self.limit_extrafanart_max
                            else: download_max = len(backdrops)
                            self.dialog.update(int(float(self.current_fanart) / float(download_max) * 100.0), __localize__(36006), self.media_name, fanarturl)
            self.processeditems = self.processeditems + 1



if (__name__ == "__main__"):
    log('XBMC Version: %s' % __xbmc_version__, xbmc.LOGNOTICE)
    log('script version %s started' % __addonversion__, xbmc.LOGNOTICE)
    Main()
    log('script stopped')
