import urllib, urllib2, re, os, socket
import xbmc, xbmcaddon, xbmcvfs, xbmcgui
from xml.etree import ElementTree

### get addon info
__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

### adjust default timeout to stop script hanging
timeout = 20
socket.setdefaulttimeout(timeout)

### logging function
def log(txt):
    message = 'script.extrafanartdownloader: %s' % txt
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

### TMDB API wrapper
### Thanks to globald
### http://forums.themoviedb.org/topic/1092/my-contribution-tmdb-api-wrapper-python/
class TMDB(object):

    def __init__(self, api_key, view='xml', lang='en'):
        ''' TMDB Client '''
        #view = yaml json xml
        self.lang = lang
        self.view = view
        self.key = api_key
        self.server = 'http://api.themoviedb.org'

    def socket(self, url):
        ''' Return URL Content '''

        data = None
        try:
            client = urllib.urlopen(url)
            data = client.read()
            client.close()
        except: pass
        return data

    def method(self, look, term):
        ''' Methods => search, imdbLookup, getInfo, getImages'''

        do = 'Movie.'+look
        term = str(term) # int conversion
        run = self.server+'/2.1/'+do+'/'+self.lang+'/'+self.view+'/'+self.key+'/'+term
        return run

    def tmdbImages(self, tmdb_Id):
        ''' GetInfo Wrapper '''
        return self.socket(self.method('getImages',tmdb_Id))

class Main:

    def __init__(self):
        self.load_settings()
        if self.tvfanart == 'true':
            self.download_tvfanart()
        else:
            log('TV fanart disabled, skipping')

    ### load settings and initial values
    def load_settings(self):
        self.fanart_baseurl = 'http://www.thetvdb.com/banners/fanart/original/'
        self.fanart_count = 0
        self.moviefanart = __addon__.getSetting("moviefanart")
        self.tvfanart = __addon__.getSetting("tvfanart")
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create(__addonname__, 'Checking for extrafanart')
        self.processeditems = 0

    ### download all tv show fanart
    def download_tvfanart(self):
        self.TV_listing()
        addondir = xbmc.translatePath('special://profile/addon_data/%s' % __addonid__)
        tempdir = os.path.join(addondir, 'temp')
        try:
            if not xbmcvfs.exists(tempdir):
                if not xbmcvfs.exists(addondir):
                    xbmcvfs.mkdir(addondir)
                    log('Created addon directory: %s' % addondir)
                xbmcvfs.mkdir(tempdir)
                log('Created temporary directory: %s' % tempdir)
        except:
            log('Could not create temporary directory: %s' % tempdir)
        else:
            for currentshow in self.TVlist:
                ### check if XBMC is shutting down
                if xbmc.abortRequested == True:
                    log('XBMC shutting down, aborting')
                    break
                ### check if script has been cancelled by user
                if self.dialog.iscanceled():
                    self.dialog.close()
                    break
                self.failcount = 0
                self.show_path = currentshow["path"]
                self.tvdbid = currentshow["id"]
                self.show_name = currentshow["name"]
                self.dialog.update(int(float(self.processeditems) / float(len(self.TVlist)) * 100), 'Checking for extrafanart', self.show_name)
                log('Processing show: %s' % self.show_name)
                extrafanart_dir = os.path.join(self.show_path, 'extrafanart')
                if not xbmcvfs.exists(extrafanart_dir):
                    xbmcvfs.mkdir(extrafanart_dir)
                    log('Created directory: %s' % extrafanart_dir)
                for i in range(1000):
                    if self.failcount < 3:
                        x = i + 1
                        fanartfile = self.tvdbid + '-' + str(x) + '.jpg'
                        fanarturl = self.fanart_baseurl + fanartfile
                        temppath = os.path.join(tempdir, fanartfile)
                        fanartpath = os.path.join(extrafanart_dir, fanartfile)
                        if not xbmcvfs.exists(fanartpath):
                            ### check if fanart exists on tvdb
                            try:
                                urllib2.urlopen(fanarturl)
                            except:
                                self.failcount = self.failcount + 1
                            else:
                                self.dialog.update(int(float(self.processeditems) / float(len(self.TVlist)) * 100), 'Downloading extrafanart', self.show_name, fanarturl)
                                log('Downloading fanart: %s' % fanarturl)
                                ### download fanart to temp path
                                try:
                                    urllib.urlretrieve(fanarturl, temppath)
                                except(socket.timeout):
                                    log('Download timed out, skipping: %s' % fanarturl)
                                    self.failcount = self.failcount + 1
                                except:
                                    log('Download failed, skipping: %s' % fanarturl)
                                    self.failcount = self.failcount + 1
                                else:
                                    ### copy fanart from temp path to library
                                    xbmcvfs.copy(temppath, fanartpath)
                                    if not xbmcvfs.exists(fanartpath):
                                        log('Error copying temp file to library: %s -> %s' % (temppath, fanartpath))
                                    else:
                                        self.failcount = 0
                                        log('Downloaded successfully: %s' % fanarturl)
                                        self.fanart_count = self.fanart_count + 1
                    else:
                        self.processeditems = self.processeditems + 1
                        break
            ### clean up
            if xbmcvfs.exists(tempdir):
                self.dialog.update(100, 'Cleaning up')
                log('Cleaning up')
                for x in os.listdir(tempdir):
                    tempfile = os.path.join(tempdir, x)
                    xbmcvfs.delete(tempfile)
                    if xbmcvfs.exists(tempfile):
                        log('Error deleting temp file: %s' % tempfile)
                    else:
                        log('Deleted temp file: %s' % tempfile)
                xbmcvfs.rmdir(tempdir)
                if xbmcvfs.exists(tempdir):
                    log('Error deleting temp directory: %s' % tempdir)
                else:
                    log('Deleted temp directory: %s' % tempdir)
            ### log results and notify user
            log('Finished: %s extrafanart downloaded' % self.fanart_count)
            summary = 'Finished: %s extrafanart downloaded' % self.fanart_count
            self.dialog.close()
            xbmcgui.Dialog().ok(__addonname__, summary)

    ### get list of all tvshows and their imdbnumber from library
    ### copied from script.logo-downloader, thanks to it's authors
    def TV_listing(self):
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}')
        json_response = re.compile( "{(.*?)}", re.DOTALL ).findall(json_query)
        self.TVlist = []
        for tvshowitem in json_response:
            findtvshowname = re.search( '"label":"(.*?)","', tvshowitem )
            if findtvshowname:
                tvshowname = ( findtvshowname.group(1) )
                findpath = re.search( '"file":"(.*?)","', tvshowitem )
                if findpath:
                    path = (findpath.group(1))
                    findimdbnumber = re.search( '"imdbnumber":"(.*?)","', tvshowitem )
                    if findimdbnumber:
                        imdbnumber = (findimdbnumber.group(1))
                        TVshow = {}
                        TVshow["name"] = tvshowname
                        TVshow["id"] = imdbnumber
                        TVshow["path"] = path
                        self.TVlist.append(TVshow)

if ( __name__ == "__main__" ):
    log('script version %s started' % __addonversion__)
    Main()
    log('script stopped')
