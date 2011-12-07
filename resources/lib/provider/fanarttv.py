from resources.lib.provider.base import BaseProvider
from resources.lib.script_exceptions import NoFanartError, ItemNotFoundError
from resources.lib.utils import _log as log
from elementtree import ElementTree as ET

class FTV_TVProvider(BaseProvider):
    def __init__(self):
        self.name = 'fanart.tv - TV API'
        self.api_key = '586118be1ac673f74963cc284d46bd8e'
        #self.url = "http://fanart.tv/webservice/series/%s/%s/xml/all/1/2"
        self.url = 'http://fanart.tv/api/fanart.php?v=4&id=%s'
        self.imagetypes = ['clearlogo', 'clearart', 'tvthumb', 'seasonthumb', 'characterart']

    def get_image_list(self, media_id):
        #xml_url = self.url % (self.api_key,media_id)
        xml_url = self.url % (media_id)
        log('API: %s ' % xml_url)
        image_list = []
        data = self.get_xml(xml_url)
        tree = ET.fromstring(data)
        for imagetype in self.imagetypes:
            imageroot = imagetype + 's'
            for images in tree.findall(imageroot):
                for image in images:
                    info = {}
                    info['id'] = image.get('id')
                    info['url'] = image.get('url')
                    info['type'] = imagetype
                    '''
                    info['language'] = image.get('lang')
                    info['likes'] = image.get('likes')
                    if imagetype == 'seasonthumb':
                        seasonxx = "%.2d" % int(image.findtext('season')) #ouput is double digit int
                        if seasonxx == '00':
                            info['season'] = '-specials'
                        else:
                            info['season'] = str(seasonxx)
                        info['season'] = "%.2d" % int(image.get('season')) #ouput is double digit int
                    else:
                        info['season'] = 'NA'
                    '''
                    if info
                        image_list.append(info)
        if image_list == []:
            raise NoFanartError(media_id)
        else:
            return image_list
        
class FTV_MovieProvider(BaseProvider):
    """
    Setup provider for TheTVDB.com
    """
    def __init__(self):
        self.name = 'fanart.tv - Music API'
        self.url = 'http://fanart.tv/api/fanart.php?id=%s'
        
class FTV_MusicProvider(BaseProvider):
    """
    Setup provider for TheTVDB.com
    """
    def __init__(self):
        self.name = 'fanart.tv - Music API'
        self.url = 'http://fanart.tv/api/music.php?id=%s&type=background'
