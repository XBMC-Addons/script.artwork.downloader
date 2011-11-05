import re
import xbmc
import urllib
import simplejson
from resources.lib.utils import _log as log

### get list of all tvshows and movies with their imdbnumber from library

def media_listing(media_type):
        if media_type == 'TVShows':
            log('Using JSON for retrieving TV Show info')
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%s", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}' % media_type)
            jsonobject = simplejson.loads(json_response)
            Medialist = []
            if jsonobject['result'].has_key('tvshows'):
                for item in jsonobject['result']['tvshows']:
                    Media = {}
                    Media['name'] = item['label']
                    Media['path'] = item['file']
                    Media['id'] = item['imdbnumber']
                    Media['tvshowid'] = item['tvshowid']
                    ### Search for season numbers
                    json_response_season = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetSeasons", "params": {"tvshowid":%s }, "id": 1}' %Media['tvshowid'])
                    jsonobject_season = simplejson.loads(json_response_season)
                    if jsonobject_season['result'].has_key('limits'):
                        limits = jsonobject_season['result']['limits']
                        Media['seasontotal'] = limits['total']
                        Media['seasonstart'] = limits['start']
                        Media['seasonend'] = limits['end']
                    Medialist.append(Media)
        elif media_type == 'Movies':
            log('Using JSON for retrieving: Movie info')
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%s", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}' % media_type)
            jsonobject = simplejson.loads(json_response)
            Medialist = []
            if jsonobject['result'].has_key('movies'):
                for item in jsonobject['result']['movies']:
                    Media = {}
                    Media['name'] = item['label']
                    Media['path'] = item['file']
                    Media['id'] = item['imdbnumber']
                    Media['movieid'] = item['movieid']
                    Medialist.append(Media)
        else:
            log('No results found')
        return Medialist