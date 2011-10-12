import os
import urllib2
import xbmc
import xbmcaddon
import platform
from script_exceptions import CopyError, DownloadError, XmlError, MediatypeError, DeleteError, CreateDirectoryError, HTTP404Error
from urllib2 import URLError

__python_version__ = platform.python_version_tuple()
if (int(__python_version__[0]) == 2 and int(__python_version__[1]) > 4):
    __xbmc_version__ = 'Eden'
    import xbmcvfs
else:
    __xbmc_version__ = 'Dharma'
    import shutil as xbmcvfs


"""
This module contains helper classes and functions to assist in the
operation of script.extrafanartdownloader
"""

__addon__ = xbmcaddon.Addon('script.extrafanartdownloader')
__addonid__ = __addon__.getAddonInfo('id')

def _log(txt, severity=xbmc.LOGDEBUG):

    """Log to txt xbmc.log at specified severity"""

    message = 'script.extrafanartdownloader: %s' % txt
    xbmc.log(msg=message, level=severity)


class fileops:

    """
    This class handles all types of file operations needed by
    script.extrafanartdownloader (creating directories, downloading
    files, copying files etc.)
    """

    def __init__(self):

        """Initialise needed directories/vars for fileops"""

        self.downloadcount = 0
        addondir = xbmc.translatePath('special://profile/addon_data/%s' % __addonid__)
        self.tempdir = os.path.join(addondir, 'temp')
        if not xbmcvfs.exists(self.tempdir):
            if not xbmcvfs.exists(addondir):
                if not xbmcvfs.mkdir(addondir):
                    raise CreateDirectoryError(addondir)
            if not xbmcvfs.mkdir(self.tempdir):
                raise CreateDirectoryError(self.tempdir)


    def _copyfile(self, sourcepath, targetpath):

        """
        Copy sourcepath to targetpath and create directory if
        necessary
        """

        targetdir = os.path.dirname(targetpath)
        if not xbmcvfs.exists(targetdir):
            if not xbmcvfs.mkdir(targetdir):
                raise CreateDirectoryError(targetdir)
        if not xbmcvfs.copy(sourcepath, targetpath):
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
            if xbmcvfs.exists(path):
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
