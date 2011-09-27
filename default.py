import urllib, urllib2, re, os, socket
import xbmc, xbmcaddon, xbmcvfs

### get addon info
__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

### adjust default timeout to stop script hanging
timeout = 10
socket.setdefaulttimeout(timeout)

### logging function
def log(txt):
    message = 'script.extrafanartdownloader: %s' % txt
    xbmc.log(msg=message, level=xbmc.LOGNOTICE)

class Main:

    def __init__(self):
        self.load_settings()
        xbmc.executebuiltin("XBMC.Notification(Extrafanart Downloader,Starting,5000)")
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

    ### download all tv show fanart
    def download_tvfanart(self):
        self.TV_listing()
        tempdir = xbmc.translatePath('special://profile/addon_data/%s/temp/' % __addonid__)
        try:
            if not xbmcvfs.exists(tempdir):
                xbmcvfs.mkdir(tempdir)
                log('Created temporary directory: %s' % tempdir)
        except:
            log('Could not create temporary directory: %s' % tempdir)
        else:
            for currentshow in self.TVlist:
                self.failcount = 0
                self.show_path = currentshow["path"]
                self.tvdbid = currentshow["id"]
                self.show_name = currentshow["name"]
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
                                ### download fanart to temp path
                                try:
                                    urllib.urlretrieve(fanarturl, temppath)
                                except:
                                    log('Download failed, skipping: %s %s' % (self.show_name, fanarturl))
                                    self.failcount = self.failcount + 1
                                else:
                                    ### copy fanart from temp path to library
                                    try:
                                        copy = xbmcvfs.copy(temppath, fanartpath)
                                    except:
                                        log('Error copying temp file to library: %s -> %s' % (temppath, fanartpath))
                                        return False
                                    else:
                                        ### delete temporary file if copy was successful
                                        try:
                                            xbmcvfs.delete(temppath)
                                        except:
                                            log('Error deleting temp file: %s' % temppath)
                                            return False
                                        self.failcount = 0
                                        log('Downloaded fanart: %s %s' % (self.show_name, fanarturl))
                                        self.fanart_count = self.fanart_count + 1
                    else:
                        break
            ### remove temporary directory
            if xbmcvfs.exists(tempdir):
                xbmcvfs.rmdir(tempdir)
                log('Removed temporary directory: %s' % tempdir)
            ### log results and notify user
            log('Finished: %s extrafanart downloaded' % self.fanart_count)
            xbmc.executebuiltin("XBMC.Notification(Extrafanart Downloader,Finished: %s extrafanart downloaded,5000)" % self.fanart_count)

    ### get list of all tvshows and their imdbnumber from library
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
