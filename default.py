# -*- coding: utf-8 -*-
import xbmcplugin
import xbmcgui
import xbmcaddon

import os

import pydevd
pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

from bromixbmc import Bromixbmc
bromixbmc = Bromixbmc("plugin.video.dmax_de", sys.argv)

__addon_data_path__ = bromixbmc.Addon.DataPath
if not os.path.isdir(__addon_data_path__):
    os.mkdir(__addon_data_path__)

#sevenTv = SevenTv(os.path.join(__addon_data_path__, 'favs.dat'))

SETTING_SHOW_FANART = bromixbmc.Addon.getSetting('showFanart')=="true"

def showIndex():
    pass

showIndex()
