import sys
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.utils import _log as log
__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addonid__   = __addon__.getAddonInfo('id')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__cwd__       = __addon__.getAddonInfo('path')
__language__  = __addon__.getLocalizedString
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"

SOURCEPATH = __cwd__
ACTION_PREVIOUS_MENU = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )




class _maingui( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self )
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )
        self.listing = kwargs.get( "listing" )

    def onInit(self):
        try :
            self.img_list = self.getControl(6)
            self.img_list.controlLeft(self.img_list)
            self.img_list.controlRight(self.img_list)
            self.getControl(3).setVisible(False)
        except :
            print_exc()
            self.img_list = self.getControl(3)

        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel(__language__(32123))

        for image in self.listing :
            listitem = xbmcgui.ListItem( image.split("/")[-1] )
            listitem.setIconImage( image )
            listitem.setLabel2(image)
            log( "### image: %s" % image )
            self.img_list.addItem( listitem )
        self.setFocus(self.img_list)

    def onAction(self, action):
        if action in ACTION_PREVIOUS_MENU:
            self.close() 

    def onClick(self, controlID):
        log( "### control: %s" % controlID )
        if controlID == 6 or controlID == 3: 
            num = self.img_list.getSelectedPosition()
            log( "### position: %s" % num )
            self.selected_url = self.img_list.getSelectedItem().getLabel2()
            self.close()

    def onFocus(self, controlID):
        pass

def MyDialog(artwork_list):
    w = MainGui( "DialogSelect.xml", SOURCEPATH, listing=artwork_list )
    w.doModal()
    try: return w.selected_url
    except: 
        print_exc()
        return False
    del w