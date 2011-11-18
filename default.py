import re
import os
import time
import sys
import xbmc
import xbmcaddon
import platform
from traceback import print_exc
import xbmcgui

### import libraries
from resources.lib import media_setup
from resources.lib import provider
from resources.lib.utils import _log as log
from resources.lib.utils import _dialog as dialog
from resources.lib.script_exceptions import DownloadError, CreateDirectoryError, HTTP404Error, HTTP503Error, NoFanartError, HTTPTimeout, ItemNotFoundError
from resources.lib import language
from resources.lib.fileops import fileops
from xml.parsers.expat import ExpatError
from resources.lib.apply_filters import apply_filters
from resources.lib.settings import _settings
from resources.lib.gui import _maingui

### get addon info
__addon__       = xbmcaddon.Addon()
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__author__      = __addon__.getAddonInfo('author')
__version__     = __addon__.getAddonInfo('version')
__localize__    = __addon__.getLocalizedString
__language__ = language.get_abbrev()
Media_listing = media_setup.media_listing




### clean up temporary folder
def cleanup(self):
    if self.fileops._exists(self.fileops.tempdir):
        dialog('update', percentage = 100, line1 = __localize__(36004), background = self.settings.background)
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
    dialog('close', background = self.settings.background)
    if self.settings.notify:
        log('Notify on finished/error enabled')
        self.settings.background = False
    if not self.settings.failcount < self.settings.failthreshold:
        log('Network error detected, script aborted', xbmc.LOGERROR)
        dialog('okdialog', line1 = __localize__(36007), line2 = __localize__(36008), background = self.settings.background)
    if not xbmc.abortRequested:
        dialog('okdialog', line1 = summary, background = self.settings.background)
    else:
        dialog('okdialog', line1 = __localize__(36007), line2 = summary, background = self.settings.background)


class Main:
    def __init__(self):
        initial_vars(self) 
        self.settings._exist()      # Check if settings.xml exists and correct version
        self.settings._get()        # Get settings from settings.xml
        self.settings._check()      # Check if there are some faulty combinations present
        self.settings._initiallog() # Create debug log for settings
        self.settings._vars()       # Get some settings vars
        self.settings._artype_list()# Fill out the GUI and Arttype lists with enabled options
        runmode_args(self)          # Check for script call methods
        dialog('create', line1 = __localize__(36005), background = self.settings.background)
        if initialise(self):
            if not self.mediatype == '':
                if not self.medianame == '':
                    if self.mode == 'gui':
                        gui_mode(self, self.mediatype, self.medianame)
                    else:
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
                if self.settings.movie_enable:
                    self.Medialist = Media_listing('movie')
                    self.mediatype = 'movie'
                    download_artwork(self, self.Medialist, self.movie_providers)
                else:
                    log('Movie fanart disabled, skipping', xbmc.LOGINFO)
                if self.settings.tvshow_enable:
                    self.Medialist = Media_listing('tvshow')
                    self.mediatype = 'tvshow'
                    download_artwork(self, self.Medialist, self.tv_providers)
                else:
                    log('TV fanart disabled, skipping', xbmc.LOGINFO)
        else:
            log('Initialisation error, script aborting', xbmc.LOGERROR)
        cleanup(self)
        finished_log(self)


    
### Declare standard vars   
def initial_vars(self):
    providers = provider.get_providers()
    self.settings = _settings()
    self.filters = apply_filters()
    self.movie_providers = providers['movie_providers']
    self.tv_providers = providers['tv_providers']
    self.music_providers = providers['music_providers']
    self.mediatype = ''
    self.medianame = ''
    self.mode = ''

### Report the total numbers of downloaded images
def finished_log(self):
    log('## Download totaliser:')
    log('- Artwork: %s' % self.fileops.downloadcount, xbmc.LOGNOTICE)
    log('Movie download totals:')
    log('- Extrafanart: %s' % self.settings.count_movie_extrafanart, xbmc.LOGNOTICE)
    log('- Extrathumbs: %s' % self.settings.count_movie_extrathumbs, xbmc.LOGNOTICE)
    log('TV Show download totals:')
    log('- Extrafanart: %s' % self.settings.count_tvshow_extrafanart, xbmc.LOGNOTICE)

    
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

### gui mode
def gui_mode(self, itemtype, itemname):
    if itemtype == 'movie':
        log("## GUI mode: Movie...")
        self.Medialist = Media_listing('movie')
    elif itemtype == 'tvshow':
        self.Medialist = Media_listing('tvshow')
        log("## GUI mode: TV Show...")
    elif itemtype == 'music':
        self.Medialist = Media_listing('music')
        log("## GUI mode: Music...")
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
        # Check for download mode
        match = re.search("mode=(.*)" , item)
        if match:
            self.mode = match.group(1)
        # Check for mediatype mode
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
        # Check for medianame
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

        
def choose_image(self):
    log( "### image list: %s" % self.image_list )
    self.image_url = self.maingui.MyDialog(self.image_list)
    if self.image_url: return True
    else: return False

