# -*- coding: utf-8 -*-
#
# Credits:
# Copied some code from: UnSupportedAppstore.bundle
#

import json
import os
from lxml import etree
#Not using objectify for now: Using SubElement requires version 3.2 of lxml
#from lxml import objectify

NAME = 'Playlists'
PREFIX = '/music/playlists'
PLUGIN_DIR = 'com.plexapp.plugins.playlist'
PMS_URL_PLEX = 'http://192.168.10.20:32400'
LIBRARY_SECTIONS = '/library/sections/'
ART = 'art-default.png'
ICON = 'icon-default.png'

# Preferences
PREFS__USERNAME = 'username'
PREFS__PLEXPORT = 'plexport'


# XML Root
PLAYLIST_ROOT = 'playlist'

# XML Attribute names
ATTR_KEY = 'key'
ATTR_TITLE = 'title'
ATTR_RATINGKEY = 'ratingKey'
ATTR_DURATION = 'duration'
ATTR_THUMB = 'thumb'
ATTR_ART = 'art'
ATTR_PARTKEY = 'partkey'
ATTR_BITRATE = 'bitrate'
ATTR_AUDIOCHANNELS = 'audioChannels'
ATTR_AUDIOCODEC = 'audioCodec'
ATTR_CONTAINER = 'container'
ATTR_VIEWGROUP = 'viewGroup'
ATTR_SEARCH = 'search'
ATTR_PROMPT = 'prompt'

# Create new playlist
NEW_PL_TITLE = 'title'
NEW_PL_DESCRIPTION = 'description'
NEW_PL_TYPE = 'playlist_type'
PL_TYPE_SIMPLE = 'SIMPLE'
PL_TYPE_SMART = 'SMART'
PL_TYPES = [PL_TYPE_SIMPLE, PL_TYPE_SMART]

# Resource stings
TEXT_MAIN_TITLE = "MAIN_TITLE"
TEXT_PREFERENCES = "PREFERENCES"

TEXT_MENU_ACTION_PLAYLIST_MAINTENANCE = "MENU_ACTION_PLAYLIST_MAINTENANCE"
TEXT_MENU_ACTION_CREATE_PLAYLIST = "MENU_ACTION_CREATE_PLAYLIST"
TEXT_MENU_ACTION_ADD_TRACKS = "MENU_ACTION_ADD_TRACKS"
TEXT_MENU_ACTION_REMOVE_TRACKS = "MENU_ACTION_REMOVE_TRACKS"
TEXT_MENU_ACTION_DELETE_PLAYLIST = "MENU_ACTION_DELETE_PLAYLIST"
TEXT_MENU_ACTION_RENAME_PLAYLIST = "MENU_ACTION_RENAME_PLAYLIST"
TEXT_MENU_TITLE_TRACK_ACTIONS = "MENU_TITLE_TRACK_ACTIONS"

TEXT_MENU_CREATEPL_ENTER_TITLE = "MENU_CREATEPL_ENTER_TITLE"
TEXT_MENU_CREATEPL_ENTER_DESCR = "MENU_CREATEPL_ENTER_DESCR"
TEXT_MENU_CREATEPL_SELECT_TYPE = "MENU_CREATEPL_SELECT_TYPE"
TEXT_MENU_CREATEPL_ENTER_TITLE_PROMPT = "MENU_CREATEPL_ENTER_TITLE_PROMPT"
TEXT_MENU_CREATEPL_ENTER_DESCR_PROMPT = "MENU_CREATEPL_ENTER_DESCR_PROMPT"
TEXT_MENU_CREATEPL_SELECT_TYPE_PROMPT = "MENU_CREATEPL_SELECT_TYPE_PROMPT"
TEXT_MENU_CREATEPL_CREATE_LIST = "MENU_CREATEPL_CREATE_LIST"

