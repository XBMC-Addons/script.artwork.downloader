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

addondir = xbmc.translatePath( __addon__.getAddonInfo('profile') )
settings_file = os.path.join(addondir, "settings.xml")
first_run = False

from resources.lib import media_setup
from resources.lib import provider
from resources.lib.utils import _log as log
from resources.lib.utils import _dialog as dialog
from resources.lib.script_exceptions import DownloadError, CreateDirectoryError, HTTP404Error, HTTP503Error, NoFanartError, HTTPTimeout, ItemNotFoundError
from resources.lib import language
from resources.lib.fileops import fileops
from xml.parsers.expat import ExpatError

Media_listing = media_setup.media_listing
__language__ = language.get_abbrev()

### clean up and
def cleanup(self):
    if self.fileops._exists(self.fileops.tempdir):
        dialog('update', percentage = 100, line1 = __localize__(36004), background = self.background)
        log('Cleaning up temp files')
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


class Main:
    def __init__(self):
        settings_exist(self)
        settings_get(self)
        settings_vars(self)        
        settings_log(self)
        runmode_args(self)
        dialog('create', line1 = __localize__(36005), background = self.background)
        if initialise(self):
            if not self.mediatype == '':
                if not self.medianame == '':
                    solo_mode(self, self.mediatype, self.medianame)
                else:
                    if self.mediatype == 'movie':
                        self.Medialist = Media_listing('movie')
                        log("Bulk mode: movie")
                        download_artwork(self, self.Medialist, self.movie_providers)
                    elif self.mediatype == 'tvshow':
                        self.Medialist = Media_listing('tvshow')
                        log("Bulk mode: TV Shows")
                        download_artwork(self, self.Medialist, self.tv_providers)
                    elif self.mediatype == 'music':
                        log('Bulk mode: Music not yet implemented', xbmc.LOGNOTICE)
            else:
                if self.moviefanart and (self.movie_extrafanart or self.movie_extrathumbs or self.movie_poster):
                    self.Medialist = Media_listing('movie')
                    self.mediatype = 'movie'
                    download_artwork(self, self.Medialist, self.movie_providers)
                else:
                    log('Movie fanart disabled, skipping', xbmc.LOGINFO)
                if self.tvfanart and (self.tvshow_extrafanart or self.tvshow_poster):
                    self.Medialist = Media_listing('tvshow')
                    self.mediatype = 'tvshow'
                    download_artwork(self, self.Medialist, self.tv_providers)
                else:
                    log('TV fanart disabled, skipping', xbmc.LOGINFO)
        else:
            log('Initialisation error, script aborting', xbmc.LOGERROR)
        cleanup(self)
        finished_log(self)

### Check if settings.xml exist
def settings_exist(self):
    if not os.path.isfile(settings_file):
        dialog('okdialog', line1 = __localize__(36037), line2 = __localize__(36038))
        log('Settings.xml file not found. Opening settings window.')
        __addon__.openSettings()
        first_run = True
    else:
        log('Settings.xml file found. Continue with initializing.')

### Get settings from settings.xml
def settings_get(self):
    self.moviefanart = __addon__.getSetting("movie_enable") == 'true'
    self.movie_poster = __addon__.getSetting("movie_poster") == 'true'
    self.movie_fanart = __addon__.getSetting("movie_fanart") == 'true'
    self.movie_extrafanart = __addon__.getSetting("movie_extrafanart") == 'true'
    self.movie_extrathumbs = __addon__.getSetting("movie_extrathumbs") == 'true'
    self.movie_logo = __addon__.getSetting("movie_logo") == 'true'
    self.movie_discart = __addon__.getSetting("movie_discart") == 'true'
    
    self.tvfanart = __addon__.getSetting("tvshow_enable") == 'true'
    self.tvshow_poster = __addon__.getSetting("tvshow_poster") == 'true'
    self.tvshow_fanart = __addon__.getSetting("tvshow_fanart") == 'true'
    self.tvshow_extrafanart = __addon__.getSetting("tvshow_extrafanart") == 'true'
    self.tvshow_clearart = __addon__.getSetting("tvshow_clearart") == 'true'
    self.tvshow_logo = __addon__.getSetting("tvshow_logo") == 'true'
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

  
    
