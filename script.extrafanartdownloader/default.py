import urllib
import urllib2
import re
import os
import xbmc
import xbmcaddon

Addon = xbmcaddon.Addon(id='script.extrafanartdownloader')
fanart_baseurl = 'http://www.thetvdb.com/banners/fanart/original/'

class EFDL:

    def __init__(self):

        self.fanart_count = 0
        xbmc.log('EFDL: Extrafanart Downloader initialising')
        xbmc.executebuiltin("XBMC.Notification('Extrafanart Downloader','Starting',5000)")

        if (xbmc.getCondVisibility('Library.IsScanningVideo')  == False):
            self.TV_listing()
            for currentshow in self.TVlist:
                self.failcount = 0
                self.show_path = currentshow["path"]
                self.tvdbid = currentshow["id"]
                self.show_name = currentshow["name"]
                extrafanart_dir = os.path.join(self.show_path, 'extrafanart')
                if not os.path.isdir(extrafanart_dir):
                    os.makedirs(extrafanart_dir)
                    xbmc.log('EFDL: Created extrafanart directory for %s: %s' % (self.show_name, extrafanart_dir))
                for i in range(1000):
                    if self.failcount < 3:
                        x = i + 1
                        fanartfile = self.tvdbid + '-' + str(x) + '.jpg'
                        fanarturl = fanart_baseurl + fanartfile
                        fanartpath = os.path.join(extrafanart_dir, fanartfile)
                        if not os.path.exists(fanartpath):
                            try:
                                urllib2.urlopen(fanarturl)
                            except:
                                self.failcount = self.failcount + 1
                            else:
                                urllib.urlretrieve(fanarturl, fanartpath)
                                self.failcount = 0
                                xbmc.log('EFDL: Downloaded fanart for %s: %s' % (self.show_name, fanarturl))
                                self.fanart_count = self.fanart_count + 1
                    else:
                        xbmc.log('EFDL: Processed \'%s\'' % self.show_name)
                        break
        else:
            xbmc.log('EFDL: Library Update is running: Aborting')
            xbmc.executebuiltin("XBMC.Notification('Extrafanart Downloader','Library Update is running: Aborting',5000)")

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
                    else:
                        imdbnumber = ''
                    TVshow = {}
                    TVshow["name"] = tvshowname
                    TVshow["id"] = imdbnumber
                    TVshow["path"] = path
                    self.TVlist.append(TVshow)


xbmc.executebuiltin('CancelAlarm(extrafanart)')

timer_amounts = {}
timer_amounts['0'] = '60'
timer_amounts['1'] = '180'
timer_amounts['2'] = '360'
timer_amounts['3'] = '720'
timer_amounts['4'] = '1440'

EFDLrun = EFDL()

xbmc.log('EFDL: Extrafanart Downloader finished: Script will run again in %s minutes' % timer_amounts[Addon.getSetting('timer_amount')])

if EFDLrun.fanart_count > 0:
    xbmc.executebuiltin("XBMC.Notification('Extrafanart Downloader','Finished: %s extrafanart downloaded',5000)" % EFDLrun.fanart_count)

xbmc.executebuiltin("XBMC.Notification('Extrafanart Downloader','Finished: Next run in %s minutes',3000)" % timer_amounts[Addon.getSetting('timer_amount')])

xbmc.executebuiltin('AlarmClock(extrafanart,XBMC.RunScript(script.extrafanartdownloader),' + timer_amounts[Addon.getSetting('timer_amount')] +  ',true)')
