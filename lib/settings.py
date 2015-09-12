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
import xbmc
import xbmcaddon
import lib.common
from lib.gui import dialog_msg
from lib.utils import log

### get addon info
ADDON         = lib.common.ADDON
localize      = lib.common.localize

### General seetting variables
def get():
    setting = {'failcount':                0,     # Initial fail count
               'failthreshold':            3,     # Abbort when this many fails
               'xmlfailthreshold':         5,     # Abbort when this many fails
               'api_timedelay':            5000,  # in msec

               'centralize_enable':        ADDON.getSetting("centralize_enable")      == 'true',
               'centralfolder_movies':     ADDON.getSetting("centralfolder_movies"),
               'centralfolder_tvshows':    ADDON.getSetting("centralfolder_tvshows"),
               'background':               ADDON.getSetting("background")             == 'true',
               'notify':                   ADDON.getSetting("notify")                 == 'true',
               'service_startup':          ADDON.getSetting("service_startup")        == 'true',
               'service_startupdelay':     ADDON.getSetting("service_startupdelay"),
               'service_enable':           ADDON.getSetting("service_enable")         == 'true',
               'service_runtime':          ADDON.getSetting("service_runtime"),
               'files_overwrite':          ADDON.getSetting("files_overwrite")        == 'true',
               'files_local':              ADDON.getSetting("files_local")            == 'true',
               'xbmc_caching_enabled':     ADDON.getSetting("xbmc_caching_enabled")   == 'true',
               'debug_enabled':            ADDON.getSetting("debug_enabled")          == 'true',
               'service_startup':          False,
               'service_enable':           False,

               'movie_enable':             ADDON.getSetting("movie_enable")           == 'true',
               'movie_poster':             ADDON.getSetting("movie_poster")           == 'true',
               'movie_fanart':             ADDON.getSetting("movie_fanart")           == 'true',
               'movie_extrafanart':        ADDON.getSetting("movie_extrafanart")      == 'true',
               'movie_extrathumbs':        ADDON.getSetting("movie_extrathumbs")      == 'true',
               'movie_logo':               ADDON.getSetting("movie_logo")             == 'true',
               'movie_clearart':           ADDON.getSetting("movie_clearart")         == 'true',
               'movie_discart':            ADDON.getSetting("movie_discart")          == 'true',
               'movie_landscape':          ADDON.getSetting("movie_landscape")        == 'true',
               'movie_banner':             ADDON.getSetting("movie_banner")           == 'true',

               'tvshow_enable':            ADDON.getSetting("tvshow_enable")          == 'true',
               'tvshow_poster':            ADDON.getSetting("tvshow_poster")          == 'true',
               'tvshow_seasonposter':      ADDON.getSetting("tvshow_seasonposter")    == 'true',
               'tvshow_fanart':            ADDON.getSetting("tvshow_fanart")          == 'true',
               'tvshow_extrafanart':       ADDON.getSetting("tvshow_extrafanart")     == 'true',
               'tvshow_clearart':          ADDON.getSetting("tvshow_clearart")        == 'true',
               'tvshow_logo':              ADDON.getSetting("tvshow_logo")            == 'true',
               'tvshow_landscape':         ADDON.getSetting("tvshow_landscape")       == 'true',
               'tvshow_seasonlandscape':   ADDON.getSetting("tvshow_seasonlandscape") == 'true',
               'tvshow_showbanner':        ADDON.getSetting("tvshow_showbanner")      == 'true',
               'tvshow_seasonbanner':      ADDON.getSetting("tvshow_seasonbanner")    == 'true',
               'tvshow_characterart':      ADDON.getSetting("tvshow_characterart")    == 'true',

               'musicvideo_enable':        ADDON.getSetting("musicvideo_enable")     == 'true',
               'musicvideo_poster':        ADDON.getSetting("musicvideo_poster")     == 'true',
               'musicvideo_fanart':        ADDON.getSetting("musicvideo_fanart")     == 'true',
               'musicvideo_extrafanart':   ADDON.getSetting("musicvideo_extrafanart")== 'true',
               'musicvideo_extrathumbs':   ADDON.getSetting("musicvideo_extrathumbs")== 'true',
               'musicvideo_logo':          ADDON.getSetting("musicvideo_logo")       == 'true',
               'musicvideo_clearart':      ADDON.getSetting("musicvideo_clearart")   == 'true',
               'musicvideo_discart':       ADDON.getSetting("musicvideo_discart")    == 'true'}
    return setting

