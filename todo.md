# General
* [x] Rename project to reflect multi-app paradigm. Maybe
"media-discord-presence" or something.
* [x] Fancy short name for CLI + Service
* [x] Windows installer using `pynsist` or `pyinstaller`
* [x] Need to make a seperate Discord app for each app we support
* [ ] Setup as a Windows service. If any app we support starts up, we start
monitoring it. We could just check perodically, or perhaps there's a way
for Windows to notify us.
* [x] Configuration via INI/JSON file. Needed to setup as a Windows
service, as well as it adds some flexibility.
* [ ] Improve logging output so we have context if service breaks (take code from ADLES).
* [ ] Add config.ini to Windows EXE build

## Dev
* [ ] Build script to bump version, build installer, tag GitHub release
(like Flask's make-release.py).
* [ ] setup.py
* [ ] Unit tests.
* [x] Upload assets to GitHub.


# Discord
* [ ] Send email asking about Spotify-like integration: gamedevs@discordapp.com
* [ ] Post on dev forum/SO about: UWP app integration
* [ ] Post on dev forum/SO about: Link to open app
* [ ] Work on reverse-engineering the method Discord-Spotify communicate


# Crunchyroll
* [ ] Upload Crunchyroll assets for small and large images in presence
* [ ] Subclass for crunchyroll

## Playback
* [ ] Title of currently playing episode
* [ ] Current time in episode
* [ ] Show name
* [ ] Season name
* [ ] Show artwork


# Funimation
* [ ] Get the current time of whatever's playing (need to dive into memory for this most likely)
* [ ] Get the playing state (paused/playing)
* [ ] Setup Transparent HTTPS proxy. Want to see if I can figure out Funimation's API (if it exists...)

## Playback
* [ ] Title of currently playing episode
* [ ] Current time in episode
* [ ] Show name
* [ ] Season name
* [ ] Show artwork


# Stretch/Long term
* [ ] GitHub.io page with documentation and downloads.
* [ ] Publish to PyPI as a package (Easier install).
* [ ] Make core functionality a seperate PyPI package with an API, so others
can use it as a way to interact with UWP apps and write their own rich
presence clients. Have the Windows service and CLI use that package.
* [ ] Automated runs of unit tests using Appveyor.
