import re
import os
import time
import sys
import xbmc
import xbmcaddon
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

import provider
from utils import _log as log
from utils import _dialog as dialog
from script_exceptions import DownloadError, CreateDirectoryError, HTTP404Error, HTTP503Error, NoFanartError, HTTPTimeout
import language
from fileops import fileops

__language__ = language.get_abbrev()


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
        providers = provider.get_providers()
        self.movie_providers = providers['movie_providers']
        self.tv_providers = providers['tv_providers']
        self.music_providers = providers['music_providers']
        self.failcount = 0
        self.failthreshold = 3
        self.fanart_centralized = 0
        self.moviefanart = __addon__.getSetting("movie_enable") == 'true'
        self.tvfanart = __addon__.getSetting("tvshow_enable") == 'true'
        self.centralize_enable = __addon__.getSetting("centralize_enable") == 'true'
        self.centralfolder_split = __addon__.getSetting("centralfolder_split")
        self.centralfolder_movies = __addon__.getSetting("centralfolder_movies")
        self.centralfolder_tvshows = __addon__.getSetting("centralfolder_tvshows")
        self.limit_extrafanart = __addon__.getSetting("limit_extrafanart") == 'true'
        self.limit_extrafanart_max = int(__addon__.getSetting("limit_extrafanart_max").rstrip('0').rstrip('.'))
        self.limit_extrafanart_rating = int(__addon__.getSetting("limit_extrafanart_rating").rstrip('0').rstrip('.'))
        self.limit_language = __addon__.getSetting("limit_language") == 'true'
        self.limit_notext = __addon__.getSetting("limit_notext") == 'true'
        self.use_cache = __addon__.getSetting("use_cache") == 'true'
        self.cache_directory = __addon__.getSetting("cache_directory")
        self.background = __addon__.getSetting("background") == 'true'
        dialog('create', line1 = __localize__(36003), background = self.background)
        self.mediatype = ''
        self.medianame = ''

        # Print out settings to log to help with debugging
        log("######## Extrafanart Downloader: Initializing...............................")
        log("######## Extrafanart Downloader: Settings...................................")
        log('## Add-on ID = %s' % str(__addonid__))
        log('## Add-on Name= %s' % str(__addonname__))
        log('## Add-on Version = %s' % str(__addonversion__))
        log('## Language Used = %s' % str(__language__))
        log('## Download Movie Fanart= %s' % str(self.moviefanart))
        log('## Download TV Show  Fanart = %s' % str(self.tvfanart))
        log('## Background Run = %s' % str(self.background))
        log('## Centralize Extrafanart = %s' % str(self.centralize_enable))
        log('## Central Movies Folder = %s' % str(self.centralfolder_movies))
        log('## Central TV Show Folder = %s' % str(self.centralfolder_tvshows))
        log('## Limit Extrafanart = %s' % str(self.limit_extrafanart))
        log('## Limit Extrafanart Max = %s' % str(self.limit_extrafanart_max))
        log('## Limit Extrafanart Rating = %s' % str(self.limit_extrafanart_rating))
        log('## Limit Language = %s' % str(self.limit_language))
        log('## Limit Fanart with no text = %s' % str(self.limit_notext))
        log('## Backup downloaded fanart= %s' % str(self.use_cache))
        log('## Backup folder = %s' % str(self.cache_directory))
        log("######## Extrafanart Downloader: Starting download.........................")


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
            dialog('update', percentage = 100, line1 = __localize__(36004), background = self.background)
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
        summary = summary_tmp + __localize__(36013)
        dialog('close', background = self.background)
        if not self.failcount < self.failthreshold:
            log('Network error detected, script aborted', xbmc.LOGERROR)
            dialog('okdialog', line1 = __localize__(36007), line2 = __localize__(36008), background = self.background)
        if not xbmc.abortRequested:
            dialog('okdialog', line1 = summary, background = self.background)
        else:
            dialog('okdialog', line1 = __localize__(36007), line2 = summary, background = self.background)

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
            if xbmc.abortRequested:
                log('XBMC abort requested, aborting')
                break
            ### check if script has been cancelled by user
            if dialog('iscanceled', background = self.background):
                break
            if not self.failcount < self.failthreshold:
                break
            try:
                self.media_path = os.path.split(currentmedia["path"])[0].rsplit(' , ', 1)[1]
            except:
                self.media_path = os.path.split(currentmedia["path"])[0]
            self.media_id = currentmedia["id"]
            self.media_name = currentmedia["name"]
            dialog('update', percentage = int(float(self.processeditems) / float(len(media_list)) * 100.0), line1 = __localize__(36005), line2 = self.media_name, line3 = '', background = self.background)
            log('Processing media: %s' % self.media_name, xbmc.LOGNOTICE)
            log('ID: %s' % self.media_id)
            log('Path: %s' % self.media_path)
            targetdirs = []
            extrafanart_dir = os.path.join(self.media_path, 'extrafanart')
            targetdirs.append(extrafanart_dir)
            if self.centralize_enable:
                if self.mediatype == 'tvshow':
                    if not self.centralfolder_tvshows == '':
                        targetdirs.append(self.centralfolder_tvshows)
                    else:
                        log('Error: Central fanart enabled but TV Show folder not set, skipping', xbmc.LOGERROR)
                elif self.mediatype == 'movie':
                    if not self.centralfolder_movies == '':
                        targetdirs.append(self.centralfolder_movies)
                    else:
                        log('Error: Central fanart enabled but Movies folder not set, skipping', xbmc.LOGERROR)
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
                        time.sleep(5)
                        try:
                            backdrops = provider.get_image_list(self.media_id)
                        except DownloadError, e:
                            self.failcount = self.failcount + 1
                            log('Error getting data from %s (Possible network error: %s), skipping' % (provider.name, str(e)), xbmc.LOGERROR)
                        except HTTP503Error, e:
                            self.failcount = self.failcount + 1
                            log('Error getting data from %s (503: API Limit Exceeded), skipping' % provider.name, xbmc.LOGERROR)
                        else:
                            got_image_list = True
                    except NoFanartError, e:
                        log('No fanart found on %s, skipping' % provider.name, xbmc.LOGINFO)
                    except HTTPTimeout, e:
                        self.failcount = self.failcount + 1
                        log('Error getting data from %s (Timed out), skipping' % provider.name, xbmc.LOGERROR)
                    except DownloadError, e:
                        self.failcount = self.failcount + 1
                        log('Error getting data from %s (Possible network error: %s), skipping' % (provider.name, str(e)), xbmc.LOGERROR)
                    else:
                        got_image_list = True
                    if got_image_list:
                        self.failcount = 0
                        self.current_fanart = 0
                        if (self.limit_extrafanart and self.limit_extrafanart_max < len(backdrops)):
                            download_max = self.limit_extrafanart_max
                        else: download_max = len(backdrops)
                        targets = targetdirs[:]
                        if self.use_cache and not self.cache_directory == '':
                            targets.append(self.cache_directory)
                        for fanart in backdrops:
                            fanarturl = fanart['url']
                            ### check if script has been cancelled by user
                            if dialog('iscanceled', background = self.background):
                                dialog('close', background = self.background)
                                break
                            if not self.failcount < 3:
                                break
                            fanartfile = provider.get_filename(fanarturl)
                            self.current_fanart = self.current_fanart + 1
                            
                            if self.limit_extrafanart and self.current_fanart > self.limit_extrafanart_max:
                                self.fileops._delete_file_in_dirs(fanartfile, targetdirs)
                                continue
                            if self.limit_extrafanart and 'rating' in fanart and fanart['rating'] < self.limit_extrafanart_rating:
                                log('Cleanup %s with low rating: %s' % (fanartfile, fanart['rating']), xbmc.LOGNOTICE)
                                self.fileops._delete_file_in_dirs(fanartfile, targetdirs)
                            elif self.limit_extrafanart and 'series_name' in fanart and self.limit_notext and fanart['series_name']:
                                log('Cleanup %s with text' % fanartfile, xbmc.LOGNOTICE)
                                self.fileops._delete_file_in_dirs(fanartfile, targetdirs)
                            elif self.limit_extrafanart and self.limit_language and 'language' in fanart and fanart['language'] != __language__:
                                log('Cleanup %s not matching language: %s' % (fanartfile, xbmc.getLanguage()), xbmc.LOGNOTICE)
                                self.fileops._delete_file_in_dirs(fanartfile, targetdirs)
                            else:
                                try:
                                    self.fileops._downloadfile(fanarturl, fanartfile, targets)
                                except HTTP404Error, e:
                                    log("File does not exist at URL: %s" % str(e), xbmc.LOGWARNING)
                                except HTTPTimeout, e:
                                    self.failcount = self.failcount + 1
                                    log("Error downloading file: %s, timed out" % str(e), xbmc.LOGERROR)
                                except CreateDirectoryError, e:
                                    log("Could not create directory, skipping: %s" % str(e), xbmc.LOGWARNING)
                                    break
                                except DownloadError, e:
                                    log("Error downloading file: %s" % str(e), xbmc.LOGERROR)
                                    self.failcount = self.failcount + 1
                            dialog('update', percentage = int(float(self.current_fanart) / float(download_max) * 100.0), line1 = __localize__(36006), line2 = self.media_name, line3 = fanartfile, background = self.background)
            log('Finished processing media: %s' % self.media_name, xbmc.LOGDEBUG)
            self.processeditems = self.processeditems + 1



if (__name__ == "__main__"):
    log('XBMC Version: %s' % __xbmc_version__, xbmc.LOGNOTICE)
    log('script version %s started' % __addonversion__, xbmc.LOGNOTICE)
    Main()
    log('script stopped')
