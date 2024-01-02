# Q&A on your documents
This project implements a chatbot capable of answering questions based on the content of uploaded PDF and DOCX files. The chatbot leverages various natural language processing (NLP) and machine learning techniques, including the OpenAI language model, text embeddings, and document retrieval.

# Quick Start Up 

## Setup the .env file
The project relies on environment variables loaded from a .env file for configuration. Key configuration parameters include OpenAI API key, model details, temperature for language generation, and various file processing parameters.

```
OPENAI_KEY=<you api key> # a subsciption is prefered, as free trial is restrcited in RPMs
OPENAI_API_VERSION="2023-05-15"
SYSTEM_MESSAGE="Awaiting your awesome documents!"
HUGGING_FACE_TRANSFORMER="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# App parameters
TEMPERATURE=0
CHAINLIT_MAX_FILE_SIZE_MB=100
CHAINLIT_MAX_FILES=10
TEXT_SPLITTER_CHUNK_SIZE=1000
TEXT_SPLITTER_CHUNK_OVERLAP=10
EMBEDDINGS_CHUNK_SIZE=16
MAX_RETRIES=5
```
## Plug & Play

1. Clone
```
git clone https://github.com/danielp2797/generative-ai-rag-qa-app
```

2. Initalize container

```
docker-compose up
```

3. Run chainlit app from inside of the container (temporal)

```
chainlit run app.py 
```

# Components

## Relevant Dependencies
- openai: Interface to the OpenAI API for natural language processing.
- chainlit: A library for building asynchronous chat applications.
- langchain: A library for handling natural language processing tasks.
- pypdf: A library for reading PDF files.
- docx: A library for working with DOCX files.
## File Processing
The chatbot prompts the user to upload PDF files.
It processes each uploaded file, extracting text from PDF and DOCX files.
Text is split into smaller chunks for efficient processing.
## Embeddings and Vector Store
OpenAI embeddings are used to convert text chunks into numerical representations.
A FAISS vector store is created to store and retrieve these embeddings efficiently.
## Chat Model
A ChatOpenAI language model is initialized with temperature settings.
## Question Answering Chain
A RetrievalQAWithSourcesChain is created, utilizing the embeddings vector store and ChatOpenAI language model.
The chain is configured to return source documents along with the answer.
## User Interaction
Upon file processing completion, the chatbot informs the user that they can now ask questions.
For each user question, the chatbot queries the chain, handles OpenAI API errors, and extracts the answer and sources from the response.
The answer is presented along with relevant source documents.