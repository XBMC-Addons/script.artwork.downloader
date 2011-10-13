import os
import urllib2
import xbmc
import xbmcgui
import xbmcaddon
import platform
from script_exceptions import CopyError, DownloadError, CreateDirectoryError, HTTP404Error
from urllib2 import URLError

__python_version__ = platform.python_version_tuple()
if (int(__python_version__[0]) == 2 and int(__python_version__[1]) > 4):
    __xbmc_version__ = 'Eden'
    import xbmcvfs
else:
    __xbmc_version__ = 'Dharma'
    import shutil


"""
This module contains helper classes and functions to assist in the
operation of script.extrafanartdownloader
"""

__addon__ = xbmcaddon.Addon('script.extrafanartdownloader')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__localize__ = __addon__.getLocalizedString

def _log(txt, severity=xbmc.LOGDEBUG):

    """Log to txt xbmc.log at specified severity"""

    message = 'script.extrafanartdownloader: %s' % txt
    xbmc.log(msg=message, level=severity)

def get_short_language():
    language = xbmc.getLanguage().upper()
    translates = {
        'ENGLISH':'en',
        'GERMAN': 'de'
    }
    if language in translates:
        return translates[language]
    else:
        ### Default to English
        return 'en'


def _progressdialog(self, action, percentage=0, status='', media_name='', url='', background=False):
    if not background:
        if action == 'create':
            dialog = xbmcgui.DialogProgress()
            dialog.create(__addonname__, status)
        if action == 'update':
            dialog.update(percentage, status, media_name, url)
        if action == 'close':
            dialog.close()
        if action == 'iscanceled':
            if dialog.iscanceled():
                return True
            else:
                return False
        if action == 'okdialog':
            xbmcgui.Dialog().ok(__addonname__, status, media_name)
    if background:
        if (action == 'create' or action == 'okdialog'):
            if media_name == '':
                msg = status
            else:
                msg = status + ': ' + media_name
            xbmc.executebuiltin("XBMC.Notification('%s','%s',10000)" %s (__addonname__, msg))


class fileops:
    """
    This class handles all types of file operations needed by
    script.extrafanartdownloader (creating directories, downloading
    files, copying files etc.)
    """

    def __init__(self):

        """Initialise needed directories/vars for fileops"""

        _log("Setting up fileops")

        if __xbmc_version__ == 'Eden':
            self._exists = lambda path: xbmcvfs.exists(path)
            self._rmdir = lambda path: xbmcvfs.rmdir(path)
            self._mkdir = lambda path: xbmcvfs.mkdir(path)
            self._delete = lambda path: xbmcvfs.delete(path)

        self.downloadcount = 0
        addondir = xbmc.translatePath('special://profile/addon_data/%s' % __addonid__)
        self.tempdir = os.path.join(addondir, 'temp')
        if not self._exists(self.tempdir):
            if not self._exists(addondir):
                if not self._mkdir(addondir):
                    raise CreateDirectoryError(addondir)
            if not self._mkdir(self.tempdir):
                raise CreateDirectoryError(self.tempdir)


    if __xbmc_version__ == 'Eden':
        def _copy(self, source, target):
            return xbmcvfs.copy(source, target)

    ###  Dharma file functions
    else:
        def _exists(self, path):
            return os.path.exists(path)
        def _copy(self, source, target):
            try:
                shutil.copy(source, target)
            except:
                if os.path.exists(target):
                    return True
                else:
                    return False
            else:
                return True
        def _mkdir(self, path):
            try:
                os.makedirs(path)
            except:
                if os.path.exists(path):
                    return True
                else:
                    return False
            else:
                return True
        def _delete(self, path):
            try:
                os.remove(path)
            except:
                return False
            else:
                return True
        def _rmdir(self, path):
            try:
                os.rmdir(path)
            except:
                return False
            else:
                return True
            

    def _copyfile(self, sourcepath, targetpath):

        """
        Copy sourcepath to targetpath and create directory if
        necessary
        """

        targetdir = os.path.dirname(targetpath)
        if not self._exists(targetdir):
            if not self._mkdir(targetdir):
                raise CreateDirectoryError(targetdir)
        if not self._copy(sourcepath, targetpath):
            raise CopyError(targetpath)
        else:
            _log("Copied successfully: %s" % targetpath)


    def _downloadfile(self, url, filename, targetdirs):

        """
        Download url to filename and place in all targetdirs.  If file
        already exists in any of the targetdirs it is copied from there
        to the others instead of being downloaded again.
        """

        fileexists = []
        filenotexistspaths = []
        for targetdir in targetdirs:
            path = os.path.join(targetdir, filename)
            if self._exists(path):
                fileexists.append(True)
                existspath = path
            else:
                fileexists.append(False)
                filenotexistspaths.append(path)
        if not True in fileexists:
            try:
                temppath = os.path.join(self.tempdir, filename)
                url = url.replace(" ", "%20")
                tempfile = open(temppath, "wb")
                response = urllib2.urlopen(url)
                tempfile.write(response.read())
                tempfile.close()
                response.close()
            except URLError, e:
                if e.code == 404:
                    raise HTTP404Error(url)
                else:
                    raise DownloadError(url)
            else:
                _log("Downloaded successfully: %s" % url, xbmc.LOGNOTICE)
                self.downloadcount = self.downloadcount + 1
                for filenotexistspath in filenotexistspaths:
                    self._copyfile(temppath, filenotexistspath)
        elif not False in fileexists:
            pass
        else:
            for filenotexistspath in filenotexistspaths:
                self._copyfile(existspath, filenotexistspath)
