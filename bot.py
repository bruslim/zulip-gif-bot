from memebot import MemeBot

import zulip
import os


subs = open('subscriptions.txt', 'r')

ZULIP_STREAMS = []

try:
    for line in subs: 
        ZULIP_STREAMS.append(line.strip())
finally: 
    f.close()

client = zulip.Client(email=os.environ['ZULIP_USERNAME'], 
                      api_key=os.environ['ZULIP_API_KEY'])

client.add_subscriptions([{"name": stream_name} for stream_name in ZULIP_STREAMS])

# meme bot
bot = MemeBot(client)

print('Loaded ' + str( len( bot.local_memes ) ) + ' memes')

# This is a blocking call that will run forever
# es6: (msg) => { return respond(msg); }
client.call_on_each_message(lambda msg: bot.respond(msg))