### Declare standard vars   
def settings_vars(self):
    providers = provider.get_providers()
    self.movie_providers = providers['movie_providers']
    self.tv_providers = providers['tv_providers']
    self.music_providers = providers['music_providers']
    self.failcount = 0
    self.failthreshold = 3
    self.xmlfailthreshold = 5
    self.limit_artwork_max = 1
    self.mediatype = ''
    self.medianame = ''
    self.count_tvshow_extrafanart = 0
    self.count_movie_extrafanart = 0
    self.count_movie_extrathumbs = 0

   
### Print out settings to log to help with debugging
def settings_log(self):
    log("## Settings...")
    log('## Language Used = %s' % str(__language__))
    log('## Background Run = %s' % str(self.background))
    
    log('## Download Movie Artwork= %s' % str(self.moviefanart))
    log('## - Movie Poster= %s' % str(self.movie_poster))
    log('## - Movie Fanart= %s' % str(self.movie_fanart))
    log('## - Movie ExtraFanart= %s' % str(self.movie_extrafanart))
    log('## - Movie ExtraThumbs= %s' % str(self.movie_extrathumbs))
    log('## - Movie Logo= %s' % str(self.movie_logo))
    log('## - Movie DiscArt= %s' % str(self.movie_discart))
    
    log('## Download TV Show Artwork = %s' % str(self.tvfanart))
    log('## - TV Show Poster = %s' % str(self.tvshow_poster))
    log('## - TV Show Fanart = %s' % str(self.tvshow_fanart))
    log('## - TV Show ExtraFanart = %s' % str(self.tvshow_extrafanart))
    log('## - TV Show Clearart = %s' % str(self.tvshow_clearart))
    log('## - TV Show Fanart = %s' % str(self.tvshow_logo))
    log('## - TV Show Showbanner = %s' % str(self.tvshow_showbanner))
    log('## - TV Show Seasonbanner = %s' % str(self.tvshow_seasonbanner))
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

### Report the total numbers of downloaded images
def finished_log(self):
    log('## Download totaliser:')
    log('- Artwork: %s' % self.fileops.downloadcount, xbmc.LOGNOTICE)
    log('Movie download totals:')
    log('- Extrafanart: %s' % self.count_movie_extrafanart, xbmc.LOGNOTICE)
    log('- Extrathumbs: %s' % self.count_movie_extrathumbs, xbmc.LOGNOTICE)
    log('TV Show download totals:')
    log('- Extrafanart: %s' % self.count_tvshow_extrafanart, xbmc.LOGNOTICE)

    
### Check for script starting arguments used by skins
def runmode_args(self):
    log("## Checking for starting arguments used by skins")
    try: log( "## arg 0: %s" % sys.argv[0] )
    except:   log( "## no arg0" )
    try: log( "## arg 1: %s" % sys.argv[1] )
    except:   log( "## no arg1" )
    try: log( "## arg 2: %s" % sys.argv[2] )
    except:   log( "## no arg2" )
    try: log( "## arg 3: %s" % sys.argv[3] )
    except:   log( "## no arg3" )
    try: log( "## arg 4: %s" % sys.argv[4] )
    except:   log( "## no arg4" )
    try: log( "arg 5: %s" % sys.argv[5] )
    except:   log( "## no arg5" )
    try: log( "## arg 6: %s" % sys.argv[6] )
    except:   log( "## no arg6" )
    try: log( "## arg 7: %s" % sys.argv[7] )
    except:   log( "## no arg7" )
    try: log( "## arg 8: %s" % sys.argv[8] )
    except:   log( "## no arg8" )




