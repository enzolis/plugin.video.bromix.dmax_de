# -*- coding: utf-8 -*-

import xbmcplugin
import xbmcgui
import xbmcaddon

import os
import json
import urllib
import urllib2

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

from bromixbmc import Bromixbmc
bromixbmc = Bromixbmc("plugin.video.dmax_de", sys.argv)

__FANART__ = os.path.join(bromixbmc.Addon.Path, "fanart.jpg")
__ICON_HIGHLIGHTS__ = os.path.join(bromixbmc.Addon.Path, "resources/media/highlight.png")
__ICON_LIBRARY__ = os.path.join(bromixbmc.Addon.Path, "resources/media/library.png")
__ICON_FAVOURITES__ = os.path.join(bromixbmc.Addon.Path, "resources/media/pin.png")

ACTION_SHOW_HIGHLIGHTS = 'showHighlights'
ACTION_SHOW_LIBRARY = 'showLibrary'
ACTION_SHOW_EPISODES = 'showEpisodes'
ACTION_ADD_TO_FAV = 'addToFav'
ACTION_REMOVE_FROM_FAVS = 'removeFromFavs'
ACTION_SHOW_FAVS = 'showFavs'
ACTION_PLAY = 'play'

SETTING_SHOW_FANART = bromixbmc.Addon.getSetting('showFanart')=="true"
if not SETTING_SHOW_FANART:
    __FANART__ = ""
    
def _doBrightcove(token, command, params={}):
    result = {}
    
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        url = 'https://api.brightcove.com/services/library'
        
        _params = {}
        _params.update(params)
        _params['command'] = command
        _params['token']= token
        url = url + '?' + urllib.urlencode(_params)
        
        content = opener.open(url)
        result = json.load(content)
    except:
        # do nothing
        pass
    
    return result 

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

def _listEpisodes(episodes, showSeriesTitle=True):
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
        
        if showSeriesTitle:
            name = title
            if len(subtitle)>0:
                name = name+" - "+subtitle
        else:
            if len(subtitle)>0:
                name = subtitle
            else:
                name = title
        
        if id!=None:
            params = {'action': ACTION_PLAY,
                      'episode': id}
            
            additionalInfoLabels = {'plot': plot}
            bromixbmc.addVideoLink(name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, additionalInfoLabels=additionalInfoLabels)
    
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
            contextMenu = [("[B]"+bromixbmc.Addon.localize(30002)+"[/B]", contextRun)]
            bromixbmc.addDir(name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, contextMenu=contextMenu)
            pass

def _listJsonResult(jsonResult, showSeriesTitle=True):
    episodes = jsonResult.get('episodes', None)
    if episodes!=None:
        _listEpisodes(episodes, showSeriesTitle)
        
    series = jsonResult.get('series', None)
    if series!=None:
        _listSeries(series)

def showIndex():
    # add 'Highlights'
    params = {'action': ACTION_SHOW_HIGHLIGHTS}
    bromixbmc.addDir(bromixbmc.Addon.localize(30001), params = params, thumbnailImage=__ICON_HIGHLIGHTS__, fanart=__FANART__)
    
    # add 'Videotheke'
    params = {'action': ACTION_SHOW_LIBRARY}
    bromixbmc.addDir(bromixbmc.Addon.localize(30000), params = params, thumbnailImage=__ICON_LIBRARY__, fanart=__FANART__)
    
    # show favourties
    if len(bromixbmc.Addon.getFavorites())>0:
        params = {'action': ACTION_SHOW_FAVS}
        bromixbmc.addDir("[B]"+bromixbmc.Addon.localize(30004)+"[/B]", thumbnailImage=__ICON_FAVOURITES__, params=params, fanart=__FANART__)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def showHighlights():
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/targets/featured/')
    
    _listJsonResult(json, showSeriesTitle=True)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def showLibrary():
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/series/')
    
    _listJsonResult(json)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def showEpisodes(series_id):
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/series//'+series_id+'/episodes/')
    
    _listJsonResult(json, showSeriesTitle=False)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def _getVideoResolution():
    resolution = 720
    
    vq = bromixbmc.Addon.getSetting('videoQuality')
    if vq=='1':
        resolution=720
    elif vq=='0':
        resolution=480
    else:
        resolution=720
        
    return resolution

def _getBestVideoUrl(json):
    url = None
    resolution = _getVideoResolution()
    last_resolution=0
    for stream in json.get('renditions', []):
        test_resolution = stream.get('frameHeight', 0)
        if test_resolution>=last_resolution and test_resolution<=resolution:
            last_resolution = test_resolution
            url = stream.get('url', None)
        pass
    
    return url

def play(episode_id):
    params = {'video_id': episode_id,
              'video_fields': 'name,renditions'}
    result = _doBrightcove('XoVA15ecuocTY5wBbxNImXVFbQd72epyxxVcH3ZVmOA.', 'find_video_by_id', params=params)
    #json = _getContentAsJson('https://api.brightcove.com/services/library?command=find_video_by_id&video_fields=name%2CFLVURL%2CreferenceId%2CitemState%2Cid&media_delivery=http&video_id='+episode_id+'&token=XoVA15ecuocTY5wBbxNImXVFbQd72epyxxVcH3ZVmOA.')
    #url = json.get('FLVURL', None)
    url = _getBestVideoUrl(result)
    if url!=None:
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(bromixbmc.Addon.Handle, True, listitem)
    else:
        bromixbmc.showNotification(bromixbmc.Addon.localize(30999))
        
def addToFavs(series_id):
    json = _getContentAsJson('http://m.app.dmax.de/free-to-air/android/genesis/series/')
    series = json.get('series', {})
    series_list = series.get('series-list', {})
    for series in series_list:
        id = series.get('series-id', "")
        title = series.get('series-title', None)
        if title!=None and id==series_id:
            
            newFav = {}
            newFav['title'] = title
            
            thumbnailImage = series.get('series-cloudinary-image', None)
            if thumbnailImage!=None:
                thumbnailImage =  'http://res.cloudinary.com/db79cecgq/image/upload/c_fill,g_faces,h_270,w_480/'+thumbnailImage
            newFav['image'] = thumbnailImage
            
            bromixbmc.Addon.addFavorite(id, newFav)  
            break
        
def removeFromFavs(series_id):
    favs = bromixbmc.Addon.removeFavorite(series_id)
    xbmc.executebuiltin("Container.Refresh");
        
def showFavs():
    def _sort_key(d):
        return d[1].get('title', "")
    
    _favs = bromixbmc.Addon.getFavorites()
    favs = sorted(_favs, key=_sort_key, reverse=False)
    
    for series in favs:
        if len(series)==2:
            item = series[1]
            name = item.get('title', None)
            thumbnailImage = item.get('image', "")
            
            if name!=None:
                params = {'action': ACTION_SHOW_EPISODES,
                          'series': series[0]}
                
                contextParams = {'action': ACTION_REMOVE_FROM_FAVS,
                                 'series': series[0]}
                contextRun = 'RunPlugin('+bromixbmc.createUrl(contextParams)+')'
                contextMenu = [("[B]"+bromixbmc.Addon.localize(30003)+"[/B]", contextRun)]
                
                bromixbmc.addDir(name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, contextMenu=contextMenu)
            
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
elif action==ACTION_REMOVE_FROM_FAVS and series_id!=None:
    removeFromFavs(series_id)
elif action==ACTION_SHOW_FAVS:
    showFavs()
else:
    showIndex()
