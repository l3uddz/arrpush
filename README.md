# ARRpush

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%203-blue.svg)](https://github.com/l3uddz/plex_autoscan/blob/master/LICENSE.md)

---

Use ruTorrent to send autodl-irssi feeds to Sonarr/Radarr.

## Dependencies

### RuTorrent (native)

Debian based distros:

```
sudo apt-get install python3
python3 -m pip install requests urllib3
```


### RuTorrent (docker)

Assumes container name is `rutorrent`.

```
docker exec -it rutorrent apk update
docker exec -it rutorrent apk add python3
docker exec -it rutorrent python3 -m pip install requests urllib3
```

## Install


1. Clone Project:

   ```
   git clone https://github.com/l3uddz/arrpush /opt/arrpush
   ```

1. Set permissions:

   ```
   chmod a+x /opt/arrpush/arrpush.py
   ```

## Setup

- Add and enable **autodl-irssi plugin** in ruTorrent.

- Add the following **ruTorrent Filter Action**:

  - **Run Program:** `/opt/arrpush/arrpush.py`

  - **Run Arguments:** `"SONARR OR RADARR URL" "API_KEY" "$(TorrentName)" "$(TorrentUrl)" "$(TorrentSize)" "$(Tracker)"`

  - **IF USING PTP or NEBULANCE**, Use the following **Run Arguments:** `"SONARR OR RADARR URL" "API_KEY" "$(TorrentName)" "$(TorrentUrl)" "$(TorrentSize)" "$(Tracker)" "$(TorrentPathName)"`

## Known Issues / Limitations

- ARRpush does not have a way to get a releases name and size from PTP and Nebulance IRC announcements without having to download and extract the torrent file itself. This may lead to high .torrent download usage for these trackers. To work around this, use filters to reduce what ARRpush pushes to Sonarr/Radarr.
