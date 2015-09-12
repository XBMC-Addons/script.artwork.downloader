#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2011-2014 Martijn Kaijser
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
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
import lib.common
import xbmcgui
from lib.utils import log

### get addon info
ADDON_NAME    = lib.common.ADDON_NAME
ADDON_PATH    = lib.common.ADDON_PATH
ADDON_ICON    = lib.common.ADDON_ICON
localize      = lib.common.localize

### set button actions for GUI
ACTION_PREVIOUS_MENU = (9, 10, 92, 216, 247, 257, 275, 61467, 61448)

pDialog = xbmcgui.DialogProgress()
pDialogBG = xbmcgui.DialogProgressBG()

# Define dialogs
def dialog_msg(action,
               percentage = 0,
               line0 = '',
               line1 = '',
               line2 = '',
               line3 = '',
               background = False,
               nolabel = localize(32026),
               yeslabel = localize(32025),
               cancelled = False):
    # Fix possible unicode errors 
    line0 = line0.encode('utf-8', 'ignore')
    line1 = line1.encode('utf-8', 'ignore')
    line2 = line2.encode('utf-8', 'ignore')
    line3 = line3.encode('utf-8', 'ignore')
    # Dialog logic
    if not line0 == '':
        line0 = ADDON_NAME + line0
    else:
        line0 = ADDON_NAME
    if not background:
        try:
            if action == 'create':
                pDialog.create(ADDON_NAME,
                               line1,
                               line2,
                               line3)
            elif action == 'update':
                pDialog.update(percentage,
                               line1 = "\n",
                               line2 = "\n",
                               line3 = "\n")
                pDialog.update(percentage,
                               line1,
                               line2,
                               line3)
            elif action == 'close':
                pDialog.close()
            elif action == 'iscanceled':
                if pDialog.iscanceled():
                    return True
                else:
                    return False
            elif action == 'createBG':
                pDialogBG.create(heading = ADDON_NAME,
                                 message = line1)
            elif action == 'updateBG':
                pDialogBG.update(percent = percentage,
                                 heading = ADDON_NAME,
                                 message = "\n")
                pDialogBG.update(percent = percentage,
                                 heading = ADDON_NAME,
                                 message = line1)
            elif action == 'closeBG':
                pDialogBG.close()
            elif action == 'iscanceledBG':
                return False
            elif action == 'okdialog':

                xbmcgui.Dialog().ok(line0,
                                    line1,
                                    line2,
                                    line3)
            elif action == 'yesno':
                return xbmcgui.Dialog().yesno(line0,
                                              line1,
                                              line2,
                                              line3,
                                              nolabel,
                                              yeslabel)
        except:
            pass
    else:
        if (action == 'create' or action == 'okdialog'):
            if line2 == '':
                msg = line1
            else:
                msg = line1 + ': ' + line2
            if not cancelled:
                xbmcgui.Dialog().notification(line0,
                                              msg,
                                              ADDON_ICON,
                                              7500)

# Return the selected url to the GUI part
def choose_image(imagelist):
    image_item = False
    image_item = dialog_select(imagelist)
    return image_item 

# This creates the art type selection dialog. The string id is the selection constraint for what type has been chosen.
def choice_type(enabled_type_list, startup, artype_list):
    # Send the image type list to the selection dialog
    select = xbmcgui.Dialog().select(ADDON_NAME + ': ' + localize(32015) , enabled_type_list)
    # When nothing is selected from the dialog
    if select == -1:
        log('### Canceled by user')
        return False
    # If some selection was made
    else:
        # Check what artwork type has been chosen and parse the image restraints
        for item in artype_list:
            if enabled_type_list[select] == localize(item['gui_string']) and startup['mediatype'] == item['media_type']:
                return item
        else:
            return False

# Pass the imagelist to the dialog and return the selection
def dialog_select(image_list):
    w = dialog_select_UI('DialogSelect.xml', ADDON_PATH, listing=image_list)
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

### Retrieves imagelist for GUI solo mode
def gui_imagelist(image_list, art_type):
    log('- Retrieving image list for GUI')
    filteredlist = []
    #retrieve list
    for artwork in image_list:
        if  art_type in artwork['art_type']:
            filteredlist.append(artwork)
    return filteredlist

### Checks imagelist if it has that type of artwork has got images
def hasimages(image_list, art_type):
    found = False
    for artwork in image_list:
        if art_type in artwork['art_type']:
            found = True
            break
        else: pass
    return found
    
class dialog_select_UI(xbmcgui.WindowXMLDialog):
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
        self.getControl(1).setLabel(localize(32015))

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