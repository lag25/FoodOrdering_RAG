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


os.environ["PINECONE_API_KEY"] = "04d5a86b-edfb-4cb3-86bb-0638717ce4af"
os.environ[
    "ANTHROPIC_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw"
ENVIRONMENT = "us-east-1"
INDEX_NAME = "foodnest"

# System prompt definition
system_prompt = """[Context]
You are a chatbot for foodNEST, the leading food delivery platform in India
Your primary goal is to assist customers in finding and ordering their favorite meals from a wide variety of restaurants with ease and convenience.
Whenever a customer talks to you, you are always polite and friendly and make small talk if the customer seems to be indulging in it. You are fluent in both English and Hindi and occasionally you respond in Hinglish.

As a delivery app chatbot, you are friendly, approachable, and always eager to help.
You understand that hunger can sometimes make people impatient, so you strive to provide quick and efficient service with a touch of humor to lighten the mood
Your functionalities include helping users browse through restaurant menus, suggesting popular dishes based on their preferences and guiding them through the ordering process


Your personality is like that of a waiter. It is a perfect blend of professionalism and playfulness, making you an enjoyable and reliable companion for users seeking a satisfying meal delivered right to their doorstep
You are concise with your answers. You do not answer with more than 70 words. Your answers are informative and playful. Something you end the sentence with a fun hinglish remark to really sell the dish"""

def get_pinecone():
    pc = pinecone.Pinecone("04d5a86b-edfb-4cb3-86bb-0638717ce4af")
    index = pc.Index("example")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Pinecone(index=index, text_key=os.environ["PINECONE_API_KEY"], embedding=embeddings)
    return vectorstore


def contextualizer(chat_history,llm,query):
    context_system_prompt = """(
    "Given a chat history and the latest user question 
    which might reference context in the chat history, 
    formulate a standalone question which can be understood 
    without the chat history. Do NOT answer the question, 
    just reformulate it if needed and otherwise return it as is.

        \n\n
        (context)\n"""
    context_system_prompt += "Here is the past chat history between the user and bot presented chronologically\n"
    context_system_prompt += "\n".join(chat_history)
        
    context_system_prompt += "\nHere's the current user query \n"
    context_system_prompt += f"{query}"

    return llm.invoke(context_system_prompt)



def llm_generate_conversational_response(llm, retriever, query,chat_history):
    # Retrieve documents matching the query
    results = retriever.invoke(query)

    # Extract relevant information from the results
    restaurant_infos = []
    for result in results:
        restaurant_info = {
            "name": result.metadata["restaurant_name"],
            "description": result.metadata["restaurant_description"],
            "menu": result.metadata["restaurant_menu"]
        }
        restaurant_infos.append(restaurant_info)

    # Create a conversational prompt using the retrieved information and history
    prompt = f"{system_prompt}\n\n"
    prompt += f"Given the following restaurants suggest various dishes and multiple restaurants to the customer and tell them why. You are only exclusively supposed to suggest the dishes with their respective restaurants and prices as from our database's restaurant info which I will give you and not create on your own. Furthermore, you response can seldom be in bullet points if needed. Heres the restaurants' info: {restaurant_infos[::]}\n\n"
    prompt += "The current user query you have to respond to is given here\n"
    context_query = contextualizer(chat_history,llm,query)
    prompt += f"User: {context_query}\n\n"

    # Use the LLM to generate a conversational response
    response = llm.invoke(prompt)
    return response.content



def generate(user_query,chat_history):
    vectorstore = get_pinecone()
    metadata_field_info = [
        AttributeInfo(
            name="restaurant_id",
            description="The ID of the restaurant",
            type="integer",
        ),
        AttributeInfo(
            name="restaurant_name",
            description="The name of the restaurant",
            type="string",
        ),
        AttributeInfo(
            name="restaurant_description",
            description="A description of the restaurant",
            type="string",
        ),
        AttributeInfo(
            name="restaurant_address",
            description="The address of the restaurant",
            type="string",
        ),
        AttributeInfo(
            name="google_maps_link",
            description="Google Maps link to the restaurant location",
            type="string",
        ),
        AttributeInfo(
            name="food_name",
            description="The name of the food item",
            type="string",
        ),
        AttributeInfo(
            name="food_description",
            description="A description of the food item",
            type="string",
        ),
        AttributeInfo(
            name="food_price",
            description="The price of the food item",
            type="integer",
        )
    ]
    document_content_description = "Detailed description of food items available at various restaurants in Vidisha, India"

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ["GOOGLE_API_KEY"])

    # Initialize retriever
    retriever = SelfQueryRetriever.from_llm(
        llm, vectorstore, document_content_description, metadata_field_info, verbose=True
    )
    response = llm_generate_conversational_response(llm, retriever, user_query,chat_history)
   # print(response)
    return response



if __name__ == "__main__":
    while True:                                                                                 # For the testing script
        print(generate(input()," ")+"\n\n")
