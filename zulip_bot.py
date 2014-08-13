import json

class ZulipBot:
  
  def __init__(self, client):
    self.client = client;

  def get_recipients(self, msg):
    if isinstance(msg['display_recipient'], list):
      for recipient in msg['display_recipient']:
        yield recipient['email'] 

  def send_pm(self, msg, content):
    recipients = list(self.get_recipients(msg))
    recipients.append(msg['sender_email']) 
    self.client.send_message({
      "type": 'private',
      "subject": msg['subject'],
      "to": json.dumps(recipients),
      "content": content
    })
  
  def send_msg(self, msg, content):
    if msg['type'] == 'stream':
      self.client.send_message({
          "type": "stream",
          "subject": msg["subject"],
          "to": msg['display_recipient'],
          "content": content
      })
    else:
      self.send_pm(msg, content)
      
    