from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console
account_sid = ''
auth_token = ''


def send_intruder_alert():
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body='Intruder ALERT!\nUnknown person has entered the monitored area',
        # from_='+12563049692',
        from_='whatsapp:',
        to='whatsapp:'
    )
    print('Intruder alert sent with message id: %s' % message.sid)


if __name__ == '__main__':
    send_intruder_alert()
