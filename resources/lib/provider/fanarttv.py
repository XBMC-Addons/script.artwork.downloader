from resources.lib.provider.base import BaseProvider
from resources.lib.script_exceptions import NoFanartError, ItemNotFoundError
from resources.lib.utils import _log as log
from resources.lib import language

from elementtree import ElementTree as ET

class FTV_TVProvider(BaseProvider):

    def __init__(self):
        self.name = 'fanart.tv - TV API'
        self.url = 'http://fanart.tv/api/fanart.php?id=%s'
        self.imagetypes = ['clearlogo', 'clearart', 'tvthumb', 'seasonthumb']
        
    def get_image_list(self, media_id):
        xml_url = self.url % (media_id)
        log('API: %s ' % xml_url)
        image_list = []
        data = self.get_xml(xml_url)
        tree = ET.fromstring(data)
        for imagetype in self.imagetypes:
            imageroot = imagetype + 's'
            for image in tree.findall(imageroot):
                info = {}
                info['type'] = imagetype
                info['url'] = image.get('url')
                if info:            
                    image_list.append(info) 
        if image_list == []:
            raise NoFanartError(media_id)
        else:
            return image_list 
        '''
        example url: http://fanart.tv/api/fanart.php?id=71663   (The Simpsons)
        API info: http://fanart.tv/api-info/
        See the download section in default.py what info[] is expected for now. This can be changed when cleaning up.
        The seasonthumbs need to get info['season'] for season numbering with the value that is between brackets.
        This will later be converted into what we need.
        The first seasonthumb is one we probably don't need.
        '''
        
        
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
