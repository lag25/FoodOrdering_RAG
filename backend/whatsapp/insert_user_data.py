import pandas as pd
from sqlalchemy.orm import Session

from ..data.database import SessionLocal
from ..data.DataClass import User

def add_user(db: Session, first_name: str,last_name :str,email:str,phone:int,eat_nv:bool,address):
    user = User(first_name=first_name, last_name = last_name, email=email,phone=phone,eat_nv = eat_nv,address=address)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user




def create_user(user):
    db = SessionLocal()
    add_user(db,user['first_name'],user['last_name'],user['email'],user['phone'],user['eat_nv'],user['address'])


    print("Data populated successfully!")

if __name__ == "__main__":
    main()
