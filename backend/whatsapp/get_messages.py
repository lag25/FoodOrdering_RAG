from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from .return_message import generate
from .check_new_user import user_check
from .user_details import get_next_question, handle_answer, is_registration_complete
from .SemanticClass import SemanticClassify

app = Flask(__name__)
app.secret_key = '19o81910'

initial_connection_made = False
#unction to be executed only once

classifiers = {}              # Stores each sematnic classify object for each
conversation = {}            # Stores the conversation history of each user

def initial_connection_function(user_id):
    # code to be executed only on the first connection
    print("Initial connection established!")
    session.clear()
    # Perform any initialization tasks here
    global initial_connection_made
    initial_connection_made = True
    classifiers[user_id] = SemanticClassify([])
    conversation[user_id] = []



@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    """Respond to incoming WhatsApp messages."""


    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')
    phone = int(from_number[12:])  # Phone number without extension
    if not initial_connection_made:
        initial_connection_function(phone)
    print(f"Received message: {incoming_msg} from {from_number}")

    # Initialize response
    chat_history = conversation[phone]
    resp = MessagingResponse()
    clf = classifiers[phone]
    if user_check(phone):
        # If the user exists, generate a regular response
        semantic_Category = clf.segment(incoming_msg)
        if(semantic_Category != "END"):
            clf.chat_history = chat_history
            response = clf.run(incoming_msg,semantic_Category)

        else:
            response = generate(incoming_msg,chat_history[-10:])
        chat_history.append(f"user : {incoming_msg}")
        chat_history.append(f"foodNEST bot : {response}")
        print(chat_history)
        resp.message(response)
    else:
        # If the user is new, handle the registration process
        if 'registration_step' not in session or session['user_id'] != phone:
            session['registration_step'] = 0
            session['user_id'] = phone
            resp.message(
                "Hi, I noticed that you are not registered in our database. Let's get you registered.")
            resp.message("What is your first name?")
        else:
            # Handle the current step of the registration
            next_question = handle_answer(session['user_id'], session['registration_step'], incoming_msg)
            if(next_question == None):
                resp.message("Registration complete! Thank you.")
                resp.message(is_registration_complete(phone))
            elif(next_question == "Invalid email format. Please enter your email again."):
                resp.message(next_question)
            else:
                session['registration_step'] += 1
                resp.message(next_question)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=False)