TEXT_TITLE_ADD_TO_PLAYLIST = "TITLE_ADD_TO_PLAYLIST"
TEXT_MSG_EMPTY_PLAYLIST = "MSG_EMPTY_PLAYLIST"
TEXT_MSG_TRACK_ALREADY_IN_PLAYLIST = "MSG_TRACK_ALREADY_IN_PLAYLIST"
TEXT_MSG_TRACK_ADDED_TO_PLAYLIST = "MSG_TRACK_ADDED_TO_PLAYLIST"
TEXT_MSG_PLAYLIST_CREATED = "MSG_PLAYLIST_CREATED"
TEXT_ERROR_NO_METADATA = "ERROR_NO_METADATA"
TEXT_ERROR_NO_TRACK_FOUND = "ERROR_NO_TRACK_FOUND"
TEXT_ERROR_NO_MEDIA_FOR_TRACK = "ERROR_NO_MEDIA_FOR_TRACK"
TEXT_ERROR_NO_TRACK_DATA = "ERROR_NO_TRACK_DATA"
TEXT_ERROR_TRACK_NOT_ADDED = "ERROR_TRACK_NOT_ADDED"
TEXT_ERROR_PLAYLIST_EXISTS = "ERROR_PLAYLIST_EXISTS"
TEXT_ERROR_MISSING_TITLE = "ERROR_MISSING_TITLE"
TEXT_ERROR_EMPTY_SEARCH_QUERY = "ERROR_EMPTY_SEARCH_QUERY" 

####################################################################################################
def Start():
    
    Plugin.AddPrefixHandler(PREFIX, MainMenu, NAME)
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    Plugin.AddViewGroup('Maintenance', viewMode='List', mediaType='items')

    ObjectContainer.title1 = L(TEXT_MAIN_TITLE)
    ObjectContainer.view_group = 'List'
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)    
    
    LoadGlobalData()

####################################################################################################
def ValidatePrefs():
    return 

def LoadGlobalData():
    global allPlaylists
    global pms_main_url
    
    pms_main_url = 'http://%s:%s' %(Network.Address, Prefs[PREFS__PLEXPORT])
    # For now: always use the main server URL
    #pms_main_url = PMS_URL_PLEX
    
    allPlaylists = loadPlaylists()   
    pass
  
####################################################################################################
#@handler(PREFIX, NAME)
def MainMenu():
    
    oc = ObjectContainer(no_cache = True)

    for playlistkey in allPlaylists.keys():
        listtitle = allPlaylists[playlistkey]
        oc.add(DirectoryObject(key = Callback(PlaylistMenu, title = listtitle, key = playlistkey), title = listtitle))
      
    oc.add(DirectoryObject(key = Callback(MaintenanceMenu, title = L(TEXT_MENU_ACTION_PLAYLIST_MAINTENANCE)), title = L(TEXT_MENU_ACTION_PLAYLIST_MAINTENANCE)))  

    oc.add(PrefsObject(title = L(TEXT_PREFERENCES)))

    return oc


####################################################################################################
## Playlists
####################################################################################################

@route(PREFIX +'/playlistmenu')
def PlaylistMenu(title, key):
    # todo
    oc = ObjectContainer(title2 = title, view_group='List', art = R('icon-default.png'), content = ContainerContent.Tracks, no_cache = True)    
    # load the playlist
    # This is an: etree.Element XML Element 
    playlist = LoadSinglePlaylist(key)
    if playlist != None:
        tracks = playlist.xpath('//Track')
        for track in tracks:
            oc.add(createTrackObject(track))
        return oc
                    
    return showMessage(message_text = L(TEXT_MSG_EMPTY_PLAYLIST) )