### solo mode
def solo_mode(self, itemtype, itemname):
    if itemtype == 'movie':
        log("## Solo mode: Movie...")
        self.Medialist = Media_listing('movie')
    elif itemtype == 'tvshow':
        self.Medialist = Media_listing('tvshow')
        log("## Solo mode: TV Show...")
    elif itemtype == 'music':
        self.Medialist = Media_listing('music')
        log("## Solo mode: Music...")
    else:
        log("Error: type must be one of 'movie', 'tvshow' or 'music', aborting", xbmc.LOGERROR)
        return False
    log('Retrieving fanart for: %s' % itemname)
    for currentitem in self.Medialist:
        if itemname == currentitem["name"]:
            if itemtype == 'movie':
                self.Medialist = []
                self.Medialist.append(currentitem)
                download_artwork(self, self.Medialist, self.movie_providers)
            if itemtype == 'tvshow':
                self.Medialist = []
                self.Medialist.append(currentitem)
                download_artwork(self, self.Medialist, self.tv_providers)
            break


### load settings and initialise needed directories
def initialise(self):
    for item in sys.argv:
        log("## Checking for downloading mode...")
        match = re.search("mediatype=(.*)" , item)
        if match:
            self.mediatype = match.group(1)
            if self.mediatype == 'tvshow' or self.mediatype == 'movie' or self.mediatype == 'music':
                pass
            else:
                log('Error: invalid mediatype, must be one of movie, tvshow or music', xbmc.LOGERROR)
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
        
