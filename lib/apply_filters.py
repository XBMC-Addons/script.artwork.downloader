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

### import libraries
from lib.settings import get_limit
setting = get_limit()

def filter(art_type, mediatype, artwork, downloaded_artwork, language, disctype = ''):
    if art_type   == 'fanart':
        return fanart(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'extrafanart':
        return extrafanart(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'extrathumbs':
        return extrathumbs(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'poster':
        return poster(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'seasonposter':
        return seasonposter(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'banner':
        return banner(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'seasonbanner':
        return seasonbanner(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'clearlogo':
        return clearlogo(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'clearart':
        return clearart(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'characterart':
        return characterart(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'landscape':
        return landscape(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'seasonlandscape':
        return seasonlandscape(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'defaultthumb':
        return defaultthumb(mediatype, artwork, downloaded_artwork, language)

    elif art_type == 'discart':
        return discart(mediatype, artwork, downloaded_artwork, language, disctype)
    else:
        return [False, 'Unrecognised art_type']

def fanart(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number fanart reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Minimal size
    elif setting.get('limit_artwork') and 'height' in artwork and (mediatype == 'movie' and artwork['height'] < setting.get('limit_size_moviefanart')) or (mediatype == 'tvshow' and artwork['height'] < setting.get('limit_size_tvshowfanart')):
        reason = 'Size was to small: %s' % artwork['height'] 
        limited = True
    # Minimal rating
    elif setting.get('limit_artwork') and artwork['rating'] < setting.get('limit_extrafanart_rating'):
        reason = 'Rating too low: %s' % artwork['rating']
        limited = True
    # Has text       
    elif setting.get('limit_artwork') and 'series_name' in artwork and setting.get('limit_notext') and artwork['series_name']:
        reason = 'Has text'
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]
    
def extrafanart(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if setting.get('limit_artwork and downloaded_artwork') >= setting.get('limit_extrafanart_max'):
        reason = 'Max number extrafanart reached: %s' % setting.get('limit_extrafanart_max')
        limited = True
    # Minimal size
    elif setting.get('limit_artwork') and 'height' in artwork and (mediatype == 'movie' and artwork['height'] < setting.get('limit_size_moviefanart')) or (mediatype == 'tvshow' and artwork['height'] < setting.get('limit_size_tvshowfanart')):
        reason = 'Size was to small: %s' % artwork['height'] 
        limited = True
    # Minimal rating
    elif setting.get('limit_artwork') and artwork['rating'] < setting.get('limit_extrafanart_rating'):
        reason = 'Rating too low: %s' % artwork['rating']
        limited = True
    # Has text
    elif setting.get('limit_artwork') and 'series_name' in artwork and setting.get('limit_notext') and artwork['series_name']:
        reason = 'Has text'
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
    return [limited, reason]

def extrathumbs(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_extrathumbs_max'):
        reason = 'Max number extrathumbs reached: %s' % setting.get('limit_extrathumbs_max')
        limited = True
    # Minimal size
    elif setting.get('limit_extrathumbs') and 'height' in artwork and artwork['height'] < int('169'):
        reason = 'Size was to small: %s' % artwork['height']
        limited = True
    return [limited, reason]
    
def poster(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''

    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number poster reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Minimal size
    elif setting.get('limit_extrathumbs') and 'height' in artwork and artwork['height'] < int('169'):
        reason = 'Size was to small: %s' % artwork['height']
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language]:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]

def seasonposter(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number seasonposter reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Minimal size
    elif setting.get('limit_extrathumbs') and 'height' in artwork and artwork['height'] < int('169'):
        reason = 'Size was to small: %s' % artwork['height']
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language]:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]

def banner(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number banner reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language]:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]
    
def seasonbanner(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number seasonbanner reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Has season
    if not 'season' in artwork:
        reason = 'No season'
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language]:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]
    
def clearlogo(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number logos reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]
    
def clearart(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number clearart reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]

def characterart(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number characterart reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]
    
def landscape(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number landscape reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]
    
def seasonlandscape(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number seasonthumb reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]

def defaultthumb(mediatype, artwork, downloaded_artwork, language):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number defaultthumb reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]        

def discart(mediatype, artwork, downloaded_artwork, language, disctype):
    limited = False
    reason = ''
    # Maximum number
    if downloaded_artwork >= setting.get('limit_artwork_max'):
        reason = 'Max number discart reached: %s' % setting.get('limit_artwork_max')
        limited = True
    # Correct discnumber
    elif not artwork['discnumber'] == '1':
        reason = "Doesn't match preferred discnumber: 1"
        limited = True
    # Correct discnumber
    elif not artwork['disctype'] == disctype:
        reason = "Doesn't match preferred disctype: %s" %disctype
        limited = True
    # Correct language
    elif setting.get('limit_artwork') and not artwork['language'] in [language, 'n/a']:
        reason = "Doesn't match preferred language: %s" % setting.get('limit_preferred_language')
        limited = True
    return [limited, reason]