accountSID = 'AC7a91ed68e24d87b700ec9fb379619417'
authToken = 'b6504aaf99dabb743ab7f813dfc2301a'
myNumber = '+918220584301'
twilioNumber = '+12249002737'

from twilio.rest import TwilioRestClient


def textmyself(message):
    twilioCli = TwilioRestClient(accountSID, authToken)
    twilioCli.messages.create(body=message, from_=twilioNumber, to=myNumber)
