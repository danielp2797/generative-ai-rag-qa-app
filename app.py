import os
import io
import sys
import time
import openai
import random
import logging
import chainlit as cl
from dotenv import load_dotenv
from dotenv import dotenv_values
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from pypdf import PdfReader
from docx import Document

load_dotenv()
# Read environment variables
temperature = float(os.environ.get("TEMPERATURE", 0.9))
api_key = os.getenv("OPENAI_KEY")
model_id = os.getenv("HUGGING_FACE_TRANSFORMER")
max_size_mb = int(os.getenv("CHAINLIT_MAX_FILE_SIZE_MB", 100))
max_files = int(os.getenv("CHAINLIT_MAX_FILES", 10))
text_splitter_chunk_size = int(os.getenv("TEXT_SPLITTER_CHUNK_SIZE", 1000))
text_splitter_chunk_overlap = int(os.getenv("TEXT_SPLITTER_CHUNK_OVERLAP", 10))
embeddings_chunk_size = int(os.getenv("EMBEDDINGS_CHUNK_SIZE", 16))
max_retries = int(os.getenv("MAX_RETRIES", 16))


openai.api_key = api_key

# Load environment variables from .env file
if os.path.exists(".env"):
    load_dotenv(override = True)
    config = dotenv_values(".env")

logging.basicConfig(stream = sys.stdout,
                    format = '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    level = logging.INFO)
logger = logging.getLogger(__name__)

# Configure system prompt
PROMPT_TEMPLATE = """Use the following pieces of context to answer the users question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.
The "SOURCES" part should be a reference to the source of the document from which you got your answer.

Example of your response should be:

---

The answer is foo
SOURCES: xyz

---

Begin!
----------------
{summaries}"""

messages = [
    SystemMessagePromptTemplate.from_template(PROMPT_TEMPLATE),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)
chain_type_kwargs = {"prompt": prompt}

@cl.on_chat_start
async def start():
    await cl.Avatar(
        name = "Chatbot",
        url = "https://cdn-icons-png.flaticon.com/512/8649/8649595.png"
    ).send()
    await cl.Avatar(
        name = "Error",
        url = "https://cdn-icons-png.flaticon.com/512/8649/8649595.png"
    ).send()
    await cl.Avatar(
        name = "User",
        url = "https://media.architecturaldigest.com/photos/5f241de2c850b2a36b415024/master/w_1600%2Cc_limit/Luke-logo.png"
    ).send()

    # Initialize the file list
    files = None

    # Wait for the user to upload a file
    while files  ==  None:
        files = await cl.AskFileMessage(
            content = f"Please upload up to {max_files} `.pdf` files to begin.",
            accept = ["application/pdf"],
            max_size_mb = max_size_mb,
            max_files = max_files,
            timeout = 43200,
            raise_on_timeout = True
        ).send()

    # Inform the user that the files are being processed
    files_names = [f"`{f.name}`" for f in files]
    content = f"Processing {', '.join(files_names)}..."
    msg = cl.Message(content = content, author = "Chatbot")
    await msg.send()

    # Create a list to store the texts of each file
    all_texts = []

    # Process each file uplodaded by the user
    for file in files:

        # Create an in-memory buffer from the file content
        bytes = io.BytesIO(file.content)

        # Get file extension
        extension = file.name.split('.')[-1]

        # Initialize the text variable
        text = ''

        # Read the file
        if extension  ==  "pdf":
            reader = PdfReader(bytes)
            for i in range(len(reader.pages)):
                text +=  reader.pages[i].extract_text()
        elif extension  ==  "docx":
            doc = Document(bytes)
            paragraph_list = []
            for paragraph in doc.paragraphs:
                paragraph_list.append(paragraph.text)
            text = '\n'.join(paragraph_list)

        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = text_splitter_chunk_size,
            chunk_overlap = text_splitter_chunk_overlap
            )
        texts = text_splitter.split_text(text)

        # Add the chunks and metadata to the list
        all_texts.extend(texts)

    # Create a metadata for each chunk
    metadatas = [{"source": f"{i}-pl"} for i in range(len(all_texts))]

    # Create a Chroma vector store
    embeddings = HuggingFaceEmbeddings(
        model_name=model_id
        )

    # Create a Chroma vector store
    db = await cl.make_async(Chroma.from_texts)(
        all_texts, embeddings, metadatas = metadatas
    )

    # Create a ChatOpenAI llm
    llm = ChatOpenAI(
        temperature = temperature,
        openai_api_key = openai.api_key
        )

    # Create a chain that uses the Chroma vector store
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm = llm,
        chain_type = "stuff",
        retriever = db.as_retriever(),
        return_source_documents = True,
        chain_type_kwargs = chain_type_kwargs
    )

    # Save the metadata and texts in the user session
    cl.user_session.set("metadatas", metadatas)
    cl.user_session.set("texts", all_texts)

    # Create a message to inform the user that the files are ready for queries
    content = ''
    if (len(files)  ==  1):
        content = f"`{files[0].name}` processed. You can now ask questions!"
    else:
        files_names = [f"`{f.name}`" for f in files]
        content = f"{', '.join(files_names)} processed. You can now ask questions."
    msg.content = content
    msg.author = "Chatbot"
    await msg.update()

     # Store the chain in the user session
    cl.user_session.set("chain", chain)

@cl.on_message
async def run(message: str):
    # Retrieve the chain from the user session
    chain = cl.user_session.get("chain")
    
    # Initialize the response
    response =  None

    # Retry the OpenAI API call if it fails
    for attempt in range(max_retries):
        try:

            print(message.content)
            # Ask the question to the chain
            response = await chain.acall(
                message.content,
                callbacks = [cl.AsyncLangchainCallbackHandler()]
            )
            print(response)
            break
        
        except Exception as e:
            logger.exception(f"An error occurred. {e}")
            break

    # Get the answer and sources from the response
    answer = response["answer"]
    sources = response["sources"].strip()
    source_elements = []

    # Get the metadata and texts from the user session
    metadatas = cl.user_session.get("metadatas")
    all_sources = [m["source"] for m in metadatas]
    texts = cl.user_session.get("texts")

    if sources:
        found_sources = []

        # Add the sources to the message
        for source in sources.split(","):
            source_name = source.strip().replace(".", "")
            # Get the index of the source
            try:
                index = all_sources.index(source_name)
            except ValueError:
                continue
            text = texts[index]
            found_sources.append(source_name)
            # Create the text element referenced in the message
            source_elements.append(cl.Text(content = text, name = source_name))

        if found_sources:
            answer +=  f"\nSources: {', '.join(found_sources)}"
        else:
            answer +=  "\nNo sources found"

    await cl.Message(content = answer, elements = source_elements).send()