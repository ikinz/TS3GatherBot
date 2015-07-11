#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Pierre Schönbeck'

class Player:
    def __init__(self, name, uid, isMod = False):
        self.uid = uid
        self.name = name
        self.isMod = isMod

    def __repr__(self):
        return "%s : %s : %s" % (self.name, self.uid, self.isMod)