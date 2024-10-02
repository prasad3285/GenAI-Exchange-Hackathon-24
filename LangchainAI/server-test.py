from flask import Flask, request, jsonify, Response
from langchain.prompts import PromptTemplate
#from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
#from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.callbacks.base import BaseCallbackHandler
from flask_cors import CORS
from langchain_core.prompts import ChatPromptTemplate
import os 
import time
from langchain.output_parsers import RegexParser
from langchain.vectorstores import Chroma
#from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader,TextLoader
from langchain.text_splitter import (CharacterTextSplitter,RecursiveCharacterTextSplitter )
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain_core.runnables import RunnablePassthrough


openai_api_key = os.getenv("OPENAI_API_KEY")

openai_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

loader = PyPDFLoader("C:/Users/guru3/Documents/Guru-24/google Hackathon/data/ConsumerWise RAG.pdf")

pages  = loader.load_and_split()

textsplitter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap= 200)

docs = textsplitter.split_documents(pages)

db = Chroma.from_documents(docs,openai_embeddings)

retriever = db.as_retriever()

llm = ChatOpenAI(
    model = "gpt-4o",
    openai_api_key=openai_api_key,  # Replace with your OpenAI API key
    streaming=True,
    temperature=0,
    #callbacks=[callback_handler],
    max_tokens = 512,
    max_retries=2
)

human_query = "Right protein for specific health concerns"


message = """

You are a nutriton,personal care expert. Strictly use the following pieces of retrieved context to answer \
         precise and concise points\
         If the context  doesnt have specific answers, say that 'Sorry I dont know the answer' \
         Start each point with a number followed by a period (e.g., '1. ', '2. ') \
         Donot show the source link. Give maximum of 9 points in case of a long list"

 

{question}

Context:
{context}

"""

prompt = ChatPromptTemplate.from_messages([("system", message)])

# system_prompt = (
#         "system", "You are a nutriton,personal care expert. Use the following pieces of retrieved context to answer \
#          precise and concise points and insights with source link \
#          If you don't know the answer, say that 'Sorry I dont know the answer' \
#          Start each point with a number followed by a period (e.g., '1. ', '2. ') \
#          Donot provide the document itself as the source but rather relevant Sources inside the document"
#          "\n\n"
#     "{context}"
#     )


# prompt = ChatPromptTemplate.from_messages (
#     [
#         ("system",  system_prompt),
#         ("human","{input}"),
#     ]     
# )   

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

response = rag_chain.invoke(human_query)

print(response.content)

# for token in rag_chain.stream("Which protein powder should be avoided for lactose intolerance"):
#               print(f"Streaming token: {token.content}")
