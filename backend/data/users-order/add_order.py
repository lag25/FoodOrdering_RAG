from backend.whatsapp.insert_user_data import add_user,main

from ..database import SessionLocal

user_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": 1234567890,
    "eat_nv": True,
    "address": "123 Main Street"
}


def func():
    db = SessionLocal()

    user_data = {                               # GPT genereated sample data
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": 1234567890,
        "eat_nv": True,
        "address": "123 Main Street"
    }


    added_user = add_user(db, **user_data)
    db.close()
    print("User added successfully!")
    print("Added user:", added_user)

    # Call main to populate the database further
    main()


if __name__ == "__main__":
    func()


