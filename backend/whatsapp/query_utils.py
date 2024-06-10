import os
from langchain_core.documents import Document
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
import pinecone
from langchain.chains.query_constructor.base import AttributeInfo

from .data.generation import setup_pinecone()


os.environ["PINECONE_API_KEY"] = "435898e5-fd77-4b74-8c39-a06995fbefad"
os.environ[
    "ANTHROPIC_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw"
ENVIRONMENT = "us-east-1"
INDEX_NAME = "foodnest-order"


def categorize_query(query):
    prompt =  ''' [SYSTEM PROMPT]
             you will be give a given query after this sentence separated by two linebreaks. Your job is to categorize if that query is :
             A. Normal Conversation : If its a noraml conversation happening between the model and user. Then only respond with normal_conversaiton
             B. Ordering food : If it seems like the user has decided to add any dish to his cart. Then only respond with food_order
             Here's the user query : \n\n'''

    prompt+=query