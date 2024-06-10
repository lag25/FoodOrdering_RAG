from ..data.database import SessionLocal
from ..data.DataClass import User
from sqlalchemy.orm import Session
from twilio.rest import Client

account_sid = 'AC93bf87b054678757c10031b1c84d6c8c'
auth_token = '853de7854a37fb5c3d14bcc6b3bc373e'

                # Initialize Twilio client
client = Client(account_sid, auth_token)

def get_users(db: Session):
    return db.query(User).all()

def user_check(phone:int):
    db = SessionLocal()
    users = get_users(db)

    for r in users:
        if r.phone == phone:
            return True
    return False

if __name__ == "__main__":
    print(user_check(8989822443))

