# TODO list
* Figure out how to use the episode ID to get more useful information about what's playing.
* Setup this app as a Windows service. It could either just check perodically for the Funimation process,
      or I could investigate if there's a way for the OS to wake us up somehow.
* Get the current time of whatever's playing (need to dive into memory for this most likely)
* Get the playing state (paused/playing)
* Setup Transparent HTTPS proxy. Want to see if I can figure out Funimation's API (if it exists...)

## Stuff we need the "Spotify" rich API for
* Send email asking about Spotify-like integration: gamedevs@discordapp.com
* Link to open app
* Link to open the specific episode in the app


# Notes
Want to follow Discord's recommendations as much as possible here
https://discordapp.com/developers/docs/rich-presence/best-practices
Ideal status information
  Show name
  Season number
  Episode number
  Episode name
  Start time, current time, or end time (so we can show elapsed/remaining using startTimestamp/endTimestamp) 

Example:
```
  Funimation
  Full Metal Panic!
  S2 E9 | Her Problem
  Elapsed: 6:03
```

Format:
* App name
* Details (this will wrap lines)
* Status (string)
* start (int)

Other useful information that might be excessive, but let's see if we can get it
* Season name


# Funimation

## Assets
* funimation_logo_large
* funimation_logo_small
* full_metal_panic_large

I suspect the episode "id" is incremented by two per episode since there may be two audo languages, English and Japanese.
The app doesn't make it easy to switch languages, however, so don't have a easy way to validate this hypothesis.
Either way, we can get the language from the filename.

File Path example:
```
\\AppData\\Local\\Packages\\FunimationProductionsLTD.FunimationNow_nat5s4eq2a0cr\\AC\\INetHistory
\\mms\\HUOPOA32\\1345116_English_431a16b9-c95a-e711-8175-020165574d09[1].dat
```

## Some examples
* Star Blazers 2202 Episode 6: 1757485 (English)
* Full Metal Panic Season 2 Episode 4: 1345116 (English)
* Full Metal Panic Season 2 Episode 7: 1345122 (English)
* Full Metal Panic Season 2 Episode 8: 1345124 (English)
* Full Metal Panic Season 2 Episode 9: 1345126 (English)
* Full Metal Panic Season 2 Episode 10: 1345128 (English)
* Full Metal Panic Season 3 Episode 1: 1755434 (English)

## Looking at the servers
Homepage IP (nslookup funimation.com): 107.154.106.169

No episode playing:
  172.217.12.14 - This is a Google analytics server

Playing episodes:
*  107.154.108.80:443
*  143.204.31.65:443
*  172.217.12.14:80
*  172.217.12.4:443
*  38.122.56.118:443

# Code snippets

```python
from pprint import pprint
print(process)
pprint(process.open_files())
pprint(process.connections('all'))
print(process.exe())
print(process.cwd())
print(process.cmdline())
```

There seems to be some...interesting permissions on the executable,
making it only spawnable by Ye Olde svchost. Will likely need to
open it the "canonical" way, whatever that is for UWP apps.

```python
cmdline = process.cmdline()
logging.debug("Program cmdline: %s", ' '.join(cmdline))
```