def choice_type(self):
    select = xbmcgui.Dialog().select(__language__(36012) , self.type_list)
    if select == -1: 
        log( "### Canceled by user" )
        xbmcgui.Dialog().ok(__language__(36013) , __language__(36014) )
        return False
    else:
        if self.type_list[select] == __language__(32128) : self.clearart = self.show_thumb = self.banner = self.poster = self.characterart = False
        elif self.type_list[select] == __language__(32129) : self.logo = self.show_thumb = self.banner = self.poster = self.characterart = False
        elif self.type_list[select] == __language__(32130) : self.logo = self.show_thumb = self.banner = self.poster = self.clearart = False
        elif self.type_list[select] == __language__(32131) : self.clearart = self.logo = self.banner = self.poster = self.characterart = False
        elif self.type_list[select] == __language__(32132) : self.logo = self.show_thumb = self.clearart = self.poster = self.characterart = False
        elif self.type_list[select] == __language__(32133) : self.logo = self.show_thumb = self.banner = self.clearart = self.characterart = False
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
        if dialog('iscanceled', background = self.settings.background):
            break
        if not self.settings.failcount < self.settings.failthreshold:
            break
        try:
            self.media_path = os.path.split(currentmedia["path"])[0].rsplit(' , ', 1)[1]
        except:
            self.media_path = os.path.split(currentmedia["path"])[0]
        self.media_id = currentmedia["id"]
        self.media_name = currentmedia["name"]
        dialog('update', percentage = int(float(self.processeditems) / float(len(media_list)) * 100.0), line1 = self.media_name, line2 = __localize__(36005), line3 = '', background = self.settings.background)
        log('########################################################')
        log('Processing media: %s' % self.media_name, xbmc.LOGNOTICE)
        log('ID: %s' % self.media_id)
        log('Path: %s' % self.media_path)
        self.target_extrafanartdirs = []
        self.target_extrathumbsdirs = []
        self.target_artworkdir = []
        extrafanart_dir = os.path.join(self.media_path, 'extrafanart')
        extrathumbs_dir = os.path.join(self.media_path, 'extrathumbs')
        self.target_extrafanartdirs.append(extrafanart_dir)
        self.target_extrathumbsdirs.append(extrathumbs_dir)
        self.target_artworkdir.append(self.media_path)
        ### Check if using the centralize option
        if self.settings.centralize_enable:
            if self.mediatype == 'tvshow':
                if not self.settings.centralfolder_tvshows == '':
                    self.target_extrafanartdirs.append(self.settings.centralfolder_tvshows)
                else:
                    log('Error: Central fanart enabled but TV Show folder not set, skipping', xbmc.LOGERROR)
            elif self.mediatype == 'movie':
                if not self.settings.centralfolder_movies == '':
                    self.target_extrafanartdirs.append(self.settings.centralfolder_movies)
                else:
                    log('Error: Central fanart enabled but movies folder not set, skipping', xbmc.LOGERROR)
        ### Check if using the cache option
        self.targets = self.target_extrafanartdirs[:]
        if self.settings.use_cache and not self.settings.cache_directory == '':
            self.targets.append(self.settings.cache_directory)
        if self.media_id == '':
            log('%s: No ID found, skipping' % self.media_name, xbmc.LOGNOTICE)
        elif self.mediatype == 'tvshow' and self.media_id.startswith('tt'):
            log('%s: IMDB ID found for TV show, skipping' % self.media_name, xbmc.LOGNOTICE)
        else:
            self.temp_image_list = []
            self.image_list = []
            for self.provider in providers:
                if not self.settings.failcount < self.settings.failthreshold:
                    break
                artwork_result = ''
                xmlfailcount = 0
                while not artwork_result == 'pass' and not artwork_result == 'skipping':
                    if artwork_result == 'retrying':
                        time.sleep(10)
                    try:
                        self.temp_image_list = self.provider.get_image_list(self.media_id)
                    except HTTP404Error, e:
                        errmsg = '404: File not found'
                        artwork_result = 'skipping'
                    except HTTP503Error, e:
                        xmlfailcount = xmlfailcount + 1
                        errmsg = '503: API Limit Exceeded'
                        artwork_result = 'retrying'
                    except NoFanartError, e:
                        errmsg = 'No fanart found'
                        artwork_result = 'skipping'
                    except ItemNotFoundError, e:
                        errmsg = '%s not found' % self.media_id
                        artwork_result = 'skipping'
                    except ExpatError, e:
                        xmlfailcount = xmlfailcount + 1
                        errmsg = 'Error parsing xml: %s' % str(e)
                        artwork_result = 'retrying'
                    except HTTPTimeout, e:
                        self.settings.failcount = self.settings.failcount + 1
                        errmsg = 'Timed out'
                        artwork_result = 'skipping'
                    except DownloadError, e:
                        self.settings.failcount = self.settings.failcount + 1
                        errmsg = 'Possible network error: %s' % str(e)
                        artwork_result = 'skipping'
                    else:
                        artwork_result = 'pass'
                        for item in self.temp_image_list:
                            self.image_list.append(item)
                    if not xmlfailcount < self.settings.xmlfailthreshold:
                        artwork_result = 'skipping'
                    if not artwork_result == 'pass':
                        log('Error getting data from %s (%s): %s' % (self.provider.name, errmsg, artwork_result))
            if len(self.image_list) > 0:
                if (self.settings.limit_artwork and self.settings.limit_extrafanart_max < len(self.image_list)):
                    self.download_max = self.settings.limit_extrafanart_max
                else:
                    self.download_max = len(self.image_list)
                if self.mode == 'gui':
                    log('here goes gui mode')
                else:
                    _download_process(self)

        log('Finished processing media: %s' % self.media_name, xbmc.LOGDEBUG)
        self.processeditems = self.processeditems + 1

