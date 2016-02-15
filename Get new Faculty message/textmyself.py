accountSID = '********************'
authToken = '*********************'
myNumber = '+********'
twilioNumber = '+**********'


from twilio.rest import TwilioRestClient


def textmyself(message):
    twilioCli = TwilioRestClient(accountSID, authToken)
    twilioCli.messages.create(body=message, from_=twilioNumber, to=myNumber)
