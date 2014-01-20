"""
Interface with SteamCommunity.com and SteamPowered.com to get owned games and fanart.
Copyright (C) 2013 T. Oldbury

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
"""

import urllib, urllib2
import xml.sax
import os, shutil, sys, time, random
import xbmc, xbmcaddon
from PIL import Image
# Import appropriate apputils
if sys.platform.startswith("win"):
    import winutils as _coreapputils
else:
    raise RuntimeError, "platform `%s' not yet supported... sorry!" % sys.platform
    
addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
lang = addon.getLocalizedString

USERDATA_FOLDER = xbmc.translatePath(os.path.join("special://masterprofile", "addon_data", addon_name))
ARTWORK_CACHE_FOLDER = os.path.join(USERDATA_FOLDER, "artworkcache")
STEAM_BIN = addon.getSetting("steam_bin")

XBMC_WIDEBANNERSIZE = (758, 140)
XBMC_TALLICONSIZE = (256, 256)

"""
steamCheck:     Start Steam in the background if it is not already running.

TODO: Add support for auto log in.
"""
def steamCheck():
    _coreapputils.launchFork("\"%s\" -silent" % STEAM_BIN.replace('"', '\"'))

"""
getValveCdn:    Return a random cdn number for steampowered.com

@return         (string) Single character, currently between 2 and 3, unless Valve adds
                more or changes CDN numbering.
"""
def getValveCdn():
    return str(random.randrange(2, 3))

"""
getUrlReq:      Make a request for a URL over HTTP, and return the contents.

@return         A string of data, or None if the request failed.
"""
def getUrlReq(url):
    try:
        req = urllib2.Request(url)
        # We pretend to be Chrome to get a normal web page, not some optimised Googlebot page.
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22')
        data = urllib2.urlopen(req).read()
        return data
    except urllib2.HTTPError:
        return None

"""
saveUrlReq:     Make a request for a URL over HTTP, and save the result to a file.

@note           Not suitable for large files as data is stored in RAM while the
                transfer is in progress.

@return         True if successful, False if not.
"""
def saveUrlReq(url, save_as):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22')
        remote = urllib2.urlopen(req)
    except urllib2.HTTPError:
        return False
    try:
        shutil.copyfileobj(remote, open(save_as, "wb"))
    except IOError:
        return False

"""
tryUrlReq:      Make a request for a URL over HTTP. If an error occurs, an exception
                is raised. No data is returned.

@return         A string of data, or None if the request failed.
"""
def tryUrlReq(url):
    urllib2.urlopen(urllib2.Request(url))

"""
checkUrl:       Check if a URL has content behind it (data)

@return         True if content available, False if not
"""
def checkUrl(url):
    try:
        urllib2.urlopen(urllib2.Request(url))
    except urllib2.URLError:
        return False
    return True

"""
borderArt:      Make the artwork as big as possible, and add a transparent border around
                any empty areas.

@param          Filename to resize (in place)

@param          Output size to create

@param          (optional) Output format, defaults to "JPEG".

@param          (optional) Resize algorithm; defaults to PIL.Image.BICUBIC (See PIL docs)

@fixme          Buggy for some image sizes; not currently used.
"""
def borderArt(filename, out_size, outfmt="JPEG", filt=Image.BICUBIC):
    # Load the artwork file
    im = Image.open(filename)
    if im.size[1] > im.size[0]:
        ratio_wh = im.size[0] / im.size[1]
        new_width = ratio_wh * out_size[1]
        im = im.resize((new_width, out_size[1]), filt)
        im_out = Image.new("RGBA", out_size, (0, 0, 0, 0))
        left_x = (out_size[0] / 2) - (new_width / 2)
        im_out.paste(im, (left_x, 0))
    else:
        ratio_hw = im.size[1] / im.size[0]
        new_height = ratio_hw * out_size[0]
        im = im.resize((out_size[0], new_height), filt)
        im_out = Image.new("RGBA", out_size, (0, 0, 0, 0))
        top_y = (out_size[1] / 2) - (new_height / 2)
        im_out.paste(im, (0, top_y))
    # Save output over original
    im_out.save(filename, outfmt)

