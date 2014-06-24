# -*- coding: utf-8 -*-
import xbmcplugin
import xbmcgui
import xbmcaddon

import os
import json
import urllib2

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
ACTION_SHOW_EPISODES = 'showEpisodes'
ACTION_PLAY = 'play'

SETTING_SHOW_FANART = bromixbmc.Addon.getSetting('showFanart')=="true"

def _getContentAsJson(url):
    result = {}
    
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        content = opener.open(url)
        result = json.load(content)
    except:
        # do nothing
        pass
    
    return result

def _listEpisodes(episodes):
    episodes_list = episodes.get('episodes-list', {})
    
    for episode in episodes_list:
        thumbnailImage = episode.get('episode-image', "")
        title = episode.get('episode-title', "")
        subtitle = episode.get('episode-subtitle', "")
        plot = episode.get('episode-long-description', "")
        id = str(episode.get('episode-id', ""))
        
        name = title+" - "+subtitle
        
        if id!="":
            params = {'action': ACTION_PLAY,
                      'episode': id}
            bromixbmc.addVideoLink(name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, plot=plot)
    
def _listSeries(series):
    def _sort_key(d):
        return d.get('series-title', "").lower()
    
    _series_list = series.get('series-list', {})
    series_list = sorted(_series_list, key=_sort_key, reverse=False)
    
    for series in series_list:
        name = series.get('series-title', None)
        id = series.get('series-id', None)
        if name!=None and id!=None:
            params = {'action': ACTION_SHOW_EPISODES,
                      'series': id}
            bromixbmc.addDir(name, params=params, fanart=__FANART__)
            pass

def _listJsonResult(jsonResult):
    episodes = jsonResult.get('episodes', None)
    if episodes!=None:
        _listEpisodes(episodes)
        
    series = jsonResult.get('series', None)
    if series!=None:
        _listSeries(series)

def showIndex():
    # add 'Highlights'
    params = {'action': ACTION_SHOW_HIGHLIGHTS}
    bromixbmc.addDir(bromixbmc.Addon.localize(30001), params = params, fanart=__FANART__)
    
    # add 'Videotheke'
    params = {'action': ACTION_SHOW_LIBRARY}
    bromixbmc.addDir(bromixbmc.Addon.localize(30000), params = params, fanart=__FANART__)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def showHighlights():
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/targets/featured/')
    
    _listJsonResult(json)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def showLibrary():
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/series/')
    
    _listJsonResult(json)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

action = bromixbmc.getParam('action')

if action==ACTION_SHOW_HIGHLIGHTS:
    showHighlights()
elif action==ACTION_SHOW_LIBRARY:
    showLibrary()
else:
    showIndex()
