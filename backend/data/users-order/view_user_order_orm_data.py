import pandas as pd
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..DataClass import User,Order

def get_users(db: Session):
    return db.query(User).all()

# def get_foods(db: Session):
#     return db.query(Foods).all()

def main():
    db = SessionLocal()

    # Fetch data from the restaurants table
    users = get_users(db)

    # Convert the data to a pandas DataFrame
    user_data = [{"id": r.id, "name": r.first_name + r.last_name, "email": r.email, "phone":r.phone, "address":r.address} for r in users]
    user_df = pd.DataFrame(user_data)

    # Print the Restaurants DataFrame
    print("users:")
    print(user_df)

    # Fetch data from the foods table
    # foods = get_foods(db)
    #
    # # Convert the data to a pandas DataFrame
    # food_data = [{"id": f.id, "restaurant_id": f.restaurant_id, "name": f.name, "description": f.description} for f in foods]
    # food_df = pd.DataFrame(food_data)
    #
    # # Print the Foods DataFrame
    # print("\nFoods:")
    # print(food_df)
    # breakpoint()

if __name__ == "__main__":
    main()