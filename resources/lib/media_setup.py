import re
import xbmc
import urllib
import simplejson
from resources.lib.utils import _log as log

### get list of all tvshows and movies with their imdbnumber from library

def media_listing(media_type):
        if media_type == 'TVShows':
            log('Using JSON for retrieving info')
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%s", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}' % media_type)
            jsonobject = simplejson.loads(json_response)
            Medialist = []
            log('Checking for JSON results')
            if jsonobject['result'].has_key('tvshows'):
                log('Processing JSON objects')
                for item in jsonobject['result']['tvshows']:
                    Media = {}
                    Media['name'] = item['label']
                    Media['path'] = item['file']
                    Media['id'] = item['imdbnumber']
                    Media['tvshowid'] = item['tvshowid']
                    log('Media name: %s' %Media['name'])
                    log('Media path: %s' %Media['path'])
                    log('Media IMDB: %s' %Media['id'])
                    ### Search for season numbers
                    json_response_season = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetSeasons", "params": {"tvshowid":%s }, "id": 1}' %Media['tvshowid'])
                    log('JSON Respons seasons: %s' %json_response)
                    log('')
                    jsonobject_season = simplejson.loads(json_response_season)
                    log('JSON Object seasons: %s' %jsonobject_season)
                    log('')
                    if jsonobject_season['result'].has_key('label'):
                        for item in jsonobject_season['result']['label']:
                            log('')
                            Media['seasontotal'] = item['label']
                            log('Season total: %s' %Media['seasontotal'])
                            #Media['seasonstart'] = item['start']
                            #log('Season start: %s' %Media['seasonstart'])                            
                            #Media['seasonend'] = item['end']
                            #log('Season end: %s' %Media['seasonend'])
                    Medialist.append(Media)
        elif media_type == 'Movies':
            log('Using JSON for retrieving info')
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%s", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}' % media_type)
            jsonobject = simplejson.loads(json_response)
            Medialist = []
            log('Checking for JSON results')
            if jsonobject['result'].has_key('movies'):
                log('Processing JSON objects')
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