#import modules
import re
import os
import time
import sys
import xbmc
import xbmcaddon
import platform
import xbmcgui
import urllib
from traceback import print_exc

### import libraries
from resources.lib import language
from resources.lib import media_setup
from resources.lib import provider
from resources.lib.provider import tmdb
from resources.lib.utils import _log as log
from resources.lib.utils import _dialog as dialog
from resources.lib.utils import _getUniq as getUniq
from resources.lib.script_exceptions import DownloadError, CreateDirectoryError, HTTP404Error, HTTP503Error, NoFanartError, HTTPTimeout, ItemNotFoundError, CopyError
from resources.lib.fileops import fileops
from resources.lib.apply_filters import apply_filters
from resources.lib.settings import _settings
from resources.lib.media_setup import _media_listing as media_listing
from xml.parsers.expat import ExpatError
### get addon info
__addon__       = xbmcaddon.Addon()
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__author__      = __addon__.getAddonInfo('author')
__version__     = __addon__.getAddonInfo('version')
__localize__    = __addon__.getLocalizedString
__addonpath__   = __addon__.getAddonInfo('path')
__language__    = language.get_abbrev()

### set button actions for GUI
ACTION_PREVIOUS_MENU = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )


class Main:

    def __init__(self):
        self.initial_vars() 
        self.settings._get()        # Get settings from settings.xml
        self.settings._get_limit() # Get settings from settings.xml
        self.settings._check()      # Check if there are some faulty combinations present
        self.settings._initiallog() # Create debug log for settings
        self.settings._vars()       # Get some settings vars
        self.settings._artype_list()# Fill out the GUI and Arttype lists with enabled options
        if self.initialise():
            # Check for silent background mode
            if self.silent:
                log('Silent mode')
                self.settings.background = True
                self.settings.notify = False
            # Check for gui mode
            elif self.mode == 'gui':
                log('set dialog true')
                self.settings.background = False
                self.settings.notify = False
                self.settings.files_overwrite = True
            dialog('create', line1 = __localize__(32008), background = self.settings.background)
            # Check if mediatype is specified
            if not self.mediatype == '':
                # Check if medianame is specified
                if not self.medianame == '':
                    if self.mode == 'gui':
                        # GUI mode check is at the end of: 'def download_artwork'
                        self.solo_mode(self.mediatype, self.medianame, self.mediapath)
                    else:
                        self.solo_mode(self.mediatype, self.medianame, self.mediapath)
                        if not dialog('iscanceled', background = self.settings.background) and not self.mode == 'customgui':
                            self._batch_download(self.download_list)
                # No medianame specified
                else:
                    if self.mediatype == 'movie':
                        self.Medialist = media_listing('movie')
                        log("Bulk mode: movie")
                        self.settings.movie_enable = 'true'
                        self.settings.tvshow_enable = 'false'
                        self.download_artwork(self.Medialist, self.movie_providers)
                    elif self.mediatype == 'tvshow':
                        self.settings.movie_enable = 'false'
                        self.settings.tvshow_enable = 'true'
                        self.Medialist = media_listing('tvshow')
                        log("Bulk mode: TV Shows")
                        self.download_artwork(self.Medialist, self.tv_providers)
                    if not dialog('iscanceled', background = self.settings.background):
                        self._batch_download(self.download_list)
            # No mediatype is specified
            else:
                # activate both movie/tvshow for custom run
                if self.mode == 'custom':
                    self.settings.movie_enable = True
                    self.settings.tvshow_enable = True
                # Normal oprations check
                if self.settings.movie_enable and not dialog('iscanceled', background = True):
                    self.Medialist = media_listing('movie')
                    self.mediatype = 'movie'
                    self.download_artwork(self.Medialist, self.movie_providers)
                else:
                    log('Movie fanart disabled, skipping', xbmc.LOGINFO)
                if self.settings.tvshow_enable and not dialog('iscanceled', background = True):
                    self.Medialist = media_listing('tvshow')
                    self.mediatype = 'tvshow'
                    self.download_artwork(self.Medialist, self.tv_providers)
                else:
                    log('TV fanart disabled, skipping', xbmc.LOGINFO)
                if not dialog('iscanceled', background = self.settings.background):
                    self._batch_download(self.download_list)
        else:
            log('Initialisation error, script aborting', xbmc.LOGERROR)
        # Make sure that files_overwrite option get's reset after downloading
        __addon__.setSetting(id="files_overwrite", value='false')
        # Cleaning up
        self.cleanup()

    ### Declare standard vars   
    def initial_vars(self):
        providers = provider.get_providers()
        self.settings = _settings()
        self.filters = apply_filters()
        self.movie_providers = providers['movie_providers']
        self.tv_providers = providers['tv_providers']
        self.download_counter = {}
        self.download_counter['Total Artwork'] = 0
        self.mediatype = ''
        self.medianame = ''
        self.mediapath = ''
        self.mode = ''
        self.silent = ''
        self.gui_selected_type = ''
        self.gui_imagelist = ''
        self.failed_items = []
        self.download_list = []
        self._download_art_succes = False

    ### load settings and initialise needed directories
    def initialise(self):
        log("## Checking for script arguments")
        try:
            log( "## arg 0: %s" % sys.argv[0] )
            log( "## arg 1: %s" % sys.argv[1] )
            log( "## arg 2: %s" % sys.argv[2] )
            log( "## arg 3: %s" % sys.argv[3] )
            log( "## arg 4: %s" % sys.argv[4] )
            log( "## arg 5: %s" % sys.argv[5] )
            log( "## arg 6: %s" % sys.argv[6] )
            log( "## arg 7: %s" % sys.argv[7] )
        except:
            log( "## No more arg" )
        log("## Checking for downloading mode...")
        for item in sys.argv:
            # Check for download mode
            match = re.search("silent=(.*)" , item)
            if match:
                self.silent = match.group(1)
            # Check for download mode
            match = re.search("mode=(.*)" , item)
            if match:
                self.mode = match.group(1)
            # Check for mediatype mode
            match = re.search("mediatype=(.*)" , item)
            if match:
                self.mediatype = match.group(1)
                if self.mediatype == 'tvshow' or self.mediatype == 'movie':
                    pass
                else:
                    log('Error: invalid mediatype, must be one of movie, tvshow or music', xbmc.LOGERROR)
                    return False
            # Check for medianame
            match = re.search("medianame=(.*)" , item)
            if match:
                self.medianame = match.group(1)
            # Check for mediapath
            match = re.search("mediapath=(.*)" , item)
            if match:
                self.mediapath = (match.group(1).rstrip(' /\ '))
                log('matchgroup: %s' %self.mediapath)
        try:
            # Creates temp folder
            self.fileops = fileops()
        except CreateDirectoryError, e:
            log("Could not create directory: %s" % str(e))
            return False
        else:
            return True 

    def cleanup(self):
        if self.fileops._exists(self.fileops.tempdir):
            dialog('update', percentage = 100, line1 = __localize__(32005), background = self.settings.background)
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
                log('Deleted temp directory: %s' % self.fileops.tempdir)
        ### log results and notify user
        # print download totals to log
        log('##### Download totaliser:')
        log('- Total Artwork: %s' % self.download_counter['Total Artwork'], xbmc.LOGNOTICE)
        for artwork_type in self.download_counter:
            if not artwork_type == 'Total Artwork':
                log('- %s: %s' % (artwork_type, self.download_counter[artwork_type]), xbmc.LOGNOTICE)
        # print failed items
        log('##### Failed items:')
        if not self.failed_items:
            log(' - No failed/missing items found')
        else:
            for item in getUniq(self.failed_items):
                log(' - %s' %item, xbmc.LOGNOTICE)
        # dialogs
        summary = __localize__(32012) + ': %s ' % self.download_counter['Total Artwork'] + __localize__(32016)
        summary_notify = ': %s ' % self.download_counter['Total Artwork'] + __localize__(32016)
        provider_msg1 = __localize__(32001)
        provider_msg2 = __localize__(32184) + " | " + __localize__(32185) + " | " + __localize__(32186)
        summary_breakdown = ''
        for artwork_type in self.download_counter:
            if not artwork_type == 'Total Artwork':
                summary_tmp = '- %s: %s' % (artwork_type, self.download_counter[artwork_type])
                summary_breakdown = summary_breakdown + ', ' + summary_tmp
        dialog('close', background = self.settings.background)
        # Some dialog checks
        if self.settings.notify:
            log('Notify on finished/error enabled')
            self.settings.background = False
        if xbmc.Player().isPlayingVideo() or self.silent or self.mode == 'gui' or self.mode == 'customgui' or self.mode == 'custom':
            log('Silent finish because of playing a video or silent mode')
            self.settings.background = True
        if not self.settings.failcount < self.settings.failthreshold:
            log('Network error detected, script aborted', xbmc.LOGERROR)
            dialog('okdialog', line1 = __localize__(32010), line2 = __localize__(32011), background = self.settings.background)
        if not xbmc.abortRequested:
            if self.settings.background:
                dialog('okdialog', line0 = summary_notify, line1 = provider_msg1 + ' ' + provider_msg2, background = self.settings.background)
            else:
                dialog('okdialog', line1 = summary, line2 = provider_msg1, line3 = provider_msg2, background = self.settings.background)
        else:
            dialog('okdialog', line1 = __localize__(32010), line2 = summary, background = self.settings.background)
        '''
        if self.mode == 'gui' or self.mode == 'customgui':
            if self._download_art_succes:
                xbmc.executebuiltin( 'XBMC.ReloadSkin()' )
        '''

    ### solo mode
    def solo_mode(self, itemtype, itemname, itempath):
        log('-----------------')
        log('Debugging type: %s' %itemtype)
        log('Debugging name: %s' %itemname)
        log('Debugging path: %s' %itempath)
        log('-----------------')
        # activate both movie/tvshow for custom r
        if self.mode == 'custom':
            self.settings.movie_enable = True
            self.settings.tvshow_enable = True
        if itemtype == 'movie':
            log("## Solo mode: Movie...")
            self.Medialist = media_listing('movie')
        elif itemtype == 'tvshow':
            self.Medialist = media_listing('tvshow')
            log("## Solo mode: TV Show...")
        else:
            log("Error: type must be one of 'movie', 'tvshow', aborting", xbmc.LOGERROR)
            return False
        log('Retrieving fanart for: %s' % itemname)
        # Search through the media lists for match
        for currentitem in self.Medialist:
            if itemname == currentitem["name"]:
                # Check on exact path match when provided
                if itempath == currentitem['path'] or itempath == '':
                    self.Medialist = []
                    self.Medialist.append(currentitem)
                else:
                    self.Medialist = []
        if itemtype == 'movie':
            self.download_artwork(self.Medialist, self.movie_providers)
        elif itemtype == 'tvshow':
            self.download_artwork(self.Medialist, self.tv_providers)


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
            # Declare some vars
            self.media_id   = currentmedia["id"]
            self.media_name = currentmedia["name"]
            self.media_path = currentmedia["path"]
            dialog('update', percentage = int(float(self.processeditems) / float(len(media_list)) * 100.0), line1 = self.media_name, line2 = __localize__(32008), line3 = '', background = self.settings.background)
            log('########################################################')
            log('Processing media:  %s' % self.media_name, xbmc.LOGNOTICE)
            # do some id conversions 
            if self.mediatype == 'movie' and self.media_id == '':
                self.media_id = tmdb._search_movie(self.media_name,currentmedia["year"])
            elif self.mediatype == 'movie' and not self.media_id == '' and not self.media_id.startswith('tt'):
                self.media_id_old = self.media_id
                self.media_id = "tt%.7d" % int(self.media_id)
                log('No IMDB ID found, try ID conversion: %s -> %s' % (self.media_id_old,self.media_id), xbmc.LOGNOTICE)
            log('Provider ID:       %s' % self.media_id)
            log('Movie path:        %s' % self.media_path)
            # Declare the target folders
            self.target_extrafanartdirs = []
            self.target_extrathumbsdirs = []
            self.target_artworkdir = []
            artwork_dir = os.path.join(self.media_path + '/')
            extrafanart_dir = os.path.join(artwork_dir + 'extrafanart' + '/')
            extrathumbs_dir = os.path.join(artwork_dir + 'extrathumbs' + '/')
            self.target_artworkdir.append(artwork_dir)
            self.target_extrafanartdirs.append(extrafanart_dir)
            self.target_extrathumbsdirs.append(extrathumbs_dir)
            
            # Check if using the centralize option
            if self.settings.centralize_enable:
                if self.mediatype == 'tvshow':
                    self.target_extrafanartdirs.append(self.settings.centralfolder_tvshows)
                elif self.mediatype == 'movie':
                    self.target_extrafanartdirs.append(self.settings.centralfolder_movies)

            # Check for presence of id used by source sites
            if self.mode == 'gui' and ((self.media_id == '') or (self.mediatype == 'tvshow' and self.media_id.startswith('tt'))):
                dialog('close', background = self.settings.background)
                dialog('okdialog','' ,self.media_name , __localize__(32030))
            elif self.media_id == '':
                log('- No ID found, skipping', xbmc.LOGNOTICE)
                self.failed_items.append('[%s] No ID found, skipping' % self.media_name)
            elif self.mediatype == 'tvshow' and self.media_id.startswith('tt'):
                log('- IMDB ID found for TV show, skipping', xbmc.LOGNOTICE)
                self.failed_items.append('[%s]: IMDB ID found for TV show, skipping' % self.media_name)
            
            # If correct ID found continue
            else:
                self.temp_image_list = []
                self.image_list = []
                # Run through all providers getting their imagelisting
                for self.provider in providers:
                    if not self.settings.failcount < self.settings.failthreshold:
                        break
                    artwork_result = ''
                    xmlfailcount = 0
                    while not artwork_result == 'pass' and not artwork_result == 'skipping':
                        if artwork_result == 'retrying':
                            time.sleep(self.settings.api_timedelay)
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
                            errmsg = 'No artwork found'
                            artwork_result = 'skipping'
                            self.failed_items.append('[%s] No fanart found' %self.media_name)
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
                    # Check for GUI mode
                    if self.mode == 'gui':
                        log('- Using GUI mode')
                        self._gui_mode()
                    elif self.mode == 'custom':
                        log('- Using custom mode')
                        self._custom_mode()
                    else:
                        #log('- Using bulk mode')
                        self._download_process()
            self.processeditems = self.processeditems + 1

    ### Processes the bulk mode downloading of files
    def _download_process(self):
        log('- Start processing image list')
        if not self.mode == 'custom':
            self.download_arttypes = []
            for item in self.settings.available_arttypes:
                if item['bulk_enabled'] and self.mediatype == item['media_type']:
                    self.download_arttypes.append(item['art_type'])

        for item in self.settings.available_arttypes:
            if item['art_type'] in self.download_arttypes and ((self.settings.movie_enable and self.mediatype == item['media_type']) or (self.settings.tvshow_enable and self.mediatype == item['media_type'])):
                if item['art_type'] == 'extrafanart':
                    self._download_art(item['art_type'], 'fanart', item['filename'], self.target_extrafanartdirs,  item['gui_string'])
                elif item['art_type'] == 'defaultthumb' and self.mediatype == 'movie':
                    self._download_art(item['art_type'], 'poster', item['filename'], self.target_artworkdir,  item['gui_string'])    
                elif item['art_type'] == 'defaultthumb' and self.mediatype == 'tvshow':
                    self._download_art(item['art_type'],  str.lower(self.settings.tvshow_defaultthumb_type), item['filename'], self.target_artworkdir,  item['gui_string'])
                elif item['art_type'] == 'extrathumbs':
                    self._download_art(item['art_type'], 'thumb', item['filename'], self.target_extrathumbsdirs,  item['gui_string'])
                else:
                    self._download_art(item['art_type'], item['art_type'], item['filename'], self.target_artworkdir,  item['gui_string'])


    ### Retrieves imagelist for GUI solo mode
    def _gui_imagelist(self, art_type):
        image_type = art_type
        log('- Retrieving image list for GUI')
        self.gui_imagelist = []
        # do some check for special cases
        if art_type == 'defaultthumb' and self.mediatype == 'tvshow':
            image_type = str.lower(self.settings.tvshow_defaultthumb_type)
        elif art_type == 'defaultthumb' and self.mediatype == 'movie':
            image_type = 'poster'
        elif art_type == 'extrafanart':
            image_type == 'fanart'
        elif art_type == 'extrathumbs':
            image_type == 'fanart'
        #retrieve list
        for artwork in self.image_list:
            if  artwork['type'] == image_type:
                self.gui_imagelist.append(artwork)
        if self.gui_imagelist == '':
            return False
        else:
            return True

    ### Artwork downloading
    def _download_art(self, art_type, image_type, filename, targetdirs, msg):
        log('* Image type: %s' %art_type)
        self.settings.failcount = 0
        current_artwork = 0
        artwork_number = 0
        limit_counter = 0
        final_image_list = []
        if (self.mode == 'gui' or self.mode == 'customgui') and not art_type == 'extrafanart' and not art_type == 'extrathumbs':
            artwork = {}
            artwork['url'] = self.image_url
            artwork['type'] = image_type
            final_image_list.append(artwork)
        else:
            for item in self.image_list:
                final_image_list.append(item)
        if len(final_image_list) == 0:
            log('- Nothing to download')
        else:
            for artwork in final_image_list:
                if image_type ==  artwork['type']:
                    ### check if script has been cancelled by user
                    if dialog('iscanceled', background = self.settings.background):
                        dialog('close', background = self.settings.background)
                        break
                    if not self.settings.failcount < self.settings.failthreshold:
                        break   

                    # Create an image info list
                    item = {}
                    item['url'] = artwork['url']
                    item['targetdirs'] = targetdirs
                    item['media_name'] = self.media_name
                    item['media_type'] = self.mediatype
                    item['artwork_type'] = art_type
                    item['artwork_string'] = msg
                    item['artwork_details'] = artwork
                    current_artwork = current_artwork + 1

                    # File naming
                    if item['artwork_type'] == 'extrafanart' and item['media_type'] == 'movie':
                        item['filename'] = artwork['url'].rsplit('/', 1)[1]
                    elif item['artwork_type'] == 'extrafanart' and item['media_type'] == 'tvshow':
                        item['filename'] = ('%s.jpg'% artwork['id'])
                    elif item['artwork_type'] == 'extrathumbs':
                        item['filename'] = (filename+'%s.jpg' % str(limit_counter + 1))
                    elif item['artwork_type'] == 'seasonthumbs' or item['artwork_type'] == 'seasonbanner':
                        item['filename'] = (filename+'%s.jpg' % artwork['season'])
                    elif item['artwork_type'] == 'seasonposter':
                        item['filename'] = (filename+'%s.jpg' % artwork['season'])
                    else: item['filename'] = filename

                    # Continue 
                    if (self.mode == 'gui' or self.mode == 'customgui') and not item['artwork_type'] == 'extrafanart' and not item['artwork_type'] == 'extrathumbs':
                        self.download_list = image_list
                    elif image_type == artwork['type']:
                        # Check for set limits
                        limited = self.filters.do_filter( item['artwork_type'], item['media_type'], item['artwork_details'], limit_counter )
                        # Delete extrafanart when below settings
                        if limited[0] and item['artwork_type'] =='extrafanart':
                            self.fileops._delete_file_in_dirs( item['filename'], item['targetdirs'], limited[1],item['media_name'] )
                        # Just ignore image when it's below settings
                        elif limited[0]:
                            log( "- Ignoring (%s): %s" % ( limited[1], item['filename']) )
                            # Check if artwork doesn't exist and the ones available are below settings
                            for targetdir in item['targetdirs']:
                                if not self.fileops._exists(os.path.join (targetdir, item['filename']) ) and not item['artwork_type'] == 'extrafanart' or not item['artwork_type'] == 'extrathumbs':
                                    self.failed_items.append('[%s] Skipping %s - Below limit setting' % (self.media_name,item['artwork_type']) )
                        else:
                            # Always add to list when set to overwrite
                            if self.settings.files_overwrite:
                                self.download_list.append(item)
                            else:
                                # Check if image already exist
                                missingfiles = False
                                for targetdir in item['targetdirs']:
                                    if not self.fileops._exists( os.path.join(targetdir, item['filename']) ):
                                        missingfiles = True
                                if missingfiles:
                                    self.download_list.append(item)
                                else:
                                    log("- Ignoring (Exists in all target directories): %s" % item['filename'] )
                            # Raise limit counter because image was added to list
                            limit_counter = limit_counter + 1
                    else: pass
            # Add to failed items if 0
            if current_artwork == 0:
                self.failed_items.append('[%s] No %s found' % (self.media_name,art_type) )
            # Print log message number of found images per art type
            log('- Found a total of: %s %s' % (current_artwork, art_type) )

    def _batch_download(self, image_list):
        log('########################################################')
        if len(image_list) == 0:
            log('- Nothing to download')
        else:
            log('- Starting download')
            # Download artwork that passed the limit check
            for item in image_list:
                if dialog('iscanceled', background = self.settings.background):
                    break
                dialog('update', percentage = int(float(self.download_counter['Total Artwork']) / float(len(image_list)) * 100.0), line1 = item['media_name'], line2 = __localize__(32009) + ' ' + item['artwork_string'], line3 = item['filename'], background = self.settings.background)
                # Try downloading the file and catch errors while trying to
                try:
                    self.fileops._downloadfile(item['url'], item['filename'], item['targetdirs'], item['media_name'])
                except HTTP404Error, e:
                    log("URL not found: %s" % str(e), xbmc.LOGERROR)
                    self._download_art_succes = False
                except HTTPTimeout, e:
                    self.settings.failcount = self.settings.failcount + 1
                    log("Download timed out: %s" % str(e), xbmc.LOGERROR)
                    self._download_art_succes = False
                except CreateDirectoryError, e:
                    log("Could not create directory, skipping: %s" % str(e), xbmc.LOGWARNING)
                    self._download_art_succes = False
                except CopyError, e:
                    log("Could not copy file (Destination may be read only), skipping: %s" % str(e), xbmc.LOGWARNING)
                    self._download_art_succes = False
                except DownloadError, e:
                    self.settings.failcount = self.settings.failcount + 1
                    log('Error downloading file: %s (Possible network error: %s), skipping' % (url, str(e)), xbmc.LOGERROR)
                    self._download_art_succes = False
                else:
                    try:
                        self.download_counter[ item['artwork_string'] ] = self.download_counter[ item['artwork_string'] ] + 1
                    except KeyError:
                        self.download_counter[ item['artwork_string'] ] = 1
                    self.download_counter['Total Artwork'] = self.download_counter['Total Artwork'] + 1
                    self._download_art_succes = True
            log('Finished download')
        log('########################################################')

    def _gui_mode(self):
        # Close the 'checking for artwork' dialog before opening the GUI list
        dialog('close', background = self.settings.background)
        self.GUI_type_list = []
        # Fill GUI art type list
        for item in self.settings.available_arttypes:
            if item['solo_enabled'] == 'true' and self.mediatype == item['media_type']:
                gui = item['gui_string']
                self.GUI_type_list.append (gui)
        # 
        if len(self.GUI_type_list) == 1:
            self.GUI_type_list[0] = "True"
        if ( len(self.GUI_type_list) == 1 ) or self._choice_type():
            self.gui_imagelist = False
            
            self._gui_imagelist(self.gui_selected_type)
            log('- Image put to GUI: %s' %self.gui_imagelist)
        
        # Download the selected image
        if self.gui_imagelist:
            if self._choose_image():
                self._download_art(self.gui_selected_type, self.gui_selected_type, self.gui_selected_filename, self.target_artworkdir, self.gui_selected_msg)
                self._batch_download(self.download_list)
                if not self._download_art_succes:
                    xbmcgui.Dialog().ok(__localize__(32006) , __localize__(32007) )
        if not self.gui_imagelist and not self.gui_selected_type == '':
            log('- No artwork found')
            xbmcgui.Dialog().ok(self.media_name , self.gui_selected_msg + ' ' + __localize__(32022) )
        elif self._download_art_succes:
            log('- Download succesfull')
        else:
            log('- Cancelled')
            xbmcgui.Dialog().ok(__localize__(32017) , __localize__(32018) )

    # This creates the art type selection dialog. The string id is the selection constraint for what type has been chosen.
    def _choice_type(self):
        select = xbmcgui.Dialog().select(__addonname__ + ': ' + __localize__(32015) , self.GUI_type_list)
        self.gui_selected_type = ''
        if select == -1: 
            log( "### Canceled by user" )
            return False
        else:
            # Check what artwork type has been chosen and parse the image restraints
            for item in self.settings.available_arttypes:
                if self.GUI_type_list[select] == item['gui_string'] and self.mediatype == item['media_type']:
                    self.gui_selected_type = item['art_type']
                    self.gui_selected_filename = item['filename']
                    self.gui_selected_msg = item['gui_string']
                    return True
            else:
                return False

    def _custom_mode(self):
        self.download_arttypes = []
        # Look for argument matching artwork types
        for item in sys.argv:
            for type in self.settings.available_arttypes:
                if item == type['art_type'] and self.mediatype == type['media_type']:
                    log('- Custom mode arttype: %s' %type['art_type'])
                    self.download_arttypes.append(item)

        # If only one specified
        if len(self.download_arttypes) == 1 and not self.medianame == '':
            log('- Start custom solomode')
            for types in self.download_arttypes:
                gui_arttype = types
            self._gui_imagelist(gui_arttype)
            log('- Number of images: %s' %len(self.gui_imagelist))
            if len(self.gui_imagelist) > 1:
                self.mode = 'customgui'
                log('- Image list larger than 1')
                if self._choose_image():
                    log('- Chosen: %s'%self.image_url)
                    for item in self.settings.available_arttypes:
                        if gui_arttype == item['art_type'] and self.mediatype == item['media_type']:
                            self.gui_selected_type = item['art_type']
                            self.gui_selected_filename = item['filename']
                            self.gui_selected_msg = item['gui_string']
                    self._download_art(self.gui_selected_type, self.gui_selected_type, self.gui_selected_filename, self.target_artworkdir, self.gui_selected_msg)
                    self._batch_download(self.download_list)
                    if not self._download_art_succes:
                        xbmcgui.Dialog().ok(__localize__(32006) , __localize__(32007) )
                if self._download_art_succes:
                    log('- Download succesfull')
                else:
                    log('- Cancelled')
                    xbmcgui.Dialog().ok(__localize__(32017) , __localize__(32018) )
            else:
                self._download_process()
                log('- More than 1 image available')

        # If more than one specified
        else:
            log('- Start custom bulkmode')
            self._download_process()


    def _choose_image(self):
        log( "### image list: %s" % self.gui_imagelist)
        self.image_url = self.MyDialog(self.gui_imagelist)
        if self.image_url:
            return True
        else:
            return False

    def MyDialog(self, image_list):
        w = MainGui( "DialogSelect.xml", __addonpath__, listing=image_list )
        w.doModal()
        try: return w.selected_url
        except: 
            print_exc()
            return False
        del w