def createTrackObject(track):
    title = track.get(ATTR_TITLE)
    key = track.get(ATTR_KEY)
    ratingKey = track.get(ATTR_RATINGKEY)            
    trackObject = TrackObject(title = title, key = pms_main_url + key, rating_key = ratingKey)
    trackObject.duration = attributeAsInt(track.get(ATTR_DURATION))
    #if track.get('art') != None:
    #    to.art = pms_main_url + track.get('art')
    if track.get(ATTR_THUMB) != None:
        trackObject.thumb = pms_main_url + track.get(ATTR_THUMB)
    partkey = track.get(ATTR_PARTKEY)
    mediaObject = MediaObject( parts = [PartObject(key = partkey)] )
    mediaObject.duration = trackObject.duration
    mediaObject.bitrate = attributeAsInt(track.get(ATTR_BITRATE))
    mediaObject.audio_channels = attributeAsInt(track.get(ATTR_AUDIOCHANNELS))
    if track.get(ATTR_AUDIOCODEC) != None:
        mediaObject.audio_codec = track.get(ATTR_AUDIOCODEC)
    if track.get(ATTR_CONTAINER) != None:
        mediaObject.container = track.get(ATTR_CONTAINER)           
    trackObject.add(mediaObject)
    return trackObject


####################################################################################################
# Playlist maintenance
####################################################################################################

@route(PREFIX +'/maintenance')
def MaintenanceMenu(title):
    oc = ObjectContainer(title2 = title, view_group='List')
    newsetting = { NEW_PL_TITLE : 'New playlist', NEW_PL_TYPE : PL_TYPE_SIMPLE, NEW_PL_DESCRIPTION : ''}
    Log.Debug(newsetting[NEW_PL_TITLE])
    oc.add(DirectoryObject(key = Callback(BrowseMusicMenu, title = L(TEXT_MENU_ACTION_ADD_TRACKS)), title = L(TEXT_MENU_ACTION_ADD_TRACKS)))  
    oc.add(DirectoryObject(key = Callback(RemoveTracksMenu, title = L(TEXT_MENU_ACTION_REMOVE_TRACKS)), title = L(TEXT_MENU_ACTION_REMOVE_TRACKS)))  
    oc.add(DirectoryObject(key = Callback(RenamePlaylistMenu, title = L(TEXT_MENU_ACTION_RENAME_PLAYLIST)), title = L(TEXT_MENU_ACTION_RENAME_PLAYLIST)))
    oc.add(DirectoryObject(key = Callback(CreatePlaylistMenu, settings = newsetting), title = L(TEXT_MENU_ACTION_CREATE_PLAYLIST)))  
    oc.add(DirectoryObject(key = Callback(DeletePlaylistMenu, title = L(TEXT_MENU_ACTION_DELETE_PLAYLIST)), title = L(TEXT_MENU_ACTION_DELETE_PLAYLIST)))
    
    return oc

@route(PREFIX +'/createplaylistoptions', settings=dict)
def CreatePlaylistMenu(settings):
    oc = ObjectContainer(title2 = L(TEXT_MENU_ACTION_CREATE_PLAYLIST), view_group='List', no_cache = True, no_history = True)    
    oc.add(InputDirectoryObject(key = Callback(CreatePLSetOption, itype = NEW_PL_TITLE, settings = settings),
                                title = Locale.LocalStringWithFormat(TEXT_MENU_CREATEPL_ENTER_TITLE , settings[NEW_PL_TITLE]),
                                prompt = L(TEXT_MENU_CREATEPL_ENTER_TITLE_PROMPT)))
    oc.add(InputDirectoryObject(key = Callback(CreatePLSetOption, itype = NEW_PL_DESCRIPTION, settings = settings),
                                title = Locale.LocalStringWithFormat(TEXT_MENU_CREATEPL_ENTER_DESCR, settings[NEW_PL_DESCRIPTION]),
                                prompt = L(TEXT_MENU_CREATEPL_ENTER_DESCR_PROMPT)))
    oc.add(PopupDirectoryObject(key = Callback(CreatePLSelectTypeMenu, settings = settings),
                                title = Locale.LocalStringWithFormat(TEXT_MENU_CREATEPL_SELECT_TYPE, settings[NEW_PL_TYPE])))
    oc.add(DirectoryObject(key = Callback(CreatePLCreatePlaylist, settings = settings),
                           title = L(TEXT_MENU_CREATEPL_CREATE_LIST)))  
    return oc

@route(PREFIX +'/setplaylistoption', settings=dict)
def CreatePLSetOption(query, itype, settings):
    settings[itype] = query
    return CreatePlaylistMenu(settings)

