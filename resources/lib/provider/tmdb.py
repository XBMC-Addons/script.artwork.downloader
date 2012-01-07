### import libraries
from resources.lib.script_exceptions import NoFanartError, ItemNotFoundError
from resources.lib.utils import _log as log
from resources.lib.utils import _normalize_string as normalize
from resources.lib.utils import _get_xml as get_xml
from resources.lib.utils import _get_json as get_json
from resources.lib import language
from elementtree import ElementTree as ET


class TMDBProvider():

    def __init__(self):
        self.name = 'TMDB'
        self.api_key = '4be68d7eab1fbd1b6fd8a3b80a65a95e'
        self.url = "http://api.themoviedb.org/3/movie/%s/images?api_key=%s"
        self.imageurl = "http://cf2.imgobject.com/t/p/"

    def get_image_list(self, media_id):
        data = get_json(self.url %(media_id, self.api_key))
        image_list = []
        # Get fanart
        for item in data['backdrops']:
            info = {}
            info['url'] = self.imageurl + 'original' + item['file_path']    # Original image url
            info['preview'] = self.imageurl + 'w300' + item['file_path']    # Create a preview url for later use
            info['id'] = item['file_path'].lstrip('/').replace('.jpg', '')  # Strip filename to get an ID
            info['type'] = 'fanart'                                         # Set standard to 'fanart'
            info['height'] = item['height']
            info['width'] = item['width']
            #info['aspect_ratio'] = item['aspect_ratio']                    # Who know when we may need it
            # Convert the 'None' value to default 'en'
            if not item['iso_639_1']:
                info['language'] = 'n/a'
            else:
                info['language'] = item['iso_639_1']
            info['rating'] = 'n/a'                                          # Rating may be integrated at later time
            
            # Create Gui string to display
            info['generalinfo'] = 'Language: %s  |  Rating: %s  |  Size: %sx%s   ' %(info['language'], info['rating'], info['width'],info['height'])
            if info:
                image_list.append(info)
        # Get thumbs
        for item in data['backdrops']:
            info = {}
            info['url'] = self.imageurl + 'w780' + item['file_path']    # Original image url
            info['preview'] = self.imageurl + 'w300' + item['file_path']    # Create a preview url for later use
            info['id'] = item['file_path'].lstrip('/').replace('.jpg', '')  # Strip filename to get an ID
            info['type'] = 'thumb'                                         # Set standard to 'fanart'
            info['height'] = item['height']
            info['width'] = item['width']
            #info['aspect_ratio'] = item['aspect_ratio']                    # Who know when we may need it
            # Convert the 'None' value to default 'en'
            if not item['iso_639_1']:
                info['language'] = 'n/a'
            else:
                info['language'] = item['iso_639_1']
            info['rating'] = 'n/a'                                          # Rating may be integrated at later time
            
            # Create Gui string to display
            info['generalinfo'] = 'Language: %s  |  Rating: %s   ' %(info['language'], info['rating'])
            if info:
                image_list.append(info)
        # Get posters
        for item in data['posters']:
            info = {}
            info['url'] = self.imageurl + 'original' + item['file_path']    # Original image url
            info['preview'] = self.imageurl + 'w185' + item['file_path']    # Create a preview url for later use
            info['id'] = item['file_path'].lstrip('/').replace('.jpg', '')  # Strip filename to get an ID
            info['type'] = 'poster'                                         # Set standard to 'fanart'
            info['height'] = item['height']
            info['width'] = item['width']
            #info['aspect_ratio'] = item['aspect_ratio']                    # Who know when we may need it
            # Convert the 'None' value to default 'en'
            if not item['iso_639_1']:
                info['language'] = 'n/a'
            else:
                info['language'] = item['iso_639_1']
            info['rating'] = 'n/a'                                          # Rating may be integrated at later time
            
            # Create Gui string to display
            info['generalinfo'] = 'Language: %s  |  Rating: %s  |  Size: %sx%s   ' %(info['language'], info['rating'], info['width'],info['height'])
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
    json_url = 'http://api.themoviedb.org/3/search/movie?query=%s+%s&api_key=%s' %( medianame, year, api_key )
    tmdb_id = ''
    log('TMDB API search:   %s ' % json_url)
    try:
        data = get_json(json_url)
        for item in data['results']:
            if item['id']:
                tmdb_id = item['id']
                break
    except Exception, e:
        log( str( e ), xbmc.LOGERROR )
    if tmdb_id == '':
        log('TMDB API search found no ID')
    return tmdb_id


def _search_movie_old(medianame,year=''):
    medianame = normalize(medianame)
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame,year) )
    illegal_char = ' -<>:"/\|?*%'
    for char in illegal_char:
        medianame = medianame.replace( char , '+' ).replace( '++', '+' ).replace( '+++', '+' )
    api_key = '4be68d7eab1fbd1b6fd8a3b80a65a95e'
    xml_url = 'http://api.themoviedb.org/2.1/Movie.search/en/xml/%s/%s+%s' %(api_key,medianame,year)
    tmdb_id = ''
    log('TMDB API search:   %s ' % xml_url)
    try:
        data = get_xml(xml_url)
        tree = ET.fromstring(data)
        for item in tree.getiterator():
            if item.findtext('id'):
                tmdb_id = item.findtext('id')
                log('TMDB API search found ID: %s'%tmdb_id)
                break
    except:
        log('TMDB API problem getting XML data')
    if tmdb_id == '':
        log('TMDB API search found no ID')
    return tmdb_id



class TMDBProvider_old():

    def __init__(self):
        self.name = 'TMDB'
        self.api_key = '4be68d7eab1fbd1b6fd8a3b80a65a95e'
        self.url = "http://api.themoviedb.org/2.1/Movie.getImages/" + language.get_abbrev() + "/xml/%s/%s"

    def get_image_list(self, media_id):
        xml_url = self.url % (self.api_key, media_id)
        log('API:               %s ' % xml_url)
        image_list = []
        data = get_xml(xml_url)
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