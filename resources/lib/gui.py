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

#import modules
import sys
import xbmcgui
from resources.lib.utils import log

### get addon info
__addon__       = ( sys.modules[ "__main__" ].__addon__ )
__addonname__   = ( sys.modules[ "__main__" ].__addonname__ )
__localize__    = ( sys.modules[ "__main__" ].__localize__ )
__addonpath__   = ( sys.modules[ "__main__" ].__addonpath__ )
### set button actions for GUI
ACTION_PREVIOUS_MENU = (9, 10, 92, 216, 247, 257, 275, 61467, 61448)

# Pass the imagelist to the dialog and return the selection
def dialog_select(image_list):
    w = MainGui('DialogSelect.xml', __addonpath__, listing=image_list)
    w.doModal()
    selected_item = False
    try:
        # Go through the image list and match the chooosen image id and return the image url
        for item in image_list:
            if w.selected_id == item['id']:
                selected_item = item
        return selected_item
    except: 
        print_exc()
        return selected_item
    del w

class MainGui(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listing = kwargs.get('listing')
        self.selected_id = ''

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
        self.getControl(1).setLabel(__localize__(32015))

        for image in self.listing:
            listitem = xbmcgui.ListItem('%s' %(image['generalinfo']))
            listitem.setIconImage(image['preview'])
            listitem.setLabel2(image['id'])
            self.img_list.addItem(listitem)
        self.setFocus(self.img_list)

    def onAction(self, action):
        if action in ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        log('# GUI control: %s' % controlID)
        if controlID == 6 or controlID == 3: 
            num = self.img_list.getSelectedPosition()
            log('# GUI position: %s' % num)
            self.selected_id = self.img_list.getSelectedItem().getLabel2()
            log('# GUI selected image ID: %s' % self.selected_id)
            self.close()

    def onFocus(self, controlID):
        pass