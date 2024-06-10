# get_user_details.py
import re
from flask import session
from ..data.database import SessionLocal
from ..data.DataClass import User
from sqlalchemy.orm import Session
from .insert_user_data import create_user
user_data = {}

def get_next_question(step):
    questions = [
        "What is your first name?",
        "What is your second name?",
        "Are you comfortable with Non-Vegetarian foods (y/n)",
        "What is your address",
        "What is your email?"
    ]
    if step < len(questions):
        return questions[step]
    return None


def is_valid_email(email):
    # regular expression to validate email format
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def handle_answer(user_id, step, answer):
    if user_id not in user_data:
        user_data[user_id] = {}
        user_data[user_id]['phone'] = user_id
    if step == 0:
        user_data[user_id]['first_name'] = answer
    if step == 1:
        user_data[user_id]['last_name'] = answer
    elif step == 2:
        user_data[user_id]['eat_nv'] = True if answer.lower() == "y" else False
    elif step == 3:
        user_data[user_id]['address'] = answer
    elif step == 4:
        if is_valid_email(answer):
            user_data[user_id]['email'] = answer
        else:
            # If email is invalid, ask the user to enter it again
            return "Invalid email format. Please enter your email again."

    # Add more steps as needed

    return get_next_question(step + 1)


def is_registration_complete(user_id):
    # required_fields = ['phone','first_name','second_name','nv' 'address', 'email']
    # if all(field in user_data[user_id] for field in required_fields):
    #     # Here, you would typically save the user data to your database
    create_user(user_data[user_id])


    return f"User {user_id} registered with data: {user_data[user_id]}"
    #     session.clear()
    #     return True
    # return False


