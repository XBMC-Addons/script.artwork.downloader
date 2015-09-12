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
import os
import time
from lib.utils import save_nfo_file

PROFILE_PATH  = lib.common.PROFILE_PATH
localize      = lib.common.localize

def create_report(data, download_counter, failed_items):
    # Download totals to log and to download report
    data += ('\n - %s: %s' %(localize(32148), time.strftime('%d %B %Y - %H:%M')))      # Time of finish
    data += ('\n[B]%s:[/B]' %(localize(32020)))                                        # Download total header
    data += ('\n - %s: %s' % (localize(32014), download_counter['Total Artwork']))# Total downloaded items
    # Cycle through the download totals
    for artwork_type in download_counter:
        if not artwork_type == 'Total Artwork':
            data += '\n - %s: %s' % (artwork_type, download_counter[artwork_type])
    data += '\n[B]%s:[/B]' %localize(32016)                                              # Failed items header
    # Cycle through the download totals
    if not failed_items:
        data += '\n - %s' %localize(32149)                                               # No failed or missing items found
    else:
        # use  list(sorted(set(mylist)))  to get unique items
        for item in list(sorted(set(failed_items))):
            data += '\n - %s' %item
    save_nfo_file(data, os.path.join(PROFILE_PATH , 'downloadreport.txt'))
