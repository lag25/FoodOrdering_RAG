import os
from langchain_core.documents import Document
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
import pinecone
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
import pandas as pd
from ..data.database import SessionLocal
from ..data.DataClass import User, Foods, Restaurant
from sqlalchemy.orm import Session
def get_foods(db: Session):
    return db.query(Foods).all()
def get_restaurants(db: Session):
    return db.query(Restaurant).all()
db = SessionLocal()

class SemanticClassify():
    def __init__(self,chat_history=[]):
        self.cart = pd.DataFrame(columns=["food name", "restaurant name", "quantity", "price"])
        os.environ["GOOGLE_API_KEY"] = "AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw"
        self.llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ["GOOGLE_API_KEY"])
        # dish , restaurant, quantity
       # self.vectorstore = vectorstore
       # self.cart = [['Vada Pav']]
       # self.llm = llm
        self.chat_history = []
        #self.query = query
        self.system_prompt = '''[context]
        You are a virtual waiter for one of the biggest food ordering app in India. Users come to you for food and restaurant suggest as well as placing their orders\n"
        Given a user query, your job is to classify it's intent. These intents can be\n
        1. Adding to cart : If you believe the user wants to add something to the cart then just respond with "addToCart" and nothing else\n
        2. Viewing the cart : If you believe the user wants to view the cart just respond with "viewCart" and nothing else\n
        3. Editing the quantity of a dish in cart : If you believe the user wants to just edit the quantity of a dish already present in the cart then just respond with "EditCart" and nothing else\n
        4. Deleting item in cart: If you believe the user wants to just remove a dish present in the cart then just respond with "DeleteCart" and nothing else\n
        5. Proceeding to checkout : If you believe the user is satisfied with their picks and wants to confirm their order and proceed to checkout then just respond with "checkOut" and nothing else\n
        6. General Querying : If you believe the user is just asking doing some inquiring and are not talking about the cart or checkout then respond with "END" and nothing else.\n\n'''
        foods = get_foods(db)
        self.food_data = [
            {"id": r.id, "restro_id": r.restaurant_id, "name": r.name, "description": r.description, "price": r.price}
            for r in
            foods]
        restaurants = get_restaurants(db)
        self.restaurant_data = [
        {"id": r.id, "name": r.name, "description": r.description, "address": r.address, "google_maps": r.google_maps_link}
        for r in restaurants
    ]
        self.food_df = pd.DataFrame(self.food_data)
        self.restaurant_df = pd.DataFrame(self.restaurant_data)
        self.food_df = self.food_df.rename(
            columns={
                "id": "food_id",
                "restro_id": "id",
                "name": "food_name",
                "description": "food_description",
            }
        )

        # Merging
        self.merged_df = pd.merge(self.restaurant_df, self.food_df, on="id")

    def funcMap(self,keyword,query):
        hashMap = {"addToCart":self.addToCart,
                   "viewCart":self.viewCart,
                   "EditCart":self.EditCart,
                   "DeleteCart":self.DeleteCart,
                    "checkOut":self.checkOut}

        return hashMap[keyword](query)


    def addToCart(self,query):
        cart_system_prompt = "[FOOD DATABASE]\n"
        cart_system_prompt += f'{self.food_data}'
        cart_system_prompt +=  "Looking at the given query given below and respond with the dish name being asked to be added to the cart. Only respond with the dish name and nothing else. If you think these are multiple dishes respond with their names,separated by commas. Also theren can be a possibility of spelling mistake from the user's end so look at the food database i gave you above and fix these mistakes if needed. If you think the user's wording is ambiguous and needs a bit of context then" \
                               "here is your past conversation history with the user - \n"
        cart_system_prompt += f"{self.chat_history}"
        cart_system_prompt += "\nIf you still cannot find these dishes then simply respond with  'no_dishes' \n\n Here is the user query :"
        prompt = cart_system_prompt + query
        response = self.llm.invoke(prompt).content
        if(response == "no_dishes"):
            return "I am sorry I cannot find any dish like you mentioned"
        else:
            for dish in list(response.split(',')):
                dish = dish.strip()
                dish = self.merged_df[self.merged_df['food_name'] == dish].iloc[0]
                food_name = dish['food_name']
                restaurant_name = dish['name']
                price = dish['price']

                # Create a new row
                new_row = {"food name": food_name, "restaurant name": restaurant_name, "quantity": 1,
                           "price": price}
                print(new_row)
                updated_df = self.cart.append(new_row, ignore_index=True)
                self.cart = updated_df

        return self.llm.invoke(f"Write a message telling the user their items which are {list(response.split(','))} have been added to the cart.Here is a pandas dataframe showing the current cart : {self.cart}. Create a well spaced and formatted text based table from this dataframe and show it to the user").content

                #self.cart.append([dish])


    def viewCart(self,query):
        if self.cart.empty or self.cart.bool==False:
            return "The cart is currently empty"
        return self.cart

    def DeleteCart(self, query):
        cart_system_prompt = "[FOOD DATABASE]\n"
        cart_system_prompt += f'{self.food_data}'
        cart_system_prompt += "Looking at the given query given below and respond with the dish name being asked to be removed from the cart. Only respond with the dish name and nothing else. If you think these are multiple dishes respond with their names, separated by commas. Also, there can be a possibility of spelling mistakes from the user's end so look at the cart I gave you above and fix these mistakes if needed. If you think the user's wording is ambiguous and needs a bit of context then use past conversation history for better understanding of the conversation context" \
                              "here is your past conversation history with the user - \n"
        cart_system_prompt += f"{self.chat_history}"
        cart_system_prompt += "\nIf you still cannot find these dishes then simply respond with 'no_dishes' \n\n Here is the user query :"
        prompt = cart_system_prompt + query
        response = self.llm.invoke(prompt).content

        if response == "no_dishes":
            return "I am sorry, I cannot find any dish like you mentioned in the cart."
        else:
            removed_dishes = []
            for dish in list(response.split(',')):
                dish = dish.strip()
                # Check if the dish exists in the cart
                if dish in self.cart['food name'].values:
                    # Remove the row containing the dish from the cart
                    self.cart = self.cart[self.cart['food name'] != dish]
                    removed_dishes.append(dish)
                else:
                    return f"I am sorry, {dish} is not in your cart."

        return self.llm.invoke(
            f"Write a message telling the user their items {removed_dishes} have been removed from the cart. Here is a pandas dataframe showing the current cart : {self.cart}. Create a well spaced and formatted text based table from this dataframe and show it to the user").content

    def EditCart(self, query):
        pass
    #     cart_system_prompt = "[FOOD DATABASE]\n"
    #     cart_system_prompt += f'{self.food_data}'
    #     cart_system_prompt += "Looking at the given query given below and respond with the dish name being asked to be edited in the cart. Only respond with the dish name and the new quantity separated by a colon, e.g., 'dish_name:new_quantity'. If you think there are multiple dishes, respond with their names and new quantities, separated by commas. Also, there can be a possibility of spelling mistakes from the user's end so look at the cart I gave you above and fix these mistakes if needed. If you think the user's wording is ambiguous and needs a bit of context then" \
    #                           "here is your past conversation history with the user - \n"
    #     cart_system_prompt += f"{self.chat_history}"
    #     cart_system_prompt += "\nIf you still cannot find these dishes then simply respond with 'no_dishes' \n\n Here is the user query :"
    #     prompt = cart_system_prompt + query
    #     response = self.llm.invoke(prompt).content
    #
    #     if response == "no_dishes":
    #         return "I am sorry, I cannot find any dish like you mentioned in the cart."
    #     else:
    #         edited_dishes = []
    #         for edit_info in list(response.split(',')):
    #             # Split the edit_info into dish name and new quantity
    #             edit_info = list(edit_info.split(":"))
    #             dish, new_quantity = edit_info[0], edit_info[1]
    #             # Check if the dish exists in the cart
    #             if dish in self.cart['food name']:
    #                 # Update the quantity of the dish in the cart
    #                 print(self.cart)
    #                 self.cart.loc[self.cart['food name'] == dish, 'quantity'] = int(new_quantity)
    #                 edited_dishes.append((dish, new_quantity))
    #             else:
    #                 return f"I am sorry, {dish} is not in your cart."
    #
    #         # Construct the response message
    #         response_message = f"The quantities of the following items have been updated in your cart: {edited_dishes}."
    #         return response_message

    def checkOut(self,query):
        total_cost = (self.cart['quantity'] * self.cart['price']).sum()

        # Optional: Create a summary of the cart items
        cart_summary = self.cart[['food name','restaurant name', 'quantity', 'price']].to_dict('records')

        # Generate the response message
        response = self.llm.invoke(
            f"Write a message telling the user that their checkout is complete. The total cost is {total_cost}. Here is a summary of your cart: {cart_summary}"
        ).content

        return response




    def segment(self,query):
        prompt = self.system_prompt + "Here's the user query\n" + query
        response = self.llm.invoke(prompt)
        return response.content

    def run(self,query,keyword):
        return self.funcMap(keyword,query)




if __name__ == "__main__":
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw"
    llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ["GOOGLE_API_KEY"])
    obj = SemanticClassify('')
    print(obj.run("Okay then add Vada pav and biryani to my cart"))
    print(obj.cart)

