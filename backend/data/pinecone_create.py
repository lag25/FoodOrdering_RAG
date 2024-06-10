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
os.environ["PINECONE_API_KEY"] = "04d5a86b-edfb-4cb3-86bb-0638717ce4af"
ENVIRONMENT = "us-east-1"
INDEX_NAME = "foodnest"

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
    restaurant_data = [
        {"id": r.id, "name": r.name, "description": r.description, "address": r.address, "google_maps": r.google_maps_link}
        for r in restaurants
    ]
    restaurant_df = pd.DataFrame(restaurant_data)

    food_data = [
        {"id": f.id, "restaurant_id": f.restaurant_id, "name": f.name, "description": f.description, "price": f.price}
        for f in foods
    ]
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
    df["food_text"] = "\n-" + df["food_name"] + "\n" + df["food_description"] + "\npIt's price is:" + df["price"].astype(str)

    df = df.groupby("id").agg({"name": "first", "description": "first", "food_text": "sum"}).reset_index()

    # Creating text for embedding
    df["text"] = (
        "```" + df["name"] + "\nRestaurant description: " + df["description"] + "\nFood available:" + df["food_text"] + "\n```"
    )

    # Convert to LangChain Documents
    documents = [
        Document(
            page_content=row["text"],
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


def setup_pinecone(documents):
    # Initialize the embeddings and vectorstore
    pc = pinecone.Pinecone("04d5a86b-edfb-4cb3-86bb-0638717ce4af")
    index = pc.Index("example")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Pinecone(index=index, text_key=os.environ["PINECONE_API_KEY"], embedding = embeddings) #index_name=INDEX_NAME, api_key=os.environ["PINECONE_API_KEY"], environment=ENVIRONMENT
    print(dir(vectorstore))
    # Create and add documents to the vectorstore
    vectorstore.add_documents(documents)
    print('embeddings succesfully created')
    return vectorstore

def alpha_main():
    documents = process_restaurants()
    vectorstore = setup_pinecone(documents)

if __name__ == "__main__":
    alpha_main()
