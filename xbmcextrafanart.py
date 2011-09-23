import urllib
import re
import xbmc
import xbmcaddon
    
class Main:
    def __init__(self):
        self.TV_listing()

        for currentshow in self.TVlist:
            self.show_path = currentshow["path"]
            self.tvdbid = currentshow["id"]
            self.show_name = currentshow["name"]

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

run_program = Main()