class SteamGameInfoParser(xml.sax.ContentHandler):
    """
    SteamGameInfoParser:	SAX parsing engine for Steam user game info (XML)
    """
    state = 0
    data = ""
    games = []
    
    def characters(self, data):
        self.data += data
    
    def startElement(self, name, attrs):
        if name == "game":
            self.state = 1 # begin listening
            self.games.append({})
            self.data = ""
    
    def endElement(self, name):
        # Are we reading game info?
        if self.state == 1:
            # Add the attribute
            self.games[-1][name] = self.data
            self.data = ""

class SteamGame(object):
    """
    __init__: Create a basic game api entry with the minimum required information.
    
    @param          game_id             Steam unique ID for this game
    
    @param          game_name           Promoted full game name (for example "Half-Life 2: Episode One")
    """
    def __init__(self, game_id, game_name):
        self.game_id = game_id
        self.game_name = game_name
        self.game_logo = ""
        # Steam Community stats only... not YET used
        self.hours_played = 0.0
        self.hours_played_last2weeks = 0.0
        # Artwork
        self.artwork_promo = []
        self.artwork_logo = []
    
    """
    setPlayTime: Set the playtime stats.
    
    @param          hours_played        (optional) Total hours played, defaults to 0.0.
    
    @param          hours_played_2wk    (optional) Hours played in last two weeks, defaults to 0.0.
    """
    def setPlayTime(self, hours_played=0.0, hours_played_last2weeks=0.0):
        self.hours_played = hours_played
        self.hours_played_last2weeks = hours_played_last2weeks
    
    """
    scrapeArtworkSteam: Attempt to download artwork available for this game.
    
    @param          artwork_type        Artwork type. One of: "promo" or "logo"
    
    @return         True if successful, False if failed
    """
    def scrapeArtworkSteam(self, artwork_type):
        if artwork_type == "promo":
            # Get the first promo item (todo: get all and let user choose)
            # These are called screenshots but appear to be Valve-chosen so we call them "promo" images
            data = getUrlReq('http://store.steampowered.com/app/' + str(self.game_id) + '/')
            pos_div = data.find('<div class="screenshot_holder">')
            if pos_div != -1:
                pos_url = data[pos_div:].find('<a href="')
                # 9: the length of the tag string
                pos_end = data[pos_url + pos_div + 9:].find('"')
                url = data[pos_div + pos_url + 9:pos_div + pos_url + pos_end]
            else:
                return False
        elif artwork_type == "logo":
            # Get the game's logo. Not all games have a logo.
            url = 'http://cdn' + getValveCdn() + '.steampowered.com/v/gfx/apps/' + str(self.game_id) + '/header.jpg'
            if not checkUrl(url):
                return False
        else:
            return False # Should we raise an exception?
        # Using the URL, download the file.
        save_as = os.path.join(ARTWORK_CACHE_FOLDER, "game_%d_%s_1.jpg" % (self.game_id, artwork_type))
        saveUrlReq(url, save_as)
        if artwork_type == "logo":
            save_as_png = os.path.join(ARTWORK_CACHE_FOLDER, "game_%d_%s_1.png" % (self.game_id, artwork_type))
            if addon.getSetting("artwork_addborder") == "true":
                if addon.getSetting("artwork_logosize") == 0:
                    sz = XBMC_WIDEBANNERSIZE
                else:
                    sz = XBMC_TALLICONSIZE
                borderArt(save_as, sz, "PNG")
                shutil.move(save_as, save_as_png)
            else:
                # We convert to PNG even if we do not add borders
                Image.open(save_as).save(save_as_png)
                os.remove(save_as) # Delete original
        return True

    """
    scrapeUncachedArtwork:  Check if artwork files are available in the cache;
                            if they are, setup internal artwork links, if not,
                            download them, then setup the links.
    
    @param                  art_update: If True, update art even if cache is fresh.
    """
    def scrapeUncachedArtwork(self, art_update=False):
        # Generate the filename, check if it exists
        xbmc.log("Checking artwork for #%d" % self.game_id, xbmc.LOGDEBUG)
        fn = os.path.join(ARTWORK_CACHE_FOLDER, "game_%d_logo_1.png" % self.game_id)
        if not os.path.exists(fn) or art_update:
            xbmc.log("Downloading logo art...", xbmc.LOGDEBUG)
            self.scrapeArtworkSteam("logo")
        self.artwork_logo = [fn]
        # Repeat for promo art (fanart)
        fn = os.path.join(ARTWORK_CACHE_FOLDER, "game_%d_promo_1.jpg" % self.game_id)
        if not os.path.exists(fn) or art_update:
            xbmc.log("Downloading promo art...", xbmc.LOGDEBUG)
            self.scrapeArtworkSteam("promo")
        self.artwork_promo = [fn]

    """
    launchGame:	Launch this game using Steam. Takes account of platform.
    
    @return     True if believed successful, False if not
    """
    def launchGame(self):
        _coreapputils.launchFork("\"%s\" -applaunch %d" % (STEAM_BIN.replace('"', '\"'), self.game_id))
        time.sleep(5) # Give Steam a few seconds to start.
        if os.path.basename(STEAM_BIN) not in _coreapputils.getProcessesList():
            return False
        return True

