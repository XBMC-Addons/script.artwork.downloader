#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2011-2013 Martijn Kaijser
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
import xbmc
import xbmcaddon
import lib.common

### get addon info
__addon__        = lib.common.__addon__

    ### Initial genral vars
def get():
    setting = {'failcount':                0,     # Initial fail count
               'failthreshold':            3,     # Abbort when this many fails
               'xmlfailthreshold':         5,     # Abbort when this many fails
               'api_timedelay':            5000,  # in msec

               'centralize_enable':        __addon__.getSetting("centralize_enable")      == 'true',
               'centralfolder_movies':     __addon__.getSetting("centralfolder_movies"),
               'centralfolder_tvshows':    __addon__.getSetting("centralfolder_tvshows"),
               'background':               __addon__.getSetting("background")             == 'true',
               'notify':                   __addon__.getSetting("notify")                 == 'true',
               'service_startup':          __addon__.getSetting("service_startup")        == 'true',
               'service_startupdelay':     __addon__.getSetting("service_startupdelay"),
               'service_enable':           __addon__.getSetting("service_enable")         == 'true',
               'service_runtime':          __addon__.getSetting("service_runtime"),
               'files_overwrite':          __addon__.getSetting("files_overwrite")        == 'true',
               'files_local':              __addon__.getSetting("files_local")            == 'true',
               'xbmc_caching_enabled':     __addon__.getSetting("xbmc_caching_enabled")   == 'true',
               'debug_enabled':            __addon__.getSetting("debug_enabled")          == 'true',
               'service_startup':          False,
               'service_enable':           False,

               'movie_enable':             __addon__.getSetting("movie_enable")           == 'true',
               'movie_poster':             __addon__.getSetting("movie_poster")           == 'true',
               'movie_fanart':             __addon__.getSetting("movie_fanart")           == 'true',
               'movie_extrafanart':        __addon__.getSetting("movie_extrafanart")      == 'true',
               'movie_extrathumbs':        __addon__.getSetting("movie_extrathumbs")      == 'true',
               'movie_logo':               __addon__.getSetting("movie_logo")             == 'true',
               'movie_clearart':           __addon__.getSetting("movie_clearart")         == 'true',
               'movie_discart':            __addon__.getSetting("movie_discart")          == 'true',
               'movie_landscape':          __addon__.getSetting("movie_landscape")        == 'true',
               'movie_banner':             __addon__.getSetting("movie_banner")           == 'true',

               'tvshow_enable':            __addon__.getSetting("tvshow_enable")          == 'true',
               'tvshow_poster':            __addon__.getSetting("tvshow_poster")          == 'true',
               'tvshow_seasonposter':      __addon__.getSetting("tvshow_seasonposter")    == 'true',
               'tvshow_fanart':            __addon__.getSetting("tvshow_fanart")          == 'true',
               'tvshow_extrafanart':       __addon__.getSetting("tvshow_extrafanart")     == 'true',
               'tvshow_clearart':          __addon__.getSetting("tvshow_clearart")        == 'true',
               'tvshow_logo':              __addon__.getSetting("tvshow_logo")            == 'true',
               'tvshow_landscape':         __addon__.getSetting("tvshow_landscape")       == 'true',
               'tvshow_seasonlandscape':   __addon__.getSetting("tvshow_seasonlandscape") == 'true',
               'tvshow_showbanner':        __addon__.getSetting("tvshow_showbanner")      == 'true',
               'tvshow_seasonbanner':      __addon__.getSetting("tvshow_seasonbanner")    == 'true',
               'tvshow_characterart':      __addon__.getSetting("tvshow_characterart")    == 'true',

               'musicvideo_enable':        __addon__.getSetting("musicvideo_enable")     == 'true',
               'musicvideo_poster':        __addon__.getSetting("musicvideo_poster")     == 'true',
               'musicvideo_fanart':        __addon__.getSetting("musicvideo_fanart")     == 'true',
               'musicvideo_extrafanart':   __addon__.getSetting("musicvideo_extrafanart")== 'true',
               'musicvideo_extrathumbs':   __addon__.getSetting("musicvideo_extrathumbs")== 'true',
               'musicvideo_logo':          __addon__.getSetting("musicvideo_logo")       == 'true',
               'musicvideo_clearart':      __addon__.getSetting("musicvideo_clearart")   == 'true',
               'musicvideo_discart':       __addon__.getSetting("musicvideo_discart")    == 'true'}
    return setting

def get_limit():
    setting = {'limit_artwork':            __addon__.getSetting("limit_artwork")          == "true",
               'limit_extrafanart_max':    (float(__addon__.getSetting("limit_extrafanart_maximum"))),
               'limit_extrafanart_rating': int(float(__addon__.getSetting("limit_extrafanart_rating"))),
               'limit_size_moviefanart':   int(__addon__.getSetting("limit_size_moviefanart")),
               'limit_size_tvshowfanart':  int(__addon__.getSetting("limit_size_tvshowfanart")),
               'limit_extrathumbs':        True,
               'limit_extrathumbs_max':    4,
               'limit_artwork_max':        1,
               'limit_preferred_language': __addon__.getSetting("limit_preferred_language"),
               'limit_notext':             __addon__.getSetting("limit_notext")           == 'true'}
    return setting