@route(PREFIX +'/selectplaylisttype', settings=dict)
def CreatePLSelectTypeMenu(settings):
    oc = ObjectContainer(title2 = L(TEXT_MENU_CREATEPL_SELECT_TYPE_PROMPT), view_group='List', no_cache = True, no_history = True)
    oc.title1 = L(TEXT_MENU_CREATEPL_SELECT_TYPE_PROMPT)
    for playlist_type in PL_TYPES:
        oc.add(DirectoryObject(key = Callback(CreatePLSetOption, query = playlist_type, itype = NEW_PL_TYPE, settings = settings),
                               title = playlist_type))         
    return oc

@route(PREFIX +'/createplaylist', settings=dict)
def CreatePLCreatePlaylist(settings):
    if settings[NEW_PL_TITLE] != None:
        return addPlaylist(settings)
        
    return showMessage(L(TEXT_ERROR_MISSING_TITLE))


@route(PREFIX +'/removetracks')
def RemoveTracksMenu(title):
    return showMessage(message_text = 'TODO: Remove tracks from playlist')
                       
@route(PREFIX +'/renameplaylist')
def RenamePlaylistMenu(title):
    return showMessage(message_text = 'TODO: Rename playlist')

@route(PREFIX +'/deleteplaylist')
def DeletePlaylistMenu(title):
    return showMessage(message_text = 'TODO: Delete playlist')

####################################################################################################
# Browse music sections
####################################################################################################

@route(PREFIX +'/browsemusic')
def BrowseMusicMenu(title):    
    oc = ObjectContainer(title2 = title, view_group='List')
    sectionUrl = pms_main_url + LIBRARY_SECTIONS
    el = XML.ElementFromURL(sectionUrl)
    #Log.Debug('element is "%s"' % XML.StringFromElement(el))

    sections = el.xpath('//Directory[@scanner="Plex Music Scanner"]')	
    for section in sections:	
        title = section.get(ATTR_TITLE)
        key = section.get(ATTR_KEY)
        oc.add(DirectoryObject(key = Callback(BrowseSectionMenu, parentUrl = sectionUrl, title = title, section = key), title = title))
        
    return oc

@route(PREFIX +'/browsesection')
def BrowseSectionMenu(parentUrl, title, section, append_trailing_slash = True):
    oc = ObjectContainer(title2 = title, view_group='List')
  
    sectionUrl = parentUrl + section 
    if append_trailing_slash:
        sectionUrl = sectionUrl + '/'
    el = XML.ElementFromURL(sectionUrl)
    Log.Debug('section element is "%s"' % XML.StringFromElement(el))
  
    viewgroup = el.get(ATTR_VIEWGROUP)
    if (viewgroup == 'track' or firstElement(el, '//Track') != None):
        tracks = el.xpath('//Track')
        for track in tracks:
            title = track.get(ATTR_TITLE)
            key = track.get(ATTR_KEY)
            ratingKey = track.get(ATTR_RATINGKEY)
            oc.add(PopupDirectoryObject(key = Callback(BrowseTrackPopupMenu, key = key, tracktitle = title), title = title))
    else:
        sections = el.xpath('//Directory')	
        for section in sections:	
            title = section.get(ATTR_TITLE)
            key = section.get(ATTR_KEY)
            if attributeAsInt(section.get(ATTR_SEARCH)) != 0:
                oc.add(InputDirectoryObject(key = Callback(SearchMenu, key = section.get(ATTR_KEY), title = section.get(ATTR_PROMPT)),
                                            prompt = section.get(ATTR_PROMPT),
                                            title = section.get(ATTR_TITLE)))
            elif key.startswith('/'):
                oc.add(DirectoryObject(key = Callback(BrowseSectionMenu, parentUrl = pms_main_url, title = title, section = key), title = title))
            else:
                oc.add(DirectoryObject(key = Callback(BrowseSectionMenu, parentUrl = sectionUrl, title = title, section = key), title = title))
  
    return oc     

