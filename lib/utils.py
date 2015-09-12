#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2011-2014 Martijn Kaijser
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

#import modules
import lib.common
import socket
import xbmc
import xbmcgui
import unicodedata
import urllib2
import sys

# Use json instead of simplejson when python v2.7 or greater
if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json
# Commoncache plugin import
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

### import libraries
from lib.script_exceptions import *
from urllib2 import HTTPError, URLError

### get addon info
ADDON         = lib.common.ADDON
ADDON_NAME    = lib.common.ADDON_NAME
ADDON_ICON    = lib.common.ADDON_ICON
localize      = lib.common.localize

cache = StorageServer.StorageServer("ArtworkDownloader",240)

### Adjust default timeout to stop script hanging
socket.setdefaulttimeout(20)
### Cache bool
CACHE_ON = True

# Fixes unicode problems
def string_unicode(text, encoding='utf-8'):
    try:
        text = unicode( text, encoding )
    except:
        pass
    return text

def normalize_string(text):
    try:
        text = unicodedata.normalize('NFKD', string_unicode(text)).encode('ascii', 'ignore')
    except:
        pass
    return text

# Define log messages
def log(txt, severity=xbmc.LOGDEBUG):
    if severity == xbmc.LOGDEBUG and not ADDON.getSetting("debug_enabled") == 'true':
        pass
    else:
        try:
            message = ('%s: %s' % (ADDON_NAME,txt) )
            xbmc.log(msg=message, level=severity)
        except UnicodeEncodeError:
            try:
                message = normalize_string('%s: %s' % (ADDON_NAME,txt) )
                xbmc.log(msg=message, level=severity)
            except:
                message = ('%s: UnicodeEncodeError' %ADDON_NAME)
                xbmc.log(msg=message, level=xbmc.LOGWARNING)


# Retrieve JSON data from cache function
def get_data(url, data_type ='json'):
    log('API: %s'% url)
    if CACHE_ON:
        result = cache.cacheFunction(get_data_new, url, data_type)
    else:
        result = get_data_new(url, data_type)    
    if not result:
        result = 'Empty'
    return result

# Retrieve JSON data from site
def get_data_new(url, data_type):
    log('Cache expired. Retrieving new data')
    data = []
    try:
        request = urllib2.Request(url)
        # TMDB needs a header to be able to read the data
        if url.startswith("http://api.themoviedb.org"):
            request.add_header("Accept", "application/json")
        req = urllib2.urlopen(request)
        if data_type == 'json':
            data = json.loads(req.read())
            if not data:
                data = 'Empty'
        else:
            data = req.read()
        req.close()
    except HTTPError, e:
        if e.code == 400:
            raise HTTP400Error(url)
        elif e.code == 404:
            raise HTTP404Error(url)
        elif e.code == 503:
            raise HTTP503Error(url)
        else:
            raise DownloadError(str(e))
    except URLError:
        raise HTTPTimeout(url)
    except socket.timeout, e:
        raise HTTPTimeout(url)
    except:
        data = 'Empty'
    return data

# Clean filenames for illegal character in the safest way for windows
def clean_filename(filename):
    illegal_char = '<>:"/\|?*'
    for char in illegal_char:
        filename = filename.replace( char , '' )
    return filename

def save_nfo_file(data, target):
    try:
        # open source path for writing and write xmlSource
        file_object = open(target.encode("utf-8"), "w")
        file_object.write(data.encode( "utf-8" ))
        file_object.close()
        return True
    except Exception, e:
        log(str(e), xbmc.LOGERROR)
        return False

def get_abbrev(lang_string):
    try:
        language_abbrev = xbmc.convertLanguage(lang_string, xbmc.ISO_639_1)
    except:
        language_abbrev = 'en' ### Default to English if conversion fails
    return language_abbrev
        
def get_language(abbrev):
    try:
        lang_string = xbmc.convertLanguage(abbrev, xbmc.ENGLISH_NAME)
    except:
        lang_string = 'n/a'
    return lang_string