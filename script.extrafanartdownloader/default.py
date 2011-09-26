import urllib, urllib2, re, os
import xbmc, xbmcaddon, xbmcvfs

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

def log(txt):
    message = 'script.extrafanartdownloader: %s' % txt
    xbmc.log(msg=message, level=xbmc.LOGNOTICE)

class Main:

    def __init__(self):
        self.load_settings()
        self.download_tvfanart()

    def load_settings(self):
        self.fanart_baseurl = 'http://www.thetvdb.com/banners/fanart/original/'
        self.fanart_count = 0
        self.timer_amounts = {}
        self.timer_amounts['0'] = '60'
        self.timer_amounts['1'] = '180'
        self.timer_amounts['2'] = '360'
        self.timer_amounts['3'] = '720'
        self.timer_amounts['4'] = '1440'

    def download_tvfanart(self):
        if (xbmc.getCondVisibility('Library.IsScanningVideo')  == True):
            log('library update is running: Aborting')
            xbmc.executebuiltin("XBMC.Notification(Extrafanart Downloader,Library update is running: Aborting,5000)")
        else:
            self.TV_listing()
            tempdir = xbmc.translatePath('special://profile/addon_data/%s/temp/' % __addonid__)
            if not xbmcvfs.exists(tempdir):
                xbmcvfs.mkdir(tempdir)
                log('Created temporary directory: %s' % tempdir)
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
                            try:
                                urllib2.urlopen(fanarturl)
                            except:
                                self.failcount = self.failcount + 1
                            else:
                                urllib.urlretrieve(fanarturl, temppath)
                                xbmcvfs.copy(temppath, fanartpath)
                                xbmcvfs.delete(temppath)
                                self.failcount = 0
                                log('Downloaded fanart: %s %s' % (self.show_name, fanarturl))
                                self.fanart_count = self.fanart_count + 1
                    else:
#                        log('Processed \'%s\'' % self.show_name)
                        break
            if xbmcvfs.exists(tempdir):
                xbmcvfs.rmdir(tempdir)
                log('Removed temporary directory: %s' % tempdir)
            xbmc.executebuiltin("XBMC.Notification(Extrafanart Downloader,Finished: %s extrafanart downloaded,5000)" % self.fanart_count)
            xbmc.executebuiltin('AlarmClock(extrafanart,XBMC.RunScript(script.extrafanartdownloader),' + self.timer_amounts[__addon__.getSetting('timer_amount')] +  ',true)')

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
    xbmc.executebuiltin("XBMC.Notification(Extrafanart Downloader,Starting,5000)")
    xbmc.executebuiltin('CancelAlarm(extrafanart)')
    Main()
    log('script stopped')