def _download_process(self):    

    if self.settings.movie_enable and self.mediatype == 'movie':
        for arttypes in self.settings.movie_arttype_list:
            try:
                if arttypes['art_type'] == 'extrafanart':
                    _download_art(self, arttypes['art_type'], 'fanart', arttypes['filename'], self.target_extrafanartdirs, self.targets, arttypes['gui'])
                elif arttypes['art_type'] == 'extrathumbs':
                    _download_art(self, arttypes['art_type'], 'fanart', arttypes['filename'], self.target_extrathumbsdirs, self.targets, arttypes['gui'])
                else:
                    _download_art(self, arttypes['art_type'], arttypes['art_type'], arttypes['filename'], target_artworkdir, self.targets, arttypes['gui'])
            except:
                log('some error')

    if self.settings.tvshow_enable and self.mediatype == 'tvshow':
        for arttypes in self.settings.tvshow_arttype_list:
            try:
                if arttypes['art_type'] == 'extrafanart':
                    _download_art(self, arttypes['art_type'], 'fanart', arttypes['filename'], self.target_extrafanartdirs, self.targets, arttypes['gui'])
                else:
                    _download_art(self, arttypes['art_type'], arttypes['art_type'], arttypes['filename'], target_artworkdir, self.targets, arttypes['gui'])                
            except:
                log('some error')

### Artwork downloading
def _download_art(self, art_type, image_type, filename, targetdirs, targets, msg):
    log('Starting with processing: %s' %art_type)
    self.settings.failcount = 0
    current_artwork = 0
    downloaded_artwork = 0
    for artwork in self.image_list:
        imageurl = artwork['url']
        if image_type == artwork['type']:
            ### check if script has been cancelled by user
            if dialog('iscanceled', background = self.settings.background):
                dialog('close', background = self.settings.background)
                break
            if not self.settings.failcount < self.settings.failthreshold:
                break
            # File naming
            if art_type == 'extrafanart':
                artworkfile = ('%s.jpg'%artwork['id'])
            elif art_type == 'extrathumbs':
                artworkfile = (filename+'%s.jpg' % str(downloaded_artwork+1))
            elif art_type == 'seasonthumbs' or art_type == 'seasonbanner':
                artworkfile = (filename+'%s.jpg' %artwork['season'])
            elif art_type == 'seasonposter':
                artworkfile = (filename+'%s.tbn' %artwork['season'])
            else: artworkfile = filename
            #increase  artwork counter
            current_artwork = current_artwork + 1
            # Check for set limits
            limited = self.filters.do_filter(art_type, self.mediatype, artwork, downloaded_artwork)
            if limited[0] and art_type =='extrafanart':
                self.fileops._delete_file_in_dirs(artworkfile, targetdirs, limited[1])
            elif limited[0]: log('Skipped. Reason: %s' %limited[1])
            else:
                try:
                    log('ID of downloaded image: %s' %artwork['id'])
                    self.fileops._downloadfile(imageurl, artworkfile, targetdirs, self.settings.overwrite)
                except HTTP404Error, e:
                    log("File does not exist at URL: %s" % str(e), xbmc.LOGWARNING)
                except HTTPTimeout, e:
                    self.settings.failcount = self.settings.failcount + 1
                    log("Error downloading file: %s, timed out" % str(e), xbmc.LOGERROR)
                except CreateDirectoryError, e:
                    log("Could not create directory, skipping: %s" % str(e), xbmc.LOGWARNING)
                    break
                except DownloadError, e:
                    self.settings.failcount = self.settings.failcount + 1
                    log('Error downloading file: %s (Possible network error: %s), skipping' % (imageurl, str(e)), xbmc.LOGERROR)
                else:
                    downloaded_artwork = downloaded_artwork + 1
            dialog('update', percentage = int(float(current_artwork) / float(self.download_max) * 100.0), line1 = self.media_name, line2 = __localize__(36006) + ' ' + __localize__(msg), line3 = artworkfile, background = self.settings.background)
    log('Finished with: %s' %art_type)

        
### Start of script
if (__name__ == "__main__"):
    log("######## Extrafanart Downloader: Initializing...............................")
    log('## Add-on ID   = %s' % str(__addonid__))
    log('## Add-on Name = %s' % str(__addonname__))
    log('## Authors     = %s' % str(__author__))
    log('## Version     = %s' % str(__version__))
    Main()
    log('script stopped')
