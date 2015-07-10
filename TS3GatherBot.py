#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Created by Pierre Schönbeck

    This bot will make it easier to set up gathers, all
    from your teamspeak 3 server.

    The bot requires access to the Teamspeak 3 server
    query!
"""

__author__      = 'Pierre Schönbeck'
__copyright__   = 'Copyright 2015, TS3GatherBot'
__credits__     = ['Pierre Schönbeck']

__licence__     = 'MIT'
__version__     = '1.0.0'
__maintainer__  = 'Pierre Schönbeck'
__status__      = 'Production'

"""
    Bot Thread
"""
import threading
import telnetlib
from Config import config, maps
from queue import Queue

class BotThread(threading.Thread):
    def __init__(self, name, password, channel, index):
        super(BotThread, self).__init__()

        self.commands = {
            "!start": self.cmd_start,
            "!stop": self.cmd_stop,
            "!maps": self.cmd_maps,
            "!ready": self.cmd_ready,
            "!unready": self.cmd_unready,
            "!help": self.cmd_help
        }

        self.name = name
        self.password = password
        self.telnet = None
        self.botId = None
        self.channel = channel
        self.ti = index

    def run(self):
        self.telnet = self.initBot()
        self.botId = self.getBotId()
        self.channel = self.moveToChannel(self.getChannelId(self.channel))

        # Print Welcome message
        self.sendChannelMessage("\\n[b]The GatherBot is currently running[/b]\\n\\n"
                                "[color=green]!start[/color] : [i]Starts a gather[/i]\\n"
                                "[color=green]!stop[/color] : [i]Stops the gather[/i]\\n\\n"
                                "[color=green]!maps[/color] : [i]Set the amount of maps to play (default=bo3)[/i]\\n"
                                "[color=green]!ready[/color] : [i]Sets you as ready[/i]\\n"
                                "[color=green]!unready[/color] : [i]Sets you as unready[/i]\\n\\n"
                                "[color=red]Please type !help for a full list of commands[/color]")

        # While an exit command has not been issued
        ex = False
        while not ex:
            while not cmdToThread[self.ti].empty():
                self.execCommand(cmdToThread[self.ti].get())

            # Read commands from user and execute them
            self.telnet.write(self.getenc("servernotifyregister event=textchannel id=%s\n" % self.channel))
            msg = str(self.telnet.read_until(self.getenc("msg=ok")))
            if msg.__contains__("notifytextmessage"):
                self.execCommand(msg)

        # When the bot is closed, close all connections
        # before exiting thread
        self.closeBot()

    """
        Connects to the teamspeak server via telnet
        and returns the telnet client
    """
    def initBot(self):
        # Connect and log in to server
        telnet = telnetlib.Telnet(config["host"], config["port"])
        telnet.open(telnet.host, telnet.port)
        telnet.write(self.getenc("login %s %s\n" % (self.name, self.password)))
        telnet.read_until(self.getenc("msg=ok"))

        # Select virtual server id
        telnet.write(self.getenc("use sid=%s\n" % (config["sid"])))
        telnet.read_until(self.getenc("msg=ok"))

        # Set bot nickname
        telnet.write(self.getenc("clientupdate client_nickname=%s\n" % (self.name)))
        telnet.read_until(self.getenc("msg=ok"))

        return telnet

    """
        Log out from telnet and close the client
    """
    def closeBot(self):
        self.telnet.write(self.getenc("logout\n"))
        self.telnet.close()
        print("Bot closed")

    """
        Get the client ID for this bot
    """
    def getBotId(self):
        self.telnet.write(self.getenc("clientfind pattern=%s\n" % (self.name)))
        botstr = str(self.telnet.read_until(self.getenc("msg=ok")))
        botstr = botstr.split()[0]
        return int(botstr.split("=")[1])

    """
        Get the channel ID from the name of the channel
    """
    def getChannelId(self, channel):
        channelLobby = channel.replace(" ", "\s")
        self.telnet.write(self.getenc("channelfind pattern=%s\n" % (channelLobby)))
        channelLobby = str(self.telnet.read_until(self.getenc("msg=ok")))
        channelLobby = channelLobby.split("\\n")[1]
        channelLobby = channelLobby.split()[0]
        return int(channelLobby.split("=")[1])

    """
        Move user to channel
    """
    def moveToChannel(self, channel):
        self.telnet.write(self.getenc("clientmove clid=%s cid=%s\n" % (self.botId, channel)))
        self.telnet.read_until(self.getenc("msg=ok"))
        return channel

    """
        Print out a server message
    """
    def sendServerMessage(self, msg):
        msg = msg.replace(" ", "\s")
        self.telnet.write(self.getenc("sendtextmessage targetmode=3 target=1 msg=%s\n" % (msg)))
        self.telnet.read_until(self.getenc("msg=ok"))

    """
        Print a message to a specific channel
    """
    def sendChannelMessage(self, msg):
        msg = msg.replace(" ", "\s")
        self.telnet.write(self.getenc("sendtextmessage targetmode=2 msg=%s\n" % (msg)))
        self.telnet.read_until(self.getenc("msg=ok"))

    def execCommand(self, cmd):
        cmd = [x.split("=") for x in cmd.split() if len(x.split("=")) > 1 and not x.__contains__("msg=ok")]
        d = {}
        for it in cmd:
            d[it[0]] = it[1]
        if d['msg'] in self.commands:
            self.commands[d['msg']](d['invokername'], d['msg'])

    def cmd_start(self, user, data):
        pass

    def cmd_stop(self, user, data):
        pass

    def cmd_maps(self, user, data):
        pass

    def cmd_ready(self, user, data):
        pass

    def cmd_unready(self, user, data):
        pass

    def cmd_help(self, user, data):
        self.sendChannelMessage(
            "[b]Available commands are:[/b]\\n"
            "[color=green]!start[/color] : [i]Starts a gather[/i]\\n"
            "[color=green]!stop[/color] : [i]Stops the gather[/i]\\n\\n"
            "[color=green]!maps[/color] : [i]Set the amount of maps to play (default=bo3)[/i]\\n"
            "[color=green]!ready[/color] : [i]Sets you as ready[/i]\\n"
            "[color=green]!unready[/color] : [i]Sets you as unready[/i]\\n\\n"
            "[color=green]!help[/color] : [i]List all available commands[/i]\\n"
        )

    def getenc(self, str):
        return str.encode('ascii')

"""
    Init the app
"""
players = []

# Create lists with all the bots and their Queues
cmdToThread = [
    Queue(), Queue(), Queue()
]
bots = [
    BotThread(config["user"], config["pass"], config["gl"], 0),
    BotThread(config["user1"], config["pass1"], config["g1"], 1),
    BotThread(config["user2"], config["pass2"], config["g2"], 2)
]

for b in bots:
    b.start()







"""
def getPlayers():
    telnet.write(getenc("clientlist\n"))
    clients = telnet.read_until(getenc("msg=ok"))
    clients = clients.replace(getenc(" "), getenc("\n"))
    clients = clients.replace(getenc("\r"), getenc(""))
    players = clients.split(getenc("|"))
    for p in players:
        try:
            if getenc(config["name"]) in p:
                players.remove(p)
            else:
                p = p.split(getenc("\n"))
                p = filter(None, p)
        except IndexError:
            print("Error")
    return players

commands = {
    "!init_gather": init_gather,
    "!stop": stop_gather
}
"""