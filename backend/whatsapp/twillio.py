from twilio.rest import Client

# Your Twilio credentials
account_sid = 'AC93bf87b054678757c10031b1c84d6c8c'
auth_token = '853de7854a37fb5c3d14bcc6b3bc373e'

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Send a message
message = client.messages.create(
    body='Hello, from your application!',
    from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
    to='whatsapp:+919109474150'       # Recipient's WhatsApp number
)
print(message.sid)

