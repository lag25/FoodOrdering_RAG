import os
from langchain_core.documents import Document
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
import pinecone
from langchain.chains.query_constructor.base import AttributeInfo

# Load environment variables
os.environ["PINECONE_API_KEY"] = "435898e5-fd77-4b74-8c39-a06995fbefad"
os.environ[
    "ANTHROPIC_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw"
ENVIRONMENT = "us-east-1"
INDEX_NAME = "foodnest-order"

# System prompt definition
system_prompt = """[Context]
You are a chatbot for AutoFood, the leading food delivery platform in North America
Your primary goal is to assist customers in finding and ordering their favorite meals from a wide variety of restaurants with ease and convenience
You are knowledgeable about the latest deals, promotions, and restaurant offerings, ensuring that users have access to the most up-to-date information

As a delivery app chatbot, you are friendly, approachable, and always eager to help.
You understand that hunger can sometimes make people impatient, so you strive to provide quick and efficient service with a touch of humor to lighten the mood
Your functionalities include helping users browse through restaurant menus, suggesting popular dishes based on their preferences, guiding them through the ordering process, and providing real-time updates on their order status

You are also capable of handling customer complaints and resolving issues related to orders, payments, and deliveries
Your personality is a perfect blend of professionalism and playfulness, making you an enjoyable and reliable companion for users seeking a satisfying meal delivered right to their doorstep
You are concise with your answers. You do not answer with more than 70 words."""


# Pinecone setup
def setup_pinecone():
    pc = pinecone.Pinecone("435898e5-fd77-4b74-8c39-a06995fbefad")
    index = pc.Index("foodnest-order")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Pinecone(index=index, text_key=os.environ["PINECONE_API_KEY"], embedding=embeddings)
    return vectorstore


# LLM and retriever interaction


def categorize_response(llm,retriever,query):
    results = retriever.invoke(query)

    # Extract relevant information from the results
    system_prompt =  ''' [SYSTEM PROMPT]
             you will be give a given query after this sentence separated by two linebreaks. Your job is to categorize if that query is :
             A. Normal Conversation : If its a normal conversation happening between the model and user where it seems like the user still is deciding what he should be ordering.Then only respond with normal_conversaiton
             B. Ordering food : If it seems like the user has decided to add any dish to his cart and is 100% sure and definitely wants to order the dish. Then only respond with food_order
             Here's the user query :'''

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
    prompt+= query

    # Use the LLM to generate a conversational response
    response = llm.invoke(prompt)
    return response.content



def llm_generate_conversational_response(llm, retriever, query, conversation_history):
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
    prompt += "Conversation history:\n"
    for turn in conversation_history:
        prompt += f"User: {turn['user']}\nBot: {turn['bot']}\n"

    prompt += f"User: {query}\n\n"

    if restaurant_infos:
        prompt += "Based on your query, here are some restaurant suggestions:\n\n"
        for info in restaurant_infos[:2]:  # Limiting to the first two results
            prompt += f"Restaurant Name: {info['name']}\nDescription: {info['description']}\nMenu: {info['menu']}\n\n"
        prompt += "Politely suggest a few dishes from these restaurants that would match the description of the user's query and tell them why they would enjoy them. Add a fun quirky remark in Hinglish."
    else:
        prompt += "I'm sorry, but I couldn't find any restaurants that match your query."

    # Use the LLM to generate a conversational response
    response = llm.invoke(prompt)
    return response.content


# Main function to handle interactive conversation
def main():
    vectorstore = setup_pinecone()
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
            name="food_name",
            description="The name of the food item",
            type="string",
        ),
        AttributeInfo(
            name="food_description",
            description="A description of the food item",
            type="string",
        ),
    ]
    document_content_description = "Detailed description of food items available at various restaurants in Vidisha, India"

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ["GOOGLE_API_KEY"])

    # Initialize retriever
    retriever = SelfQueryRetriever.from_llm(
        llm, vectorstore, document_content_description, metadata_field_info, verbose=True
    )

    conversation_history = []

    # Interactive loop
    while True:
        user_query = input("User: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        response = categorize_response(llm, retriever, user_query)
        print(f"Bot: {response}")
        conversation_history.append({"user": user_query, "bot": response})


if __name__ == "__main__":
    main()
