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

# modules
import os
import time
import xbmc
import xbmcaddon
import xbmcvfs
import lib.common

### get addon info
ADDON         = lib.common.ADDON
ADDON_PATH    = lib.common.ADDON_PATH
ADDON_NAME    = lib.common.ADDON_NAME
ADDON_VERSION = lib.common.ADDON_VERSION
PROFILE_PATH  = lib.common.PROFILE_PATH
localize      = lib.common.localize

#import libraries
from lib.settings import get
from lib.utils import log
setting = get()

# starts update/sync
def autostart():
        xbmcaddon.Addon().setSetting(id="files_overwrite", value='false')
        tempdir = os.path.join(PROFILE_PATH, 'temp')
        service_runtime  = str(setting.get('service_runtime') + ':00')
        log('## Service - Run at startup: %s'% setting.get('service_startup'), xbmc.LOGNOTICE)        
        log('## Service - Delayed startup: %s minutes'% setting.get('service_startupdelay'), xbmc.LOGNOTICE)   
        log('## Service - Run as service: %s'% setting.get('service_enable'), xbmc.LOGNOTICE)
        log('## Service - Time: %s'% service_runtime, xbmc.LOGNOTICE)
        log("##########........................")
        # Check if tempdir exists and remove it
        if xbmcvfs.exists(tempdir):
            xbmcvfs.rmdir(tempdir)
            log('Removing temp folder from previous aborted run.')
            xbmc.sleep(5000)
        # Run script when enabled and check on existence of tempdir.
        # This because it is possible that script was running even when we previously deleted it.
        # Could happen when switching profiles and service gets triggered again
        if setting.get('service_startup') and not xbmcvfs.exists(tempdir):
            xbmc.executebuiltin('XBMC.AlarmClock(ArtworkDownloader,XBMC.RunScript(script.artwork.downloader,silent=true),00:%s:15,silent)' % setting.get('setting.service_startupdelay')) 
        if setting.get('service_enable'):
            while (not xbmc.abortRequested):
                xbmc.sleep(5000)
                if not(time.strftime('%H:%M') == service_runtime):
                    pass
                else:
                    if not xbmcvfs.exists(tempdir):
                        log('Time is %s:%s, Scheduled run starting' % (time.strftime('%H'), time.strftime('%M')))
                        xbmc.executebuiltin('XBMC.RunScript(script.artwork.downloader,silent=true)')
                        # Because we now use the commoncache module the script is run so fast it is possible it is started twice
                        # within the one minute window. So keep looping until it goes out of that window
                        while (not xbmc.abortRequested and time.strftime('%H:%M') == service_runtime):
                            xbmc.sleep(5000)
                    else:
                        log('Addon already running, scheduled run aborted', xbmc.LOGNOTICE)

if (__name__ == "__main__"):
    log("######## Artwork Downloader Service: Initializing........................")
    log('## Add-on Name = %s' % str(ADDON_NAME))
    log('## Version     = %s' % str(ADDON_VERSION))
    autostart()