class SteamCommunityIfc(object):
    """
    __init__: Create the interface.
    
    @param      public_name     Public name is set up in the Steam profile and 
                                can be the same as the Steam user's name or to
                                whatever they like, but it must be unique and
                                present.
    """
    def __init__(self, public_name):
        assert len(public_name) != 0
        self._public_name = public_name
        self.owned_games = []
        self.http_code = -1
    
    """
    checkSteamConnectivity: Can we connect to SteamCommunity.com?
    
    @return         True if we can, False if not. If False, HTTP error string
                    is updated.
    """
    def checkSteamConnectivity(self):
        try:
            tryUrlReq('http://steamcommunity.com')
        except urllib2.HTTPError, e:
            self.http_code = e.code
            return False
        except urllib2.URLError, e:
            self.http_code = 1001 # URLError code
            return False
        return True
    
    """
    getOwnedGames: Download and create the owned games list. 
    
    @param          get_art: Get art (for new, or if art_update True, always)
                    Setting to False allows for a fast update, but artwork data
                    will be missing (so not suitable for home screen.)
   
    @param          art_update: If True, update art even if cache is fresh
    
    @param          prog_callback: xbmcgui.ProgressDialog to update progress
                    status during the data fetch
    
    @return         True if successful, false if failed.
                    (List can be read back later through other functions.)
    """
    def getOwnedGames(self, get_art=True, art_update=False, prog_callback=None):
        if hasattr(prog_callback, "update"): 
            prog_callback.update(10, lang(33012))
        data = getUrlReq('http://steamcommunity.com/id/' + self._public_name + '/games?tab=all&xml=1')
        if data == None:
            raise RuntimeError, "Can't connect to SteamCommunity.com for games list"
        if hasattr(prog_callback, "update"): 
            prog_callback.update(15, lang(33013))
        sax_engine = SteamGameInfoParser()
        xml.sax.parseString(data, sax_engine)
        # Import the game data: create a new SteamGame for each entry.
        num_games = len(sax_engine.games)
        num = 0
        for game_info in sax_engine.games:
            if hasattr(prog_callback, "update"):
                # We don't get here with zero games, so we're not worried about a divide by zero error.
                prog_callback.update(15 + int((float(num) / float(num_games)) * 85), lang(33014) % game_info['name'].strip())
                if prog_callback.iscanceled():
                    # If cancelled abort fetch of all games so we don't get an inconsistent list
                    self.owned_games = []
                    break
            game = SteamGame(int(game_info['appID']), game_info['name'].strip().encode('utf-8'))
            if 'hoursLast2Weeks' in game_info and 'hoursOnRecord' in game_info:
                game.setPlayTime(float(game_info['hoursLast2Weeks']), float(game_info['hoursOnRecord']))
            else:
                xbmc.log("Note: Game time specified via alternate means -- not yet implemented (FIXME)", xbmc.LOGNOTICE)
            if get_art:
                game.scrapeUncachedArtwork(art_update)
            self.owned_games.append(game)
            num += 1
