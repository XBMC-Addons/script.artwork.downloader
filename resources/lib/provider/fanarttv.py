from resources.lib.provider.base import BaseProvider
#from script_exceptions import NoFanartError
#from utils import _log as log

#import ElementTree as ET

class FTV_TVProvider(BaseProvider):
    """
    Setup provider for TheTVDB.com
    """
    def __init__(self):
        self.name = 'fanart.tv - TV API'
        self.url = 'http://fanart.tv/api/fanart.php?id=%s'

        
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