class MainGui( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self )
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )
        self.listing = kwargs.get( "listing" )

    def onInit(self):
        try :
            self.img_list = self.getControl(6)
            self.img_list.controlLeft(self.img_list)
            self.img_list.controlRight(self.img_list)
            self.getControl(3).setVisible(False)
        except :
            print_exc()
            self.img_list = self.getControl(3)

        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel(__localize__(32015))

        for image in self.listing:
            listitem = xbmcgui.ListItem( 'Language: %s  -  Rating: %s' %(image['language'],image['rating']) )
            listitem.setIconImage( image['url'] )
            listitem.setLabel2( image['url'] )
            self.img_list.addItem( listitem )
        self.setFocus(self.img_list)

    def onAction(self, action):
        if action in ACTION_PREVIOUS_MENU:
            self.close()


    def onClick(self, controlID):
        log( "# GUI control: %s" % controlID )
        if controlID == 6 or controlID == 3: 
            num = self.img_list.getSelectedPosition()
            log( "# GUI position: %s" % num )
            self.selected_url = self.img_list.getSelectedItem().getLabel2()
            self.close()

    def onFocus(self, controlID):
        pass


### Start of script
if (__name__ == "__main__"):
    log("######## Extrafanart Downloader: Initializing...............................")
    log('## Add-on ID   = %s' % str(__addonid__))
    log('## Add-on Name = %s' % str(__addonname__))
    log('## Authors     = %s' % str(__author__))
    log('## Version     = %s' % str(__version__))
    Main()
    log('script stopped')