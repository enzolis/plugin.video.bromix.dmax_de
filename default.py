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
    
__FANART__ = os.path.join(bromixbmc.Addon.Path, "fanart.jpg")

ACTION_SHOW_HIGHLIGHTS = 'showHighlights'
ACTION_SHOW_LIBRARY = 'showLibrary'

SETTING_SHOW_FANART = bromixbmc.Addon.getSetting('showFanart')=="true"

def showIndex():
    # add 'Highlights'
    params = {'action': ACTION_SHOW_HIGHLIGHTS}
    bromixbmc.addDir(bromixbmc.Addon.localize(30001), params = params, fanart=__FANART__)
    
    # add 'Videotheke'
    params = {'action': ACTION_SHOW_LIBRARY}
    bromixbmc.addDir(bromixbmc.Addon.localize(30000), params = params, fanart=__FANART__)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

showIndex()
