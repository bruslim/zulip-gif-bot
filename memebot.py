#!/usr/bin/env python

import zulip
import json
import requests
import os
import urllib
import datetime

from zulip_bot import ZulipBot

class MemeBot(ZulipBot):
  
  def __init__(self, client):
    ZulipBot.__init__(self, client);
    self.local_memes = json.loads(open('meme_seeds.json').read())
    self.load_memes()
  
  # call respond function when client interacts with gif bot
  def respond(self, msg):

    # If sender email is my email return
    if msg['sender_email'] == os.environ['ZULIP_USERNAME']:
      return

    # split the content by 0
    content = msg['content'].split()

    # assume content starts a t 0
    content_starts = 0;

    # special command
    if ((content[0].upper() == "MEME" and content[1].upper() == "ME")):
      content_starts = 2

    # handle @meme bot command
    # @meme bot meme me
    if ((content[0].upper() == "@**MEME" and content[1].upper() == "BOT**" and content[2].upper() == "MEME" and content[3].upper() == "ME")):
      content_starts = 4

    # no content?
    if (content_starts <= 0):
      return

    # rejoin the strings
    query = [q.strip() for q in (" ".join(content[content_starts:])).split("|")]

    # set defualt response
    response_content = ''

    # special !memes for a list of memes 
    if (query[0].lower() == '!memes'):
      all_the_memes = self.list_all_memes();
      self.send_pm(msg,  'I know of ' +  str( len( self.local_memes ) ) + ' memes:\n' + "\n".join(sorted(all_the_memes)))
      return

    # get the meme
    meme = self.get_meme(query[0]);
    # uknown?
    if (meme is None):
      #pm error message
      self.send_pm(msg, self.create_image(61527, query[0] ,"Y U NO !MEMES") + "\nUnknown Meme: " + query[0])
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
          top = query[1]

        if (len(query) > 2):
          bottom = query[2]

        response_content = self.create_image(meme['id'], top, bottom)

    self.send_msg(msg, response_content)



  def list_all_memes(self):
    for meme_name in self.local_memes:
      meme = self.local_memes[meme_name]
      yield '[' + meme['name'] + '](' + meme['url'] + ')'

  def create_image(self, image_id, top_text, bottom_text):
    response = requests.post("https://api.imgflip.com/caption_image",data={
        'template_id': image_id,
        'username': os.environ['IMG_FLIP_USERNAME'],
        'password': os.environ['IMG_FLIP_PASSWORD'],
        'text0': top_text,
        'text1': bottom_text,
      }).content
    return json.loads(response)['data']['url']

  def get_meme(self, name):
    # should we reload the list?
    if ((datetime.datetime.now() - self.last_loaded) < datetime.timedelta(hours=6)):
      self.load_memes()

    # normalize it
    lower = name.lower()

    # get it if it exists
    if lower in self.local_memes:
      return self.local_memes[lower]

    # return nothing if not
    return None

  # load the memes
  def load_memes(self):
    response = requests.get("https://api.imgflip.com/get_memes").content
    
    loaded_json = json.loads(response)
    
    memes = loaded_json['data']['memes']
    
    for meme in memes:
      self.local_memes[meme['name'].lower()] = meme
    
    self.last_loaded = datetime.datetime.now()
    
    return len(memes)



