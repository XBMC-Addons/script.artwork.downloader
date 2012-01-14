#import modules
import xbmc
import xbmcaddon
def get_abbrev():
    language = xbmcaddon.Addon().getSetting("limit_language").upper()
    translates = {
        'DUTCH'     : 'nl',
        'ENGLISH'   : 'en',
        'FRENCH'    : 'fr',
        'GERMAN'    : 'de',
        'ITALIAN'   : 'it',
        'POLISH'    : 'pl',
        'RUSSIAN'   : 'ru',
        'SPANISH'   : 'es'
    }
    if language in translates:
        return translates[language]
    else:
        ### Default to English
        return 'en'