def get_limit():
    setting = {'limit_artwork':            ADDON.getSetting("limit_artwork")          == "true",
               'limit_extrafanart_max':    (float(ADDON.getSetting("limit_extrafanart_maximum"))),
               'limit_extrafanart_rating': int(float(ADDON.getSetting("limit_extrafanart_rating"))),
               'limit_size_moviefanart':   int(ADDON.getSetting("limit_size_moviefanart")),
               'limit_size_tvshowfanart':  int(ADDON.getSetting("limit_size_tvshowfanart")),
               'limit_extrathumbs':        True,
               'limit_extrathumbs_max':    4,
               'limit_artwork_max':        1,
               'limit_preferred_language': ADDON.getSetting("limit_preferred_language"),
               'limit_notext':             ADDON.getSetting("limit_notext")           == 'true'}
    return setting
    
### Check for faulty setting combinations
def check():
    setting = get()
    settings_faulty = True
    while settings_faulty:
        settings_faulty = True
        check_movie = check_tvshow = check_musicvideo = check_centralize = True
        # re-check settings after posible change
        setting = get()
        # Check if faulty setting in movie section
        if setting.get('movie_enable'):
            if not setting.get('movie_poster') and not setting.get('movie_fanart') and not setting.get('movie_extrafanart') and not setting.get('movie_extrathumbs') and not setting.get('movie_logo') and not setting.get('movie_clearart') and not setting.get('movie_discart') and not setting.get('movie_landscape') and not setting.get('movie_banner'):
                check_movie = False
                log('Setting check: No subsetting of movies enabled')
            else: check_movie = True
        # Check if faulty setting in tvshow section
        if setting.get('tvshow_enable'):
            if not setting.get('tvshow_poster') and not setting.get('tvshow_seasonposter') and not setting.get('tvshow_fanart') and not setting.get('tvshow_extrafanart') and not setting.get('tvshow_clearart') and not setting.get('tvshow_characterart') and not setting.get('tvshow_logo') and not setting.get('tvshow_showbanner') and not setting.get('tvshow_seasonbanner') and not setting.get('tvshow_landscape') and not setting.get('tvshow_seasonlandscape'):
                check_tvshow = False
                log('Setting check: No subsetting of tv shows enabled')
            else: check_tvshow = True
        # Check if faulty setting in musicvideo section
        if setting.get('musicvideo_enable'):
            if not setting.get('musicvideo_poster') and not setting.get('musicvideo_fanart') and not setting.get('musicvideo_extrafanart') and not setting.get('musicvideo_extrathumbs') and not setting.get('musicvideo_logo') and not setting.get('musicvideo_clearart') and not setting.get('musicvideo_discart'):
                check_musicvideo = False
                log('Setting check: No subsetting of musicvideo enabled')
            else: check_musicvideo = True
        # Check if faulty setting in centralize section
        if setting.get('centralize_enable'):
            if setting.get('centralfolder_movies') == '' and setting.get('centralfolder_tvshows') == '':
                check_centralize = False
                log('Setting check: No centralized folder chosen')
            else: check_centralize = True
        # Compare all setting check
        if check_movie and check_tvshow and check_musicvideo and check_centralize:
            settings_faulty = False
        else: settings_faulty = True
        # Faulty setting found
        if settings_faulty:
            log('Faulty setting combination found')
            # when faulty setting detected ask to open the settings window
            if dialog_msg('yesno', line1 = localize(32003), line2 = localize(32004), background = False, nolabel = localize(32026), yeslabel = localize(32025)):
                ADDON.openSettings()
            # if not cancel the script
            else:
                return False
        else:
            return True
