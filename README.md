# generative-ai-rag-qa-app

Setup int the .env file

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
How to run the project

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
