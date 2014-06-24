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
ACTION_ADD_TO_FAV = 'addToFav'
ACTION_SHOW_FAVS = 'showFavs'
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
    
    xbmcplugin.setContent(bromixbmc.Addon.Handle, 'episodes')
    for episode in episodes_list:
        thumbnailImage = episode.get('episode-cloudinary-image', None)
        if thumbnailImage!=None:
            thumbnailImage =  'http://res.cloudinary.com/db79cecgq/image/upload/c_fill,g_faces,h_270,w_480/'+thumbnailImage
            
        title = episode.get('episode-title', "")
        subtitle = episode.get('episode-subtitle', "")
        plot = episode.get('episode-long-description', "")
        
        id = episode.get('episode-additional-info', None)
        if id!=None:
            id = id.get('episode-brightcove-id', None)
        
        name = title+" - "+subtitle
        
        if id!=None:
            params = {'action': ACTION_PLAY,
                      'episode': id}
            bromixbmc.addVideoLink(name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, plot=plot, tvshowtitle=title)
    
def _listSeries(series):
    def _sort_key(d):
        return d.get('series-title', "").lower()
    
    _series_list = series.get('series-list', {})
    series_list = sorted(_series_list, key=_sort_key, reverse=False)
    
    for series in series_list:
        name = series.get('series-title', None)
        id = series.get('series-id', None)
        
        thumbnailImage = series.get('series-cloudinary-image', None)
        if thumbnailImage!=None:
            thumbnailImage =  'http://res.cloudinary.com/db79cecgq/image/upload/c_fill,g_faces,h_270,w_480/'+thumbnailImage
        
        if name!=None and id!=None:
            params = {'action': ACTION_SHOW_EPISODES,
                      'series': id}
            
            contextParams = {'action': ACTION_ADD_TO_FAV,
                             'series': id}
            contextRun = 'RunPlugin('+bromixbmc.createUrl(contextParams)+')'
            contextMenu = [(bromixbmc.Addon.localize(30002), contextRun)]
            bromixbmc.addDir(name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, contextMenu=contextMenu)
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
    
    # show favourties?
    favs = bromixbmc.Addon.loadFavs()
    if len(favs['favs'])>0:
        params = {'action': ACTION_SHOW_FAVS}
        bromixbmc.addDir("[B]"+bromixbmc.Addon.localize(30004)+"[/B]", params=params, fanart=__FANART__)
    
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

def showEpisodes(series_id):
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/series//'+series_id+'/episodes/')
    
    _listJsonResult(json)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def play(episode_id):
    json = _getContentAsJson('https://api.brightcove.com/services/library?command=find_video_by_id&video_fields=name%2CFLVURL%2CreferenceId%2CitemState%2Cid&media_delivery=http&video_id='+episode_id+'&token=XoVA15ecuocTY5wBbxNImXVFbQd72epyxxVcH3ZVmOA.')
    url = json.get('FLVURL', None)
    if url!=None:
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(bromixbmc.Addon.Handle, True, listitem)
    else:
        bromixbmc.showNotification(bromixbmc.Addon.localize(30999))
        
def addToFavs(series_id):
    favs = bromixbmc.Addon.loadFavs()
    
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/series/')
    series = json.get('series', {})
    series_list = series.get('series-list', {})
    for series in series_list:
        id = series.get('series-id', "")
        title = series.get('series-title', None)
        if title!=None and id==series_id:
            favs['favs'][id] = {}
            item = favs['favs'][id]
            item['title'] = title
            
            thumbnailImage = series.get('series-cloudinary-image', None)
            if thumbnailImage!=None:
                thumbnailImage =  'http://res.cloudinary.com/db79cecgq/image/upload/c_fill,g_faces,h_270,w_480/'+thumbnailImage
            item['image'] = thumbnailImage
            
            bromixbmc.Addon.storeFavs(favs)  
            break
        
def showFavs():
    def _sort_key(d):
        return d[1].get('title', "")
    
    _favs = bromixbmc.Addon.loadFavs()['favs']
    favs = sorted(_favs.items(), key=_sort_key, reverse=False)
    
    for series in favs:
        item = series[1]
        name = item.get('title', None)
        thumbnailImage = item.get('image', "")
        
        if name!=None:
            params = {'action': ACTION_SHOW_EPISODES,
                      'series': series[0]}
            bromixbmc.addDir(name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__)
            
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

action = bromixbmc.getParam('action')
series_id = bromixbmc.getParam('series')
episode_id = bromixbmc.getParam('episode')

if action==ACTION_SHOW_HIGHLIGHTS:
    showHighlights()
elif action==ACTION_SHOW_LIBRARY:
    showLibrary()
elif action==ACTION_SHOW_EPISODES and series_id!=None:
    showEpisodes(series_id)
elif action==ACTION_PLAY and episode_id!=None:
    play(episode_id)
elif action==ACTION_ADD_TO_FAV and series_id!=None:
    addToFavs(series_id)
elif action==ACTION_SHOW_FAVS:
    showFavs()
else:
    showIndex()
