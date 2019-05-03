# ArrPush

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
