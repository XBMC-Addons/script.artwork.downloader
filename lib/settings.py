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
import os
import xbmcgui
import sys
import lib.common

### get addon info
__addon__        = lib.common.__addon__
                    
def get_limit():
    setting = {'limit_artwork': __addon__.getSetting("limit_artwork") == "true",
               'limit_extrafanart_max': (float(__addon__.getSetting("limit_extrafanart_maximum"))),
               'limit_extrafanart_rating': int(float(__addon__.getSetting("limit_extrafanart_rating"))),
               'limit_size_moviefanart': int(__addon__.getSetting("limit_size_moviefanart")),
               'limit_size_tvshowfanart': int(__addon__.getSetting("limit_size_tvshowfanart")),
               'limit_extrathumbs': True,
               'limit_extrathumbs_max': 4,
               'limit_artwork_max': 1,
               'limit_preferred_language': __addon__.getSetting("limit_preferred_language"),
               'limit_notext': __addon__.getSetting("limit_notext") == 'true'}
    return setting