def SearchMenu(query, key, title):
    if query != None and len(query) > 0:
        return BrowseSectionMenu(parentUrl = pms_main_url,
                                 title = "%s '%s'" % (title, query),
                                 section = '/%s&query=%s' % (key, query),
                                 append_trailing_slash = False)
    return showMessage(L(TEXT_ERROR_EMPTY_SEARCH_QUERY))

@route(PREFIX +'/browsetrack')
def BrowseTrackPopupMenu(key, tracktitle):
    oc = ObjectContainer(title2 = L(TEXT_MENU_TITLE_TRACK_ACTIONS), no_cache = True)
    oc.title1 = L(TEXT_MENU_TITLE_TRACK_ACTIONS)
    
    for playlistkey in allPlaylists.keys():
        listtitle = allPlaylists[playlistkey]
        oc.add(PopupDirectoryObject(key = Callback(addToPlaylist, playlistkey = playlistkey, key = key, tracktitle = tracktitle),
                                    title = listtitle))
    return oc


@route(PREFIX +'/addtoplaylist')
def addToPlaylist(playlistkey, key, tracktitle):
   
    # use key to get the track information
    trackUrl = pms_main_url + key + '/'
    el = XML.ElementFromURL(trackUrl)
    if el == None:
        return showMessage(message_text = Locale.LocalStringWithFormat(TEXT_ERROR_NO_METADATA, key))                      
    Log.Debug('track element is "%s"' % XML.StringFromElement(el))
    track = firstElement(el, '//Track')
    if track == None:
        return showMessage(message_text = Locale.LocalStringWithFormat(TEXT_ERROR_NO_TRACK_FOUND, tracktitle, key))                        
    media = firstElement(track, '//Media')
    if media == None:
        return showMessage(message_text = Locale.LocalStringWithFormat(TEXT_ERROR_NO_MEDIA_FOR_TRACK, tracktitle, key))                
    part = firstElement(media, '//Part')
    if part == None:
        return showMessage(message_text = Locale.LocalStringWithFormat(TEXT_ERROR_NO_TRACK_DATA, tracktitle, key))                

    Log.Debug('adding track to playlist')
    playlist = LoadSinglePlaylist(playlistkey)
    if playlist != None:
        if trackInPlaylist(track.get(ATTR_KEY), playlist) == True:
            return showMessage(message_text = Locale.LocalStringWithFormat(TEXT_MSG_TRACK_ALREADY_IN_PLAYLIST, tracktitle, key))                

        elNewtrack = etree.SubElement(playlist, 'Track')
        # atributes for TrackObject
        elNewtrack.set(ATTR_KEY, track.get(ATTR_KEY))                                                
        elNewtrack.set(ATTR_TITLE, track.get(ATTR_TITLE))
        setAttributeIfPresent(elNewtrack, track, ATTR_RATINGKEY)
        setAttributeIfPresent(elNewtrack, part, ATTR_DURATION)
        setAttributeIfPresent(elNewtrack, track, ATTR_ART)
        setAttributeIfPresent(elNewtrack, track, ATTR_THUMB)
        # additional atributes for MediaObject
        setAttributeIfPresent(elNewtrack, media, ATTR_BITRATE)
        setAttributeIfPresent(elNewtrack, media, ATTR_AUDIOCODEC)
        setAttributeIfPresent(elNewtrack, media, ATTR_AUDIOCHANNELS)
        setAttributeIfPresent(elNewtrack, media, ATTR_CONTAINER)
        # additional atributes for PartObject
        elNewtrack.set(ATTR_PARTKEY, pms_main_url + part.get(ATTR_KEY))
        SaveSinglePlaylist(playlistkey, playlist)
        return showMessage(message_text = Locale.LocalStringWithFormat(TEXT_MSG_TRACK_ADDED_TO_PLAYLIST, track, key, playlistkey))
            
    return showMessage(message_text = L(TEXT_ERROR_TRACK_NOT_ADDED))


####################################################################################################
# Load / Save playlist
####################################################################################################

