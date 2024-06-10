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
import bs4
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

os.environ["PINECONE_API_KEY"] = "04d5a86b-edfb-4cb3-86bb-0638717ce4af"
os.environ[
    "ANTHROPIC_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDBMa_0v2me-OT5tr-yToNb6ttT3JcdpPw"
ENVIRONMENT = "us-east-1"
INDEX_NAME = "foodnest"

# System prompt definition


def get_pinecone():
    pc = pinecone.Pinecone("04d5a86b-edfb-4cb3-86bb-0638717ce4af")
    index = pc.Index("example")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Pinecone(index=index, text_key=os.environ["PINECONE_API_KEY"], embedding=embeddings)
    return vectorstore





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
    prompt += f"Given the following restaurants suggest various dishes and multiple restaurants to the customer and tell them why. You are only exclusively supposed to suggest the dishes I gave you and not create on your own Furthermore, you response can ocassionally be in bullet points if needed. Heres the restaurants' info: {restaurant_infos[::]}\n\n"
    prompt += f"You also have the ability to use context from past messages to give a sensible response to the current user query. The past chat history between you and the user is Chronologically given here\n\n"
    prompt += f"{chat_history}\n"
    prompt += "The current user query you have to respond to is given here\n"
    prompt += f"User: {query}\n\n"

    # Use the LLM to generate a conversational response
    response = llm.invoke(prompt)
    return response.content



def generate(user_query):
    system_prompt = """[Context]
    You are a chatbot for foodNEST, the leading food delivery platform in India
    Your primary goal is to assist customers in finding and ordering their favorite meals from a wide variety of restaurants with ease and convenience.
    Whenever a customer talks to you, you are always polite and friendly and make small talk if the customer seems to be indulging in it. You are fluent in both English and Hindi and occasionally you respond in Hinglish.

    As a delivery app chatbot, you are friendly, approachable, and always eager to help.
    You understand that hunger can sometimes make people impatient, so you strive to provide quick and efficient service with a touch of humor to lighten the mood
    Your functionalities include helping users browse through restaurant menus, suggesting popular dishes based on their preferences and guiding them through the ordering process


    Your personality is like that of a waiter. It is a perfect blend of professionalism and playfulness, making you an enjoyable and reliable companion for users seeking a satisfying meal delivered right to their doorstep
    You are concise with your answers. You do not answer with more than 70 words."""


    llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ["GOOGLE_API_KEY"])
    vectorstore = get_pinecone()
    retriever = vectorstore.as_retriever()
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    ### Answer question ###
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    ### Statefully manage chat history ###
    store = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain.invoke(
    {"input": user_query},
    config={
        "configurable": {"session_id": "abc123"}
    },  # constructs a key "abc123" in `store`.
)["answer"]



if __name__ == "__main__":
    while True:                                                                                 # For the testing script
        print(generate(input())+"\n\n")
