#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Pierre Schönbeck'

# Bot and channel settings
config = {
    "host": "127.0.0.1",
    "port": "10011",
    "user": "GatherBot1",
    "pass": "xxxx",
    "user1": "GatherBot2",
    "pass1": "xxxx",
    "user2": "GatherBot3",
    "pass2": "xxxx",
    "sid": 1,
    "gl": "Gather-Lobby",
    "g1": "Gather1",
    "g2": "Gather2"
}

# Maps available in gathers
maps = [
    "de_inferno",
    "de_dust2",
    "de_mirage",
    "de_train",
    "de_cbble",
    "de_cache",
    "de_overpass"
]

# b = ban, p = pick
# Last map will always be the remaining one.
vetoprocesses = {
    "bo1": "bbbbbb",
    "bo3": "bbppbb",
    "bo5": "bbpppp"
}

# Teamspeak3 users that will have access to admin commands
admins = {
    "<uid>": "x"
}
