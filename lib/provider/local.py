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
import sys
import os
import urllib
import xbmcvfs

### import libraries
#from resources.lib.provider.base import BaseProvider
from lib.art_list import arttype_list
from lib.script_exceptions import NoFanartError
from lib.settings import get_limit
from lib.utils import *
from operator import itemgetter

### get addon info
localize      = ( sys.modules[ "__main__" ].localize )
arttype_list = arttype_list()
limit = get_limit()

class local():
    def get_image_list(self,media_item):
        force_update = False
        image_list = []
        missing_arttypes =[]
        file_list = xbmcvfs.listdir(media_item['artworkdir'][0])
        ### Processes the bulk mode downloading of files
        i = 0 # needed
        j = 0 # have
        for item in arttype_list:
            if item['bulk_enabled'] and media_item['mediatype'] == item['media_type']:
                #log('finding: %s, arttype counter: %s'%(item['art_type'], i))
                i += 1
                # File checking
                if item['art_type'] == 'extrafanart':
                    extrafanart_file_list = ''
                    if 'extrafanart' in file_list[0]:
                        extrafanart_file_list = xbmcvfs.listdir(media_item['extrafanartdirs'][0])
                        #log('list of extrafanart files: %s'%extrafanart_file_list[1])
                        #log('extrafanart found: %s'%len(extrafanart_file_list[1]))
                        if len(extrafanart_file_list[1]) >= limit.get('limit_extrafanart_max'):
                            j += 1
                        else:
                            missing_arttypes.append(item['art_type'])

                elif item['art_type'] == 'extrathumbs':
                    extrathumbs_file_list = ''
                    if 'extrathumbs' in file_list[0]:
                        extrathumbs_file_list = xbmcvfs.listdir(media_item['extrathumbsdirs'][0])
                        #log('list of extrathumbs files: %s'%extrathumbs_file_list[1])
                        #log('extrathumbs found: %s'%len(extrathumbs_file_list[1]))
                        if len(extrathumbs_file_list[1]) >= limit.get('limit_extrathumbs_max'):
                            j += 1
                        else:
                            missing_arttypes.append(item['art_type'])

                elif item['art_type'] in ['seasonposter']:
                    for season in media_item['seasons']:
                        if season == '0':
                            filename = "season-specials-poster.jpg"
                        elif season == 'all':
                            filename = "season-all-poster.jpg"
                        else:
                            filename = (item['filename'] % int(season))
                        #log ('finding: %s'%filename)
                        if filename in file_list[1]:
                            url = os.path.join(media_item['artworkdir'][0], filename).encode('utf-8')
                            j += 1
                            generalinfo = '%s: %s  |  ' %( localize(32141), 'n/a')
                            generalinfo += '%s: %s  |  ' %( localize(32144), season)
                            generalinfo += '%s: %s  |  ' %( localize(32143), 'n/a')
                            generalinfo += '%s: %s  |  ' %( localize(32145), 'n/a')
                            # Fill list
                            #log ('found: %s'%url)
                            image_list.append({'url': url,
                                               'preview': url,
                                               'id': filename,
                                               'art_type': [item['art_type']],
                                               'size': '0',
                                               'season': season,
                                               'language': 'EN',
                                               'votes': '0',
                                               'generalinfo': generalinfo})
                        else:
                            missing_arttypes.append(item['art_type'])

                elif item['art_type'] in ['seasonbanner']:
                    for season in media_item['seasons']:
                        if season == '0':
                            filename = "season-specials-banner.jpg"
                        elif season == 'all':
                            filename = "season-all-banner.jpg"
                        else:
                            filename = (item['filename'] % int(season))
                        #log ('finding: %s'%filename)
                        if filename in file_list[1]:
                            url = os.path.join(media_item['artworkdir'][0], filename).encode('utf-8')
                            j += 1
                            generalinfo = '%s: %s  |  ' %( localize(32141), 'n/a')
                            generalinfo += '%s: %s  |  ' %( localize(32144), season)
                            generalinfo += '%s: %s  |  ' %( localize(32143), 'n/a')
                            generalinfo += '%s: %s  |  ' %( localize(32145), 'n/a')
                            # Fill list
                            #log ('found: %s'%url)
                            image_list.append({'url': url,
                                               'preview': url,
                                               'id': filename,
                                               'art_type': [item['art_type']],
                                               'size': '0',
                                               'season': season,
                                               'language': 'EN',
                                               'votes': '0',
                                               'generalinfo': generalinfo})
                        else:
                            missing_arttypes.append(item['art_type'])

                elif item['art_type'] in ['seasonlandscape']:
                    for season in media_item['seasons']:
                        if season == 'all' or season == '':
                            filename = "season-all-landscape.jpg"
                        else:
                            filename = (item['filename'] % int(season))
                        #log ('finding: %s'%filename) 
                        if filename in file_list[1]:
                            url = os.path.join(media_item['artworkdir'][0], filename).encode('utf-8')
                            j += 1
                            generalinfo = '%s: %s  |  ' %( localize(32141), 'n/a')
                            generalinfo += '%s: %s  |  ' %( localize(32144), season)
                            generalinfo += '%s: %s  |  ' %( localize(32143), 'n/a')
                            generalinfo += '%s: %s  |  ' %( localize(32145), 'n/a')
                            # Fill list
                            #log ('found: %s'%url)
                            image_list.append({'url': url,
                                               'preview': url,
                                               'id': filename,
                                               'art_type': [item['art_type']],
                                               'size': '0',
                                               'season': season,
                                               'language': 'EN',
                                               'votes': '0',
                                               'generalinfo': generalinfo})
                        else:
                            missing_arttypes.append(item['art_type'])

                else:
                    if media_item['mediatype'] == 'tvshow':
                        filename = item['filename']
                    else:
                        # only use <movie_filename>-<art_type>.ext for movies
                        filename = media_item['base_name'] + '-' + item['filename']
                        #see if there's still the old <art_type>.ext and rename it
                        filename_old = item['filename']
                        if filename_old in file_list[1]:
                            filename_new_full = os.path.join(media_item['artworkdir'][0], filename)
                            filename_old_full = os.path.join(media_item['artworkdir'][0], filename_old)
                            log('Found: %s'%filename_old)
                            log('Renaming to: %s'%filename)
                            success = xbmcvfs.rename(filename_old_full,filename_new_full)
                            if success:
                                file_list = xbmcvfs.listdir(media_item['artworkdir'][0])
                                force_update = True
                            else:
                                log('Failed to rename : %s'%filename)
                    #log('Searching for: %s'%filename)
                    if filename in file_list[1]:
                        url = os.path.join(media_item['artworkdir'][0], filename).encode('utf-8')
                        j += 1
                        generalinfo = '%s: %s  |  ' %( localize(32141), 'n/a')
                        generalinfo += '%s: %s  |  ' %( localize(32143), 'n/a')
                        generalinfo += '%s: %s  |  ' %( localize(32145), 'n/a')
                        # Fill list
                        #log ('found: %s'%url)
                        image_list.append({'url': url,
                                           'preview': url,
                                           'id': filename,
                                           'art_type': [item['art_type']],
                                           'size': '0',
                                           'season': 'n/a',
                                           'language': 'EN',
                                           'votes': '0',
                                           'generalinfo': generalinfo})
                    else:
                        missing_arttypes.append(item['art_type'])
        #log('total local types needed: %s'%i)
        #log('total local types found:  %s'%j)
        if j < i:
            #log('scan providers for more')
            scan_more = True
        else:
            #log('don''t scan for more')
            scan_more = False
        if image_list == []:
            return image_list, scan_more, missing_arttypes, force_update
        else:
            # Sort the list before return. Last sort method is primary
            image_list = sorted(image_list, key=itemgetter('votes'), reverse=True)
            image_list = sorted(image_list, key=itemgetter('size'), reverse=False)
            image_list = sorted(image_list, key=itemgetter('language'))
            return image_list, scan_more, missing_arttypes, force_update