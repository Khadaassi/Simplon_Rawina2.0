from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    return ChatOllama(model="mistral", temperature=0.7)


def get_groq_llm():
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="meta-llama/llama-4-maverick-17b-128e-instruct")
    return llm