### download media fanart
def download_artwork(self, media_list, providers):
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
        targetthumbsdirs = []
        target_artworkdir = []
        extrafanart_dir = os.path.join(self.media_path, 'extrafanart')
        extrathumbs_dir = os.path.join(self.media_path, 'extrathumbs')
        targetdirs.append(extrafanart_dir)
        targetthumbsdirs.append(extrathumbs_dir)
        target_artworkdir.append(self.media_path)
        ### Check if using the centralize option
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
                    log('Error: Central fanart enabled but movies folder not set, skipping', xbmc.LOGERROR)
        ### Check if using the cache option
        targets = targetdirs[:]
        if self.use_cache and not self.cache_directory == '':
            targets.append(self.cache_directory)
        if self.media_id == '':
            log('%s: No ID found, skipping' % self.media_name, xbmc.LOGNOTICE)
        elif self.mediatype == 'tvshow' and self.media_id.startswith('tt'):
            log('%s: IMDB ID found for TV show, skipping' % self.media_name, xbmc.LOGNOTICE)
        else:
            for provider in providers:
                if not self.failcount < self.failthreshold:
                    break
                artwork_result = ''
                self.xmlfailcount = 0
                while not artwork_result == 'pass' and not artwork_result == 'skipping':
                    if artwork_result == 'retrying':
                        time.sleep(10)
                    try:
                        image_list = provider.get_image_list(self.media_id)
                    except HTTP404Error, e:
                        errmsg = '404: File not found'
                        artwork_result = 'skipping'
                    except HTTP503Error, e:
                        self.xmlfailcount = self.xmlfailcount + 1
                        errmsg = '503: API Limit Exceeded'
                        artwork_result = 'retrying'
                    except NoFanartError, e:
                        errmsg = 'No fanart found'
                        artwork_result = 'skipping'
                    except ItemNotFoundError, e:
                        errmsg = '%s not found' % self.media_id
                        artwork_result = 'skipping'
                    except ExpatError, e:
                        self.xmlfailcount = self.xmlfailcount + 1
                        errmsg = 'Error parsing xml: %s' % str(e)
                        artwork_result = 'retrying'
                    except HTTPTimeout, e:
                        self.failcount = self.failcount + 1
                        errmsg = 'Timed out'
                        artwork_result = 'skipping'
                    except DownloadError, e:
                        self.failcount = self.failcount + 1
                        errmsg = 'Possible network error: %s' % str(e)
                        artwork_result = 'skipping'
                    else:
                        artwork_result = 'pass'
                    if not self.xmlfailcount < self.xmlfailthreshold:
                        artwork_result = 'skipping'
                    if not artwork_result == 'pass':
                        log('Error getting data from %s (%s): %s' % (provider.name, errmsg, artwork_result))
                if artwork_result == 'pass':
                    if (self.limit_artwork and self.limit_extrafanart_max < len(image_list)):
                        download_max = self.limit_extrafanart_max
                    else: download_max = len(image_list)

                ### Extrafanart downloading
                    if self.movie_extrafanart or self.tvshow_extrafanart:
                        self.failcount = 0
                        self.current_artwork = 0
                        self.downloaded_artwork = 0
                        log('Extrafanart enabled. Processing')
                        for fanart in image_list:
                            type = 'fanart'
                            size = 'original'
                            imageurl = fanart['url']
                            if size in fanart['size'] and type in fanart['type']:
                                ### check if script has been cancelled by user
                                if dialog('iscanceled', background = self.background):
                                    dialog('close', background = self.background)
                                    break
                                if not self.failcount < self.failthreshold:
                                    break
                                if self.mediatype == 'movie':
                                    fanartfile = provider.get_filename(fanart['id'])
                                else:
                                    fanartfile = provider.get_filename(imageurl)
                                self.current_artwork = self.current_artwork + 1
                                ### Check for set limits
                                #limit on maximum
                                if self.limit_artwork and self.downloaded_artwork >= self.limit_extrafanart_max:
                                    reason = 'Max number fanart reached: %s' % self.limit_extrafanart_max
                                    self.fileops._delete_file_in_dirs(fanartfile, targetdirs, reason)
                                # limit on size
                                elif self.limit_artwork and 'height' in fanart and (self.mediatype == 'movie' and fanart['height'] < self.limit_size_moviefanart) or (self.mediatype == 'tvshow' and fanart['height'] < self.limit_size_tvshowfanart):
                                    reason = 'Size was to small: %s' % fanart['height'] 
                                    self.fileops._delete_file_in_dirs(fanartfile, targetdirs, reason)
                                # limit on rating
                                elif self.limit_artwork and 'rating' in fanart and fanart['rating'] < self.limit_extrafanart_rating:
                                    reason = 'Rating too low: %s' % fanart['rating']
                                    self.fileops._delete_file_in_dirs(fanartfile, targetdirs, reason)
                                # limit without text
                                elif self.limit_artwork and 'series_name' in fanart and self.limit_notext and fanart['series_name']:
                                    reason = 'Has text'
                                    self.fileops._delete_file_in_dirs(fanartfile, targetdirs, reason)
                                # limit on language
                                elif self.limit_artwork and self.limit_language and 'language' in fanart and fanart['language'] != __language__:
                                    reason = "Doesn't match current language: %s" % xbmc.getLanguage()
                                    self.fileops._delete_file_in_dirs(fanartfile, targetdirs, reason)
                                else:
                                    try:
                                        self.fileops._downloadfile(imageurl, fanartfile, targets)
                                    except HTTP404Error, e:
                                        log("File does not exist at URL: %s" % str(e), xbmc.LOGWARNING)
                                    except HTTPTimeout, e:
                                        self.failcount = self.failcount + 1
                                        log("Error downloading file: %s, timed out" % str(e), xbmc.LOGERROR)
                                    except CreateDirectoryError, e:
                                        log("Could not create directory, skipping: %s" % str(e), xbmc.LOGWARNING)
                                        break
                                    except DownloadError, e:
                                        self.failcount = self.failcount + 1
                                        log('Error downloading file: %s (Possible network error: %s), skipping' % (imageurl, str(e)), xbmc.LOGERROR)
                                    else:
                                        self.downloaded_artwork = self.downloaded_artwork + 1
                                dialog('update', percentage = int(float(self.current_artwork) / float(download_max) * 100.0), line1 = __localize__(36006) + ' ' + __localize__(36102), line2 = self.media_name, line3 = fanartfile, background = self.background)
                        if self.mediatype == 'movie': self.count_movie_extrafanart = self.count_movie_extrafanart + self.downloaded_artwork
                        if self.mediatype == 'tvshow': self.count_tvshow_extrafanart = self.count_tvshow_extrafanart + self.downloaded_artwork
                        log('Finished with %s extrafanart' %self.mediatype)
                    else:    
                        log('Extrafanart %s disabled. skipping' %self.mediatype)
                    
                ### Movie extrathumbs downloading
                    if self.movie_extrathumbs and self.mediatype == 'movie':
                        self.failcount = 0
                        self.current_artwork = 0
                        self.downloaded_artwork = 0
                        log('Movie extrathumbs enabled. Processing')
                        for extrathumbs in image_list:
                            type = 'fanart'
                            size = 'thumb'
                            imageurl = extrathumbs['url']
                            if size in extrathumbs['size'] and type in extrathumbs['type']:
                                ### check if script has been cancelled by user
                                if dialog('iscanceled', background = self.background):
                                    dialog('close', background = self.background)
                                    break
                                if not self.failcount < self.failthreshold:
                                    break
                                extrathumbsfile = ('thumb%s.jpg' % str(self.downloaded_artwork+1))
                                self.current_artwork = self.current_artwork + 1
                                ### Check for set limits
                                # limit on maximum
                                if self.downloaded_artwork >= self.limit_extrathumbs_max:
                                    reason = 'Max number extrathumbs reached: %s' % self.downloaded_artwork
                                    self.fileops._delete_file_in_dirs(extrathumbsfile, targetthumbsdirs, reason)
                                # limit on size
                                elif self.limit_extrathumbs and 'height' in extrathumbs and extrathumbs['height'] < int('169'):
                                    reason = 'Size was to small: %s' % extrathumbs['height'] 
                                else:
                                    try:
                                        self.fileops._downloadfile(imageurl, extrathumbsfile, targetthumbsdirs)
                                    except HTTP404Error, e:
                                        log("File does not exist at URL: %s" % str(e), xbmc.LOGWARNING)
                                    except HTTPTimeout, e:
                                        self.failcount = self.failcount + 1
                                        log("Error downloading file: %s, timed out" % str(e), xbmc.LOGERROR)
                                    except CreateDirectoryError, e:
                                        log("Could not create directory, skipping: %s" % str(e), xbmc.LOGWARNING)
                                        break
                                    except DownloadError, e:
                                        self.failcount = self.failcount + 1
                                        log('Error downloading file: %s (Possible network error: %s), skipping' % (imageurl, str(e)), xbmc.LOGERROR)
                                    else:
                                        self.downloaded_artwork = self.downloaded_artwork + 1
                                dialog('update', percentage = int(float(self.current_artwork) / float(download_max) * 100.0), line1 = __localize__(36006) + ' ' + __localize__(36110), line2 = self.media_name, line3 = extrathumbsfile, background = self.background)
                        ### Add to total counter
                        self.count_movie_extrathumbs = self.count_movie_extrathumbs + self.downloaded_artwork
                        log('Finished with %s extrathumbs' %self.mediatype)
                    else:    
                        log('Extrathumbs %s disabled. skipping' %self.mediatype)
        log('Finished processing media: %s' % self.media_name, xbmc.LOGDEBUG)
        self.processeditems = self.processeditems + 1


### Start of script
if (__name__ == "__main__"):
    log("######## Extrafanart Downloader: Initializing...............................")
    log('## Add-on ID = %s' % str(__addonid__))
    log('## Add-on Name= %s' % str(__addonname__))
    log('## Add-on Version = %s' % str(__addonversion__))
    Main()
    log('script stopped')