import urllib
import re
import os
import xbmc
import xbmcaddon

Addon = xbmcaddon.Addon(id='script.extrafanartdownloader')

class Main:

    def __init__(self):

        xbmc.executebuiltin('CancelAlarm(extrafanart)')

        timer_amounts = {}
        timer_amounts['0'] = '60'
        timer_amounts['1'] = '180'
        timer_amounts['2'] = '360'
        timer_amounts['3'] = '720'
        timer_amounts['4'] = '1440'

        if(xbmc.Player().isPlaying() == False):
            if (xbmc.getCondVisibility('Library.IsScanningVideo')  == False):
                self.TV_listing()
                for currentshow in self.TVlist:
                    self.show_path = currentshow["path"]
                    self.tvdbid = currentshow["id"]
                    self.show_name = currentshow["name"]
                    logmessage = self.show_name + ' ' + self.tvdbid + ' ' + self.show_path
                    xbmc.log(logmessage)
                    xbmc.log('testy test')
                    xbmc.executebuiltin(AlarmClock(extrafanart,XBMC.RunScript(script.extrafanartdownloader), timer_amounts[Addon.getSetting('timer_amount')], true))

    def TV_listing(self):
        # json statement for tv shows
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"fields": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}')
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

#run the program
run_program = Main()
             
