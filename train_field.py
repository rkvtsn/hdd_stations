#!/usr/bin/env python
# coding=utf-8
import sarge

#     "tgtadm --lld iscsi --mode target --op show"
#     "lvscan"
#     "vgscan"

ONLINE_TAG_BEGIN = "I_T nexus information:"
ONLINE_TAG_END = "LUN information:"

#
# def cmd_stations_status():
#     with open('tgtadm_list.txt') as fp:
#         return fp.read()

def cmd_stations_status():
    p = sarge.run("tgtadm --lld iscsi --mode target --op show", stdout=sarge.Capture())
    if p.returncode != 0:
        raise IOError()
    return p.stdout.read().decode('unicode_escape')


def refresh_stations_status():
    stations = {}
    cmd_text = cmd_stations_status()
    targets = list(filter(bool, cmd_text.replace('Target', '#Target').split('#')))
    for t in targets:
        target = [x.strip() for x in t.split('\n')]
        target_name, _, name = target[0].split(':')
        begin = t.find(ONLINE_TAG_BEGIN)
        end = t.find(ONLINE_TAG_END)
        online_information = t[begin + len(ONLINE_TAG_BEGIN):end]
        stations[name] = not online_information.strip
    return stations


print(refresh_stations_status())
