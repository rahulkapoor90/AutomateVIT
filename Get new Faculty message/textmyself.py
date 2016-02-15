accountSID = 'ACb19eeeaf4f63fcc78b19b293d54b490c'
authToken = '44452addcb1df3e80171a8491953d6e7'
myNumber = '+918220584301'
twilioNumber = '+19546076780'

from twilio.rest import TwilioRestClient


def textmyself(message):
    twilioCli = TwilioRestClient(accountSID, authToken)
    twilioCli.messages.create(body=message, from_=twilioNumber, to=myNumber)
