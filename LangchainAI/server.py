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


class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.messages = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.messages.append(token)

    def get_messages(self):
        return self.messages

# Create an instance of the custom callback handler
callback_handler = StreamingCallbackHandler()

# Define a regex to capture numbered list items like "1. ", "2. ", etc.
regex_parser = RegexParser(
    regex=r"(\d+)\.\s+(.+?)(?=\d+\.\s+|$)",  # This regex captures "1. " followed by the text
    output_keys=["index", "list_item"]
)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 
CORS(app)  # Enable CORS




# Initialize OpenAI Chat LLM with streaming enabled



llm = ChatOpenAI(
    model = "gpt-4o",
    openai_api_key=openai_api_key,  # Replace with your OpenAI API key
    streaming=True,
    temperature=0.2,
    callbacks=[callback_handler],
    max_tokens = 512,
    max_retries=2
)

#system_prompt = "You are a nutrtion expert that provides accurate and concise answers "

# Define the prompt template
# prompt_template = PromptTemplate(
#     input_variables=["question"],
#     template=f"{system_prompt}\nQ: {{question}}\nA:"
# )





# human_query = "Which protein powder should be avoided for lactose intolerance"

# system_prompt = (
#         "system", "You are a nutriton,personal care expert. Use the following pieces of retrieved context to answer \
#          precise and concise points and insights with source link \
#          If you don't know the answer, say that 'Sorry I dont know the answer' \
#          Start each point with a number followed by a period (e.g., '1. ', '2. ')"
#          "\n\n"
#     "{context}"
#     )



# prompt = ChatPromptTemplate.from_messages (
#     [
#         ("system",  system_prompt),
#         ("human","{input}"),
#     ]     
# )   

# rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

# rag_chain.stream("input":human_query)


message = """

You are a nutriton,personal care expert. Use the following pieces of retrieved context to answer \
         precise and concise points and insights with source link below\
         If you don't know the answer, say that 'Sorry I dont know the answer' \
         Start each point with a number followed by a period (e.g., '1. ', '2. ') \
         Donot show the source link"

{question}

Context:
{context}

"""

prompt = ChatPromptTemplate.from_messages([("human", message)])

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm


# rag_chain = RetrievalQA.from_llm(
#     llm=llm,  # Your existing LLM instance
#     chain_type="stuff",  # Specifies the chain type (you can use 'stuff' or 'map_reduce')
#     retriever=retriever,
#     return_source_documents=True,
#     chain_type_kwargs={"prompt": prompt}  # Your existing prompt template
# )


# Route to accept a question
@app.route('/ask', methods=['POST'])
def ask():
    global latest_question
    latest_question = request.json.get('question', '')
    
    # if latest_question:
    #     print(f"Received message from user: {latest_question}")
    # else:
    #     print("No 'question' key found or question was empty.")

    print(f"Received message from user: {latest_question}")
    return jsonify({"status": "Question received"})

# Route to handle streaming responses
@app.route('/stream', methods=['GET'])
def stream():
    def generate():
        global latest_question
        #callback_handler.messages.clear()  # Clear previous messages
        #chain = prompt | llm
        
        #list_started = False  # Track if we're inside a list


    

        # Invoke the chain; tokens will be added to messages via the callback handler
        #chain.invoke({"question": latest_question})

        # Stream each token as it's received
        #for token in callback_handler.get_messages():
        for token in rag_chain.stream(latest_question):
            yield f"data: {(token.content)}\n\n"  # Convert chunk to a string
            print(f"Streaming token: {token}")  # Debug print
            #yield f"data: {token}\n\n"
            #yield f"data: {token['text']}\n\n"
            #callback_handler.messages = []
            #time.sleep(0.03)
        #     content = token.content.strip()  # Get the token content

        #     # Apply the regex parser to extract numbered list items from the token content
        #     match = regex_parser.parse(content)

        #     if match and 'list_item' in match:
        #         if not list_started:
        #             list_started = True
        #             yield f"data: <ul>\n\n"  # Start the unordered list

        #         # Stream each item as an HTML list item
        #         yield f"data: <li>{match['list_item']}</li>\n\n"
        #     else:
        #         # Stream non-list items or regular text
        #         if list_started:
        #             yield f"data: </ul>\n\n"  # Close the list if not matched
        #             list_started = False
        #         yield f"data: {content}\n\n"  # Stream the regular token content

        # # Close the list at the end if still open
        # if list_started:
        #     yield f"data: </ul>\n\n"



    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True,port='5001')