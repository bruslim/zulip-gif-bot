#!/usr/bin/env python

import zulip
import json
import requests
import random
import os
import urllib

f = open('subscriptions.txt', 'r')

ZULIP_STREAMS = []

try:
    for line in f: 
        ZULIP_STREAMS.append(line.strip())
finally: 
    f.close()

client = zulip.Client(email='meme-bot@students.hackerschool.com',
                      api_key='bAD KETY')

client.add_subscriptions([{"name": stream_name} for stream_name in ZULIP_STREAMS])

# call respond function when client interacts with gif bot
def respond(msg):

    if msg['sender_email'] != "meme-bot@students.hackerschool.com":
        content = msg['content'].split()
        
        contentStarts = 0;
        
        if ((content[0].upper() == "MEME" and content[1].upper() == "ME")):
            contentStarts = 2
        
        if ((content[0].upper() == "@**MEME" and content[1].upper() == "BOT**" and content[2].upper() == "MEME" and content[3].upper() == "ME")):
            contentStarts = 4
            
        if (contentStarts > 0):
            query = " ".join(content[contentStarts:]).split(",")
            
            print(query);
            
            api_call = "http://apimeme.com/meme?meme=" + urllib.quote(query[0]) 
            if (len(query) > 1): 
              api_call = api_call + "&top=" + urllib.quote(query[1])
            if (len(query) > 2):
              api_call = api_call + "&bottom=" + urllib.quote(query[2])
              
            

            if msg['type'] == 'stream':
                client.send_message({
                    "type": "stream",
                    "subject": msg["subject"],
                    "to": msg['display_recipient'],
                    "content": api_call
                })
            else:
                client.send_message({
                    "type": msg['type'],
                    "subject": msg['subject'],
                    "to": msg['sender_email'],
                    "content": api_call
                })
  

# This is a blocking call that will run forever
client.call_on_each_message(lambda msg: respond(msg))
