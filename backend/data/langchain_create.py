import os
import pandas as pd
from sqlalchemy.orm import Session
#from langchain import PromptTemplate, Document, TextSplitter, Retriever
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_community.document_loaders import TextLoader
import pinecone
#from langchain.indexes import VectorStoreIndexCreator
from langchain.chains import llm
#from langchain.schema import LLM, BaseRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.llms import Anthropic
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever

from langchain_google_genai import ChatGoogleGenerativeAI
# Load environment variables
os.environ["PINECONE_API_KEY"] = "435898e5-fd77-4b74-8c39-a06995fbefad"
os.environ["ANTHROPIC_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw"
ENVIRONMENT = "us-east-1"
INDEX_NAME = "foodnest-order"

# Importing utility functions and database session
try:
    from data_utils import get_db, get_restaurants, get_foods
    from DataClass import Restaurant, Foods
    from database import SessionLocal
except:
    from .data_utils import get_db, get_restaurants, get_foods
    from .DataClass import Restaurant, Foods
    from .database import SessionLocal

def process_restaurants():
    # Reading SQLite db
    db = SessionLocal()
    restaurants = get_restaurants(db)
    foods = get_foods(db)

    # Convert the data to a pandas DataFrame
    restaurant_data = [{"id": r.id, "name": r.name, "description": r.description} for r in restaurants]
    restaurant_df = pd.DataFrame(restaurant_data)

    food_data = [
        {"id": f.id, "restaurant_id": f.restaurant_id, "name": f.name, "description": f.description}
        for f in foods]
    food_df = pd.DataFrame(food_data)

    # Processing for merge: renaming columns
    food_df = food_df.rename(
        columns={
            "id": "food_id",
            "restaurant_id": "id",
            "name": "food_name",
            "description": "food_description",
        }
    )

    # Merging
    df = pd.merge(restaurant_df, food_df, on="id")

    # Groupby restaurant and creating text for embedding
    df["food_text"] = "\n-" + df["food_name"] + "\n" + df["food_description"]

    df = df.groupby("id").agg({"name": "first", "description": "first", "food_text": "sum"}).reset_index()

    # Creating text for embedding
    df["text"] = "```" + df["name"] + "\nRestaurant description: " + df["description"] + "\nFood available:" + df[
        "food_text"] + "\n```"

    # Convert to LangChain Documents
    documents = [
        Document(
            page_content = "string",text=row["text"],
            metadata={
                "search_type": "restaurant",
                "restaurant_id": row["id"],
                "restaurant_name": row["name"],
                "restaurant_description": row["description"],
                "restaurant_menu": row["food_text"],
            }
        )
        for index, row in df.iterrows()
    ]

    return documents


def llm_generate_conversational_response(llm, retriever, query):
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

    # Create a conversational prompt using the retrieved information
    if restaurant_infos:
        prompt = "Based on your query, here are some restaurant suggestions:\n\n"
        for info in restaurant_infos[:2]:  # Limiting to the first two results
            prompt += f"Restaurant Name: {info['name']}\nDescription: {info['description']}\nMenu: {info['menu']}\n\n"
        prompt += "Using this data, politely ask which restaurant the user would like to order from and also show its menu?"
    else:
        prompt = "I'm sorry, but I couldn't find any restaurants that match your query."

    # Use the LLM to generate a conversational response
    gemini_llm = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.2)
    response = llm.invoke("What is the capital of china ?")
    return response.content

def generate_conversational_response(retriever, query):
    # Retrieve documents matching the query
    results = retriever.invoke(query)

    # Extract the first two restaurant names
    restaurant_names = []
    for result in results[:2]:
        restaurant_name = result.metadata["restaurant_name"]
        restaurant_names.append(restaurant_name)

    # Format the response
    if restaurant_names:
        response = f"The top two restaurants for your query are {restaurant_names[0]} and {restaurant_names[1]}."
    else:
        response = "No matching restaurants found."

    return response

def setup_pinecone(documents):
    # Initialize the embeddings and vectorstore
    pc = pinecone.Pinecone("435898e5-fd77-4b74-8c39-a06995fbefad")
    index = pc.Index("foodnest-order")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Pinecone(index=index, text_key=os.environ["PINECONE_API_KEY"], embedding = embeddings) #index_name=INDEX_NAME, api_key=os.environ["PINECONE_API_KEY"], environment=ENVIRONMENT
    print(dir(vectorstore))
    # Create and add documents to the vectorstore
    vectorstore.add_documents(documents)
    print('embeddings succesfully created')
    return vectorstore

def main():
    documents = process_restaurants()
    vectorstore = setup_pinecone(documents)

    # Initialize retrievers
   # retriever = BaseRetriever(vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(documents)

    # Testing
    query = "testing, I would like to order some spicy indian delicacy"
    # results = {
    #     "regular": retriever.retrieve(query, top_k=2),
    #     "bm25": bm25_retriever.retrieve(query, top_k=2)
    # }

    # Display results
    for retriever_type, result in results.items():
        print(f"Retriever: {retriever_type}")
        for res in result:
            print((res.metadata["restaurant_name"], res.score))
        print("\n\n")


def alpha_main():
    documents = process_restaurants()
    vectorstore = setup_pinecone(documents)
    print(documents)
    print(vectorstore)

def beta_main():
   vectorstore = setup_pinecone(process_restaurants())
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
   document_content_description = "Detailed description of food items available at various restaurants"

    # Initialize LLM (you can replace with actual API key or model)
   llm = ChatGoogleGenerativeAI(model='gemini-pro',google_api_key="AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw")
   query = "I would like to order some chicken wings"
    # Initialize embeddings and vector store
    # Assuming documents have already been added to the vectorstore
   retriever = SelfQueryRetriever.from_llm(
        llm, vectorstore, document_content_description, metadata_field_info, verbose=True
    )
   response = llm_generate_conversational_response(llm,retriever, query)
   print(response)
if __name__ == "__main__":
    beta_main()
