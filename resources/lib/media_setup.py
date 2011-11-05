import re
import xbmc
import urllib
import simplejson

def log(txt, severity=xbmc.LOGDEBUG):
    try:
        """Log to txt xbmc.log at specified severity"""
        message = 'script.extrafanartdownloader: %s' % txt
        xbmc.log(msg=message, level=severity)
    except:
        log('ASCII error')

### get list of all tvshows and movies with their imdbnumber from library
### copied from script.logo-downloader, thanks to it's authors
def media_listing(media_type):
        if media_type == 'TVShows':
            log('Using JSON for retrieving info')
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%s", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}' % media_type)
            #log('JSON Respons: %s' %json_response)
            #log('')
            jsonobject = simplejson.loads(json_response)
            #log('JSON Object: %s' %jsonobject)
            #log('')
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
                    #log('Media name: %s' %Media['name'])
                    #log('Media path: %s' %Media['path'])
                    #log('Media IMDB: %s' %Media['id'])
                    Medialist.append(Media)
        elif media_type == 'Movies':
            log('Using JSON for retrieving info')
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%s", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}' % media_type)
            #log('JSON Respons: %s' %json_response)
            #log('')
            jsonobject = simplejson.loads(json_response)
            #log('JSON Object: %s' %jsonobject)
            #log('')
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
                    #log('Media name: %s' %Media['name'])
                    #log('Media path: %s' %Media['path'])
                    #log('Media IMDB: %s' %Media['id'])
                    Medialist.append(Media)
        else:
            log('No results found')
        return Medialist
