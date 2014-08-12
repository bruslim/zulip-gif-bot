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

# meme seeds
local_memes = {
  'not bad obama': {
    'id': 289182,
    'name': 'Not Bad Obama',
    'url': 'https://i.imgflip.com/674u.jpg'
  },
  "over 9000": {
    'id': 2525024,
    'name': 'Over 9000',
    'url': 'https://i.imgflip.com/1i4bk.jpg'
  },
  "me gusta": {
    'id': 7249133,
    'name': 'Me Gusta',
    'url': 'https://i.imgflip.com/4bdgt.jpg'
  },
  "table flip guy": {
    'id': 1380694,
    'name': "Table Flip Guy",
    'url': "https://i.imgflip.com/tlcm.jpg"
  },
  "challenge accepted": {
    "id": 8881419,
    "name": "Challenge Accepted",
    "url": "https://i.imgflip.com/5acy3.jpg"
  },
  "derp": {
    "id":806713,
    "name":"Derp",
    "url": "https://i.imgflip.com/hagp.jpg"
  }
}

last_loaded = datetime.datetime.now()

# call respond function when client interacts with gif bot
def respond(msg):
 
  # If sender email is my email return
  if msg['sender_email'] == os.environ['ZULIP_USERNAME']:
    return

  # split the content by 0
  content = msg['content'].split()
  
  # assume content starts a t 0
  contentStarts = 0;

  # special command
  if ((content[0].upper() == "MEME" and content[1].upper() == "ME")):
    contentStarts = 2

  # handle @meme bot command
  if ((content[0].upper() == "@**MEME" and content[1].upper() == "BOT**" and content[2].upper() == "MEME" and content[3].upper() == "ME")):
    contentStarts = 4

  # no content?
  if (contentStarts <= 0):
    return
  
  # rejoin the strings
  query = (" ".join(content[contentStarts:])).split("|")
  
  # set defualt response
  response_content = ''
  
  # special !memes for a list of memes 
  if (query[0].strip().lower() == '!memes'):
    all_the_memes = list_all_memes();
    send_pm(msg,  'I know of ' +  str( len( local_memes ) ) + ' memes:\n' + "\n".join(sorted(all_the_memes)))
    return
  
  # get the meme
  meme = get_meme(query[0].strip());
  # uknown?
  if (meme is None):
    #pm error message
    send_pm(msg, create_image(61527, query[0].strip() ,"Y U NO !MEMES") + "\nUnknown Meme: " + query[0])
    return
  else:
    # if just meme name
    if (len(query) == 1):
      response_content = meme['url']
      
    else:
      # init top and bottom text
      top = ''
      bottom = ''

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

# method to get recipients for a group pm
def get_recipients(msg):
  if isinstance(msg['display_recipient'], list):
    for recipient in msg['display_recipient']:
      yield recipient['email']

def send_pm(msg, content):
  recipients = list(get_recipients(msg))
  recipients.append(msg['sender_email']) 
  client.send_message({
    "type": 'private',
    "subject": msg['subject'],
    "to": json.dumps(recipients),
    "content": content
  })
  
def list_all_memes():
  for meme_name in local_memes:
    meme = local_memes[meme_name]
    yield '[' + meme['name'] + '](' + meme['url'] + ')'
  
    
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
  
  # should we reload the list?
  if ((datetime.datetime.now() - last_loaded) < datetime.timedelta(hours=6)):
    load_memes()
  
  # normalize it
  upper = name.lower()
  
  # get it if it exists
  if upper in local_memes:
    return local_memes[upper]

  # return nothing if not
  return None

# load the memes
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

