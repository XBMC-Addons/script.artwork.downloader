from resources.lib.provider.base import BaseProvider
from resources.lib.script_exceptions import NoFanartError, ItemNotFoundError
from resources.lib.utils import _log as log
from resources.lib.utils import _normalize_string as normalize
from resources.lib import language
from elementtree import ElementTree as ET
from resources.lib.utils import _get_xml as _get_xml

class TMDBProvider(BaseProvider):

    def __init__(self):
        self.name = 'TMDB'
        self.api_key = '4be68d7eab1fbd1b6fd8a3b80a65a95e'
        self.api_limits = True
        self.url = "http://api.themoviedb.org/2.1/Movie.getImages/" + language.get_abbrev() + "/xml/%s/%s"

    def get_image_list(self, media_id):
        xml_url = self.url % (self.api_key, media_id)
        log('API: %s ' % xml_url)
        image_list = []
        data = _get_xml(xml_url)
        tree = ET.fromstring(data)
        tree = tree.findall('movies')[0]
        try:
            tree = tree.findall('movie')[0]
        except IndexError:
            raise ItemNotFoundError(media_id)
        else:
            tree = tree.findall('images')[0]
            for imagetype in ['poster', 'backdrop']:
                for image in tree.findall(imagetype):
                    for sizes in image:
                        info = {}
                        info['id'] = image.get('id')
                        info['type'] = ''
                        if imagetype == 'backdrop' and sizes.get('size') == 'original':
                            info['type'] = 'fanart'
                        elif imagetype == 'backdrop' and sizes.get('size') == 'poster':
                            info['type'] = 'thumb'
                        elif imagetype == 'poster' and sizes.get('size') == 'original':
                            info['type'] = 'poster'
                        if not info['type'] == '' and sizes.get('size') == 'thumb':
                            info['preview'] = sizes.get('url')
                        info['url'] = sizes.get('url')
                        info['language'] = language.get_abbrev()
                        info['rating'] = 'n/a'
                        info['preview'] = info['url']
                        info['height'] = int(sizes.get('height'))
                        info['width'] = int(sizes.get('width'))
                        if info:
                            image_list.append(info)
            if image_list == []:
                raise NoFanartError(media_id)
            else:
                return image_list

def _search_movie(medianame,year=''):
    medianame = normalize(medianame)
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame,year) )
    illegal_char = ' -<>:"/\|?*%'
    for char in illegal_char:
        medianame = medianame.replace( char , '+' ).replace( '++', '+' ).replace( '+++', '+' )
    api_key = '4be68d7eab1fbd1b6fd8a3b80a65a95e'
    xml_url = 'http://api.themoviedb.org/2.1/Movie.search/en/xml/%s/%s+%s' %(api_key,medianame,year)
    tmdb_id = ''
    log('TMDB API search url: %s ' % xml_url)
    data = _get_xml(xml_url)
    tree = ET.fromstring(data)
    #log('%s'%data)
    '''
    for item in tree.getiterator():
        if item.tag == ('id'):
            tmdb_id = 'tmdb%s' %item.text
            print tmdb_id
    '''
    for item in tree.getiterator():
        if item.findtext('id'):
            tmdb_id = item.findtext('id')
            log('Found tmdb ID: %s'%tmdb_id)
            break
    if tmdb_id == '':
        log('Did not find tmdb ID')
    return tmdb_id