def loadPlaylists():
    # Load all existing playlists (name only) for the current user
    playlistsName = getPlaylistName()
    allPlaylists = Data.LoadObject(playlistsName)
    if allPlaylists == None:
        allPlaylists = {}
        Data.SaveObject(playlistsName, allPlaylists)

    return allPlaylists


@route(PREFIX +'/addplaylist', settings=dict)
def addPlaylist(settings):
    global allPlaylists
    # Generate a new key!
    if allPlaylists == None:
        allPlaylists = {}
    playlistKey = settings[NEW_PL_TITLE]
    if playlistKey in allPlaylists.keys():
        return showMessage(Locale.LocalStringWithFormat(TEXT_ERROR_PLAYLIST_EXISTS, playlistKey))
    # For now, just set the title. Tobe changed to store the settings object in the allPlaylists dict
    allPlaylists[playlistKey] = playlistKey
    Data.SaveObject(getPlaylistName(), allPlaylists)
    return showMessage(Locale.LocalStringWithFormat(TEXT_MSG_PLAYLIST_CREATED, playlistKey))

@route(PREFIX +'/getplaylistname')
def getPlaylistName():
    username = Prefs[PREFS__USERNAME]
    playlistsName = '%s_allPlaylists' % username
    return playlistsName

def LoadSinglePlaylist(playlistkey):   
    full_filename = GetPlaylistFileName(playlistkey)
    Log.Debug('LoadSinglePlaylist: %s' % full_filename)
    if os.path.isfile(full_filename):
        try:
            tree = etree.parse(full_filename)
            root = tree.getroot()
            return root
        except:            
            return None
    return CreateSinglePlaylist(playlistkey)

def SaveSinglePlaylist(playlistkey, playlist):
    full_filename = GetPlaylistFileName(playlistkey)
    Log.Debug('SaveSinglePlaylist: %s' % full_filename)
    if etree.iselement(playlist):
        try:
            #code
            etree.ElementTree(playlist).write(full_filename, pretty_print = True)
        except Exception:
            pass
    pass    
    
def CreateSinglePlaylist(playlistkey):    
    newplaylist = etree.Element(PLAYLIST_ROOT)
    if newplaylist != None:
        etree.SubElement(newplaylist, ATTR_KEY).text = playlistkey
        etree.SubElement(newplaylist, ATTR_TITLE).text = allPlaylists[playlistkey]
        SaveSinglePlaylist(playlistkey, newplaylist)        
    return newplaylist;


####################################################################################################
# Generic helper functions
####################################################################################################

def setAttributeIfPresent(to_elem, from_elem, attr_name):
    if to_elem != None and from_elem != None and attr_name != None and from_elem.get(attr_name) != None:
        to_elem.set(attr_name, from_elem.get(attr_name))
    pass

def attributeAsInt(attr_value, def_value = 0):
    if attr_value != None:
        try:
            if attr_value.isdigit():
                return int(attr_value)
        except Exception:
            pass
    return def_value

def firstElement(element, query):
    if element != None and query != None:
        try:
            elem = element.xpath(query)
            if elem != None and len(elem) > 0:
                return elem[0]
        except Exception:
            pass
    return None

@route(PREFIX +'/trackinplaylist')
def trackInPlaylist(trackkey, playlist):
    if playlist != None and trackkey != None:
        track = playlist.xpath('//Track[@key="%s"]' % trackkey)
        if track != None and len(track) > 0:
            return True
    return False

def showMessage(message_text):
    return ObjectContainer(header=NAME, message=message_text, no_history = True, no_cache = True)

@route(PREFIX + '/supportpath')
def GetSupportPath(directory, subdirectory = None):
    return Core.storage.join_path(Core.app_support_path, Core.config.plugin_support_dir_name, directory, PLUGIN_DIR, subdirectory)

@route(PREFIX + '/playlistfilename')
def GetPlaylistFileName(playlistkey):
    playlist_filename = '%s - %s.xml' % (Prefs[PREFS__USERNAME], playlistkey)
    return Core.storage.join_path(GetSupportPath('Data', 'DataItems'), playlist_filename)

