#!/usr/bin/env python

import zulip
import json
import requests
import os
import urllib
import datetime

f = open('subscriptions.txt', 'r')

ZULIP_STREAMS = []

try:
    for line in f: 
        ZULIP_STREAMS.append(line.strip())
finally: 
    f.close()

client = zulip.Client(email=os.environ['ZULIP_USERNAME'], 
                      api_key=os.environ['ZULIP_API_KEY'])

client.add_subscriptions([{"name": stream_name} for stream_name in ZULIP_STREAMS])

local_memes = {}
last_loaded = datetime.datetime.now()

# call respond function when client interacts with gif bot
def respond(msg):
 
  # If sender email is my email return
  if msg['sender_email'] == "meme-bot@students.hackerschool.com": #os.environ['ZULIP_USERNAME']:
    return

  content = msg['content'].split()
  
  contentStarts = 0;

  if ((content[0].upper() == "MEME" and content[1].upper() == "ME")):
    contentStarts = 2

  if ((content[0].upper() == "@**MEME" and content[1].upper() == "BOT**" and content[2].upper() == "MEME" and content[3].upper() == "ME")):
    contentStarts = 4

  if (contentStarts <= 0):
    return
  
  # rejoin the strings
  query = (" ".join(content[contentStarts:])).split("|")
  response_content = ''
  
  # special !memes for a list of memes 
  if (query[0].strip().lower() == '!memes'):
    all_the_memes = list_all_memes();
    send_pm(msg,  'List of known memes:\n' + "\n".join(sorted(all_the_memes)))
    return
  
  # get the meme
  meme = get_meme(query[0].strip());
  if (meme is None):
    send_pm(msg, create_image(61527, query[0].strip() ,"Y U NO !MEMES") + "\nUnknown Meme: " + query[0])
    return
  else:
    top = ''
    bottom = ''

    if (len(query) == 1):
      response_content = meme['url']
    else:
      if (len(query) > 1): 
        top = query[1].strip()

      if (len(query) > 2):
        bottom = query[2].strip()

      response_content = create_image(meme['id'], top, bottom)

  if msg['type'] == 'stream':
    client.send_message({
        "type": "stream",
        "subject": msg["subject"],
        "to": msg['display_recipient'],
        "content": response_content
    })
  else:
    send_pm(msg, response_content)


def send_pm(msg, content):
  client.send_message({
    "type": 'private',
    "subject": msg['subject'],
    "to": msg['sender_email'],
    "content": content
  })
  
def list_all_memes():
  for meme_name in local_memes:
    meme = local_memes[meme_name]
    yield '[' + (meme['name']) + '](' + (meme['url']) + ')'
  
    
def create_image(image_id, top_text, bottom_text):
  response = requests.post("https://api.imgflip.com/caption_image",data={
      'template_id': image_id,
      'username': os.environ['IMG_FLIP_USERNAME'],
      'password': os.environ['IMG_FLIP_PASSWORD'],
      'text0': top_text,
      'text1': bottom_text,
    }).content
  data = json.loads(response)
  return data['data']['url']
    
def get_meme(name):
  
  if ((datetime.datetime.now() - last_loaded) < datetime.timedelta(hours=6)):
    load_memes()
  
  upper = name.lower()
  
  if upper in local_memes:
    return local_memes[upper]

  return None

def load_memes():
  response = requests.get("https://api.imgflip.com/get_memes").content
  loaded_json = json.loads(response)
  memes = loaded_json['data']['memes'];

  for meme in memes:
    local_memes[meme['name'].lower()] = meme
  
  last_loaded = datetime.datetime.now()

  
  return len(memes)



#init the list





load_memes()

print('Loaded ' + str( len( local_memes ) ) + ' memes')

# This is a blocking call that will run forever
client.call_on_each_message(lambda msg: respond(msg))

