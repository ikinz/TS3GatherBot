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

# Amount of players needed to start gather (even number please :))
PLAYERS_NEEDED = 4

"""
    Bot Thread
"""
import threading
import telnetlib
from Config import config, maps, admins, vetoprocesses
from queue import Queue
from Player import Player

class BotThread(threading.Thread):
    def __init__(self, name, password, channel, index):
        super(BotThread, self).__init__()

        self.commands = {
            # User commands
            "!start": self.cmd_start,
            "!stop": self.cmd_stop,
            "!maps": self.cmd_maps,
            "!ready": self.cmd_ready,
            "!r": self.cmd_ready,
            "!gaben": self.cmd_ready,
            "!unready": self.cmd_unready,
            "!notready": self.cmd_unready,
            "!nr": self.cmd_unready,
            "!ur": self.cmd_unready,
            "!help": self.cmd_help,
            "!h": self.cmd_help,

            # Admin commands
            "!activate": self.cmd_activate
        }

        self.name = name
        self.password = password
        self.telnet = None
        self.botId = None
        self.channel = channel
        self.ti = index

    def run(self):
        self.telnet = self.initBot()
        self.botId = self.getPlayerId(self.name)
        self.channel = self.moveToChannel(self.getChannelId(self.channel))

        # Print Welcome message
        self.sendChannelMessage(
            "\\n[b]The GatherBot is currently running[/b]\\n\\n"
            "[color=green]!start[/color] : [i]Starts a gather[/i]\\n"
            "[color=green]!stop[/color] : [i]Stops the gather[/i]\\n\\n"
            "[color=green]!maps[/color] : [i]Set the amount of maps to play (default=bo3)[/i]\\n"
            "[color=green]!ready[/color] : [i]Sets you as ready[/i]\\n"
            "[color=green]!unready[/color] : [i]Sets you as unready[/i]\\n\\n"
            "[color=red]Please type !help for a full list of commands[/color]"
        )

        # While an exit command has not been issued
        ex = False
        while not ex:
            while not cmdToThread[self.ti].empty():
                #self.execCommand(cmdToThread[self.ti].get())
                self.sendChannelMessage(cmdToThread[self.ti].get())

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
    def getPlayerId(self, name):
        self.telnet.write(self.getenc("clientfind pattern=%s\n" % name))
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

    def getPlayersInLobby(self):
        pass

    def execCommand(self, cmd):
        i1 = cmd.index("invokeruid")
        i1 = cmd.index("=", i1)
        i2 = cmd.index("\\n", i1)
        userid = cmd[i1 + 1:i2]
        cmd = [x.split("=") for x in cmd.split() if len(x.split("=")) > 1 and not x.__contains__("msg=ok")]
        d = {}
        for it in cmd:
            d[it[0]] = it[1]
        global active
        cmdsp = d['msg'].split("\\\\s")
        if (cmdsp[0] in self.commands and active) or d['msg'] == '!activate':
            self.commands[cmdsp[0]](userid, d['invokername'], d['msg'])

    def cmd_start(self, userid, user, data):
        global gatherRunning
        if not gatherRunning:
            gatherRunning = True
            global players
            players.append(Player(user, userid, True))

            broadcastMessage("[color=green]A gather has been started by %s![/color]" % user)
        else:
            self.sendChannelMessage("[color=red]A gather is already running![/color]")

    def cmd_stop(self, userid, user, data):
        global gatherRunning
        global players
        p = None
        for x in players:
            if x.uid == userid:
                p = x
        if gatherRunning and p.isMod:
            gatherRunning = False
            global vetoSystem
            vetoSystem = "bo3"

            # Move all players to Lobby
            plrs = ["clid=" + str(self.getPlayerId(x.name)) for x in players]
            plrs = "|".join(plrs)
            self.telnet.write(self.getenc("clientmove %s cid=%s\n" % (plrs, self.getChannelId(config['gl']))))
            self.telnet.read_until(self.getenc("msg=ok"))

            players = []

            broadcastMessage("[color=red]Gather has been stopped![/color]")
        else:
            self.sendChannelMessage("[color=red]No gather currently running![/color]")

    """
        Change the amount of maps that will be played
        Only available to game mods!
    """
    def cmd_maps(self, userid, user, data):
        global gatherRunning
        if gatherRunning:
            data = data.split("\\\\s")
            global players
            p = None
            for x in players:
                if x.uid == userid:
                    p = x
            if len(data) > 1 and p.isMod:
                data = data[1].lower()
                if data in vetoprocesses:
                    global vetoSystem
                    vetoSystem = data
                    broadcastMessage("[color=green]Game changed to %s![/color]" % data)
                else:
                    self.sendChannelMessage("[color=red]%s not supported![/color]" % data)
            else:
                self.sendChannelMessage("[color=red]You didn't enter a value or you're not the game mod![/color]" % data)
        else:
            self.sendChannelMessage("[color=red]No gather currently running![/color]")

    def cmd_ready(self, userid, user, data):
        global gatherRunning
        if gatherRunning:
            global players
            alreadyReady = False
            for p in players:
                if p.uid == userid:
                    alreadyReady = True

            if not alreadyReady:
                players.append(Player(user, userid))
                broadcastMessage("[color=green]%s is ready![/color]" % user)
                self.start_gather()
            else:
                self.sendChannelMessage("[color=red]You're already ready![/color]")
        else:
            self.sendChannelMessage("[color=red]No gather currently running![/color]")

    def start_gather(self):
        global players
        if len(players) == PLAYERS_NEEDED:
            broadcastMessage("[color=green]%s players are ready! Setting up teams![/color]" % PLAYERS_NEEDED)
            l = players[:]
            import random
            random.shuffle(l)
            team1 = l[:int(PLAYERS_NEEDED/2)]
            team2 = l[int(PLAYERS_NEEDED/2):]

            plrs = ["clid=" + str(self.getPlayerId(x.name)) for x in team1]
            plrs = "|".join(plrs)
            self.telnet.write(self.getenc("clientmove %s cid=%s\n" % (plrs, self.getChannelId(config['g1']))))
            self.telnet.read_until(self.getenc("msg=ok"))
            plrs = ["clid=" + str(self.getPlayerId(x.name)) for x in team2]
            plrs = "|".join(plrs)
            self.telnet.write(self.getenc("clientmove %s cid=%s\n" % (plrs, self.getChannelId(config['g2']))))
            self.telnet.read_until(self.getenc("msg=ok"))

    def cmd_unready(self, userid, user, data):
        global gatherRunning
        if gatherRunning:
            global players
            for p in players:
                if p.uid == userid:
                    if p.isMod:
                        self.sendChannelMessage("[color=red]You can't leave your own gather. Use !stop to cancel it instead![/color]")
                    else:
                        players.remove(p)
        else:
            self.sendChannelMessage("[color=red]No gather currently running![/color]")

    def cmd_help(self, userid, user, data):
        string = "\\n[b]Available commands are:[/b]\\n" \
            "[color=grey]!<cmd> (<aliases>) : [i]<Description>[/i][/color]\\n\\n" \
            "[color=green]!start[/color] : [i]Starts a gather[/i]\\n" \
            "[color=green]!stop[/color] : [i]Stops the gather[/i]\\n\\n" \
            "[color=green]!maps[/color] : [i]Set the amount of maps to play (default=bo3)[/i]\\n" \
            "[color=green]!ready (!r, !gaben)[/color] : [i]Sets you as ready[/i]\\n" \
            "[color=green]!unready (!notready, !nr, !ur)[/color] : [i]Sets you as unready[/i]\\n\\n" \
            "[color=green]!help (!h)[/color] : [i]List all available commands[/i]\\n"

        if userid in admins.keys():
            string += "\\n\\n" \
                "[b]Admin Commands:[/b]\\n" \
                "[color=grey]!<cmd> (<aliases>) : [i]<Description>[/i][/color]\\n\\n" \
                "[color=green]!activate[/color] : [i]Toggle this bot[/i]\\n"

        self.sendChannelMessage(string)

    def cmd_activate(self, userid, user, data):
        if userid in admins:
            global active
            active = not active
            if active:
                broadcastMessage("[color=green]GatherBot has been activated[/color]")
            else:
                broadcastMessage("[color=red]GatherBot has been deactivated[/color]")
        else:
            self.sendChannelMessage("[color=red]You're not an admin, GTFO![/color]")

    def getenc(self, str):
        return str.encode('ascii')

def broadcastMessage(msg):
    for q in cmdToThread:
        q.put(msg)

"""
    Init the app
"""
active = True

players = []
gatherRunning = False
vetoSystem = "bo3"

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
