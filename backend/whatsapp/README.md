# Whatsapp

Contains all the code for user ended logic:

- ```python -m backend.data.get_messages.py ``` - starts running our flask API
- ```python check_new_user.py``` - Checks if the user is a returning customer or a new one
- ```python insert_user_data.py``` - Updates the database with the necessary information gotten from the new customer
- ```python SemanticClass.py``` - Contains the class that tags the query based on the semantic context and all the other funcionalities related to the cart and checkout
- ```python return_message.py``` - Module that is used for general querying/Q&A with the customer


### NOTE
- Multiple files are redundant and are not used in the working of the application. They will soon be purged and removed from the repo
- There are multiple instances where API credentials can be seen being used working publicly. They will be removed and a dot env file will be implemented instead.
