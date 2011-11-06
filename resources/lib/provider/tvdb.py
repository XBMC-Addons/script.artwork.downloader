from resources.lib.provider.base import BaseProvider
from resources.lib.script_exceptions import NoFanartError
from resources.lib.utils import _log as log

from elementtree import ElementTree as ET

class TVDBProvider(BaseProvider):
    """
    Setup provider for TheTVDB.com
    """
    def __init__(self):
        self.name = 'TVDB'
        self.api_key = '1A41A145E2DA0053'
        self.url = 'http://www.thetvdb.com/api/%s/series/%s/banners.xml'
        self.url_prefix = 'http://www.thetvdb.com/banners/'
    
    def get_image_list(self, media_id):
        xml_url = self.url % (self.api_key, media_id)
        log('API: %s ' % xml_url)
        image_list = []
        data = self.get_xml(xml_url)
        tree = ET.fromstring(data)
        for image in tree.findall('Banner'):
            info = {}
            if image.findtext('BannerPath'):
                info['url'] = self.url_prefix + image.findtext('BannerPath')
                info['language'] = image.findtext('Language')
                if image.findtext('BannerType2') :
                    info['type'] = image.findtext('BannerType')
                    try:
                        x,y = image.findtext('BannerType2').split('x')
                        info['width'] = int(x)
                        info['height'] = int(y)
                    except:
                        info['type2'] = image.findtext('BannerType')
                    info['size'] = 'original'
                info['series_name'] = image.findtext('SeriesName') == 'true'
                if image.findtext('RatingCount') and int(image.findtext('RatingCount')) >= 1:
                    info['rating'] = float(image.findtext('Rating'))
                else:
                    info['rating'] = 0
            if info:            
                image_list.append(info) 
        if image_list == []:
            raise NoFanartError(media_id)
        else:
            return image_list