#import modules
import sys
import os
import urllib
import xbmcvfs

### import libraries
#from resources.lib.provider.base import BaseProvider
from resources.lib.script_exceptions import NoFanartError
from resources.lib.utils import *
from operator import itemgetter
from resources.lib.settings import settings
from resources.lib.fileops import fileops

### get addon info
__localize__    = ( sys.modules[ "__main__" ].__localize__ )


class local():
    def get_image_list(self,media_item):
        self.settings = settings()
        self.settings._get_general()    # Get settings from settings.xml
        self.settings._get_artwork()    # Get settings from settings.xml
        self.settings._get_limit()      # Get settings from settings.xml
        self.settings._vars()           # Get some settings vars
        self.settings._artype_list()    # Fill out the GUI and Arttype lists with enabled options
        image_list = []
        target_extrafanartdirs = []
        target_extrathumbsdirs = []
        target_artworkdir = []
        for item in media_item['path']:
            artwork_dir = os.path.join(item + '/')
            extrafanart_dir = os.path.join(artwork_dir + 'extrafanart' + '/')
            extrathumbs_dir = os.path.join(artwork_dir + 'extrathumbs' + '/')
            target_artworkdir.append(artwork_dir.replace('BDMV','').replace('VIDEO_TS',''))
            target_extrafanartdirs.append(extrafanart_dir)
            target_extrathumbsdirs.append(extrathumbs_dir)
        ### Processes the bulk mode downloading of files
        i = 0
        for item in self.settings.available_arttypes:
            add_new = False
            if media_item['mediatype'] == item['media_type']:
                # File naming
                if item['art_type']   == 'extrafanart':
                    pass
                    #item['filename'] = ('%s.jpg'% artwork['id'])
                elif item['art_type'] == 'extrathumbs':
                    pass
                    #item['filename'] = (filename % str(limit_counter + 1))
                elif item['art_type'] in ['seasonposter']:
                    pass
                    '''
                    if artwork['season'] == '0':
                        item['filename'] = "season-specials-poster.jpg"
                    elif artwork['season'] == 'all':
                        item['filename'] = "season-all-poster.jpg"
                    elif artwork['season'] == 'n/a':
                        break
                    else:
                        item['filename'] = (filename % int(artwork['season']))
                    '''
                elif item['art_type'] in ['seasonbanner']:
                    pass
                    '''
                    if artwork['season'] == '0':
                        item['filename'] = "season-specials-banner.jpg"
                    elif artwork['season'] == 'all':
                        item['filename'] = "season-all-banner.jpg"
                    elif artwork['season'] == 'n/a':
                        break
                    else:
                        item['filename'] = (filename % int(artwork['season']))
                    '''
                elif item['art_type'] in ['seasonlandscape']:
                    pass
                    '''
                    if artwork['season'] == 'all' or artwork['season'] == '':
                        item['filename'] = "season-all-landscape.jpg"
                    else:
                        item['filename'] = (filename % int(artwork['season'])
                    '''
                else:
                    filename = item['filename']
                    for targetdir in target_artworkdir:
                        url = os.path.join(targetdir, filename).encode('utf-8')
                        if xbmcvfs.exists(url):
                            add_new = True
                        break
                if add_new:
                    generalinfo = '%s: %s  |  ' %( __localize__(32141), 'English')
                    '''
                    if item.get('season'):
                        generalinfo += '%s: %s  |  ' %( __localize__(32144), item.get('season'))
                    '''
                    generalinfo += '%s: %s  |  ' %( __localize__(32143), 'n/a')
                    generalinfo += '%s: %s  |  ' %( __localize__(32145), 'n/a')
                    # Fill list
                    i += 1
                    image_list.append({'url': url,
                                       'preview': url,
                                       'id': 'local%s'%i,
                                       'type': [item['art_type']],
                                       'size': '0',
                                       'season': 'n/a',
                                       'language': 'EN',
                                       'votes': '0',
                                       'generalinfo': generalinfo})
        if image_list == []:
            return image_list
        else:
            # Sort the list before return. Last sort method is primary
            image_list = sorted(image_list, key=itemgetter('votes'), reverse=True)
            image_list = sorted(image_list, key=itemgetter('size'), reverse=False)
            image_list = sorted(image_list, key=itemgetter('language'))
            return image_list