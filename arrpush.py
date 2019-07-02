#!/usr/bin/env python3
"""
    #########################################################################
    # Title:      ArrPush                                                   #
    # Author:     l3uddz                                                    #
    # URL:        https://github.com/l3uddz/arrpush                         #
    # --                                                                    #
    #########################################################################
    #                   GNU General Public License v3.0                     #
    #########################################################################

"""

import logging
import os
import re
import string
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from urllib.parse import urljoin

import requests
import urllib3

############################################################
# INIT
############################################################

# Logging

log_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)-10s - %(name)-20s - %(funcName)-30s - %(message)s')
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# disable loggers
logging.getLogger('urllib3').setLevel(logging.ERROR)
urllib3.disable_warnings()

# Set console logger
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

# Set file logger
file_handler = RotatingFileHandler(
    os.path.join(os.path.dirname(sys.argv[0]), "arrpush.log"),
    maxBytes=1024 * 1024 * 5,
    backupCount=5
)
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

# Set logging level
root_logger.setLevel(logging.DEBUG)
log = root_logger.getChild('arrpush')

# Indexer Settings
parse_name_from_indexers = [
    'passthepopcorn',
    'nebulance'
]


############################################################
# BDECODE
# https://github.com/utdemir/bencoder/blob/master/bencoder.py
############################################################

def decode(s):
    def decode_first(s):
        if s.startswith(b"i"):
            match = re.match(b"i(-?\\d+)e", s)
            return int(match.group(1)), s[match.span()[1]:]
        elif s.startswith(b"l") or s.startswith(b"d"):
            l = []
            rest = s[1:]
            while not rest.startswith(b"e"):
                elem, rest = decode_first(rest)
                l.append(elem)
            rest = rest[1:]
            if s.startswith(b"l"):
                return l, rest
            else:
                return {i: j for i, j in zip(l[::2], l[1::2])}, rest
        elif any(s.startswith(i.encode()) for i in string.digits):
            m = re.match(b"(\\d+):", s)
            length = int(m.group(1))
            rest_i = m.span()[1]
            start = rest_i
            end = rest_i + length
            return s[start:end], s[end:]
        else:
            raise ValueError("Malformed input.")

    if isinstance(s, str):
        s = s.encode("ascii")

    ret, rest = decode_first(s)
    if rest:
        raise ValueError("Malformed input.")
    return ret


############################################################
# MISC
############################################################


def get_torrent_content_from_url(torrent_url):
    try:
        # retrieve torrent url data
        response = requests.get(torrent_url, timeout=30, verify=False)
        if response.status_code == 200:
            return response.content

        log.error("Failed to retrieve torrent data from %s", torrent_url)
        return None
    except Exception:
        log.exception("Exception retrieving torrent data from %s: ",
                      torrent_url)
        return None


def get_torrent_content_from_file(torrent_path):
    try:
        # retrieve torrent file data
        with open(torrent_path, 'rb') as torrent_file:
            return torrent_file.read()

        log.error("Failed to retrieve torrent data from %s", torrent_path)
        return None
    except Exception:
        log.exception("Exception retrieving torrent data from %s: ",
                      torrent_path)
        return None


def get_torrent_name(torrent_content):
    decoded_torrent_data = {}

    try:
        # decode bencoded torrent file
        decoded_torrent_data = decode(torrent_content)
        if b'info' not in decoded_torrent_data or b'name' not in decoded_torrent_data[b'info']:
            log.exception("Failed to parse torrent name: ")
            return None
    except Exception:
        log.exception("Exception parsing torrent data: ")

    try:
        parsed_torrent_name = decoded_torrent_data[b'info'][b'name'].decode()
        log.info("Retrieved torrent name: %s", parsed_torrent_name)
        return parsed_torrent_name
    except Exception:
        log.error("Exception parsing torrent name: ")
    return None


# https://stackoverflow.com/a/40347452
def get_bytes(size, suffix):
    size = int(float(size))
    suffix = suffix.lower()

    if suffix == 'kb' or suffix == 'kib':
        return size << 10
    elif suffix == 'mb' or suffix == 'mib':
        return size << 20
    elif suffix == 'gb' or suffix == 'gib':
        return size << 30
    return False


def push_release(arr_url, arr_api_key, download_url, title, size, indexer):
    try:
        tries = 0

        # build payload and headers
        payload = {'title': title,
                   'downloadUrl': download_url,
                   'size': str(size),
                   'indexer': indexer,
                   'downloadProtocol': 'torrent',
                   'protocol': 'torrent',
                   'publishDate': datetime.now().isoformat(timespec='seconds')}
        headers = {'Content-Type': 'application/json',
                   'X-Api-Key': arr_api_key}

        while tries < 5:
            tries += 1

            # make request
            req = requests.post(urljoin(arr_url, 'api/release/push'), json=payload, headers=headers, timeout=60,
                                verify=False)
            if req.status_code == 200:
                log.info("Successfully pushed %s (%s) to %s", title, indexer, arr_url)
                return True

            log.error("Failed pushing %s (%s) to %s, Attempt %d/5. Response status_code: %d, response text:\n%s", title,
                      download_url, arr_url, tries, req.status_code, req.text)
            time.sleep(10)

        return False
    except Exception:
        log.error("Exception pushing %s to %s: ", download_url, arr_url)
    return False


############################################################
# MAIN
############################################################

if __name__ == "__main__":
    # parse args
    if len(sys.argv) < 7:
        log.error("Not enough arguments were supplied: %s", sys.argv)
        sys.exit(1)

    try:
        service_url = sys.argv[1]
        service_api_key = sys.argv[2]
        torrent_name = sys.argv[3]
        torrent_url = sys.argv[4]
        torrent_tracker = sys.argv[6]

        # get size in bytes
        torrent_size, torrent_size_type = sys.argv[5].split()
        torrent_size = get_bytes(torrent_size, torrent_size_type)
    except Exception:
        log.exception("Failed parsing arguments supplied %s: ", sys.argv)
        sys.exit(1)

    if torrent_tracker.lower() in parse_name_from_indexers:
        # get torrent name from torrent file for specific trackers
        if len(sys.argv) == 8:
            torrent_path = sys.argv[7]
            torrent_content = get_torrent_content_from_file(torrent_path)
            log.info("Retrieved Torrent Content from : %s", torrent_path)
        else:
            torrent_content = get_torrent_content_from_url(torrent_url)
            log.info("Retrieved Torrent Content from : %s", torrent_url)

        tmp = get_torrent_name(torrent_content) if torrent_content else None
        torrent_name = sys.argv[3] if not tmp else tmp

    # send to sonarr/radarr
    if push_release(service_url, service_api_key, torrent_url, torrent_name, torrent_size, torrent_tracker):
        sys.exit(0)
    else:
        sys.exit(1)
