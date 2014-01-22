SteamBMC
========

Essentially this lets you play and launch any installed Steam game on your system. It also fetches artwork and logo images from the Steam server. No messing around with custom Advanced Launchers -- this handles everything automatically, and will fetch new games as they are added to your Steam account. It integrates into XBMC, unlike Big Picture. It's buggy, unlike Big Picture. Hopefully the last one will change.

### Features
- Automatically downloads the list of owned games from SteamCommunity.com
- Launch games with a single click, all within XBMC
- Downloads artwork where available (background fanart and logo)
- Pretty fast to launch games, faster than waiting for the Steam client to start

### Known Bugs
- If an artwork download is in progress and XBMC is quit, the download will continue until all art has been downloaded, even if the XBMC window is gone. This leaves XBMC hanging at 100% CPU on shutdown in some cases, though it does eventually finish after art has been fully downloaded.
- There are compatibility issues (it doesn't open the games page) with 12.0, or at least my install of 12.0. Use of 12.2 is recommended.
- "Border Art" is buggy, and only currently works for wide logo scaling. Don't use it unless you HAVE to (some skins like to scale artwork out of aspect ratio. Most are fairly good with not doing this in my experience.)
- "Playback Failed" may appear in some cases, even if the game launches successfully. This appears to be related to some kind of internal XBMC time out. If the Steam.exe process does not fork quick enough, XBMC thinks the playback was unsuccessful.


### To-Do
- Multiple Steam profiles (different Steam accounts with different games), perhaps with dynamic user-switching (all games in one page, from multiple accounts, with it logging into a different Steam account for each.)
- Full Linux/OS X support. Coming shortly.
- Game time, game ratings, game summaries, etc. Skeleton code for fetching game play time, but nothing more.
- Cache games list -- avoid fetching too often.
- Ability to hide games not wanted on the list.
- Group games into categories e.g. Kid Friendly. (Maybe...)
- Add your own fanart.
- Select higher resolution fanart if available. (Currently, the code only finds the first fanart available, which may be crusty and low resolution. Try and find a 720p/1080p background, if available.)
- Changing the public URL doesn't get reflected after you leave the settings dialog. You need to leave the addon then enter it again to refresh that.

### Compatability
Currently **Windows only.** However, Linux and Mac OS X support will be added soon.


### License
Licensed under GPLv2. See the LICENSE file for more information.