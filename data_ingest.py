from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader

from langchain_openai import OpenAIEmbeddings

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

import os
from dotenv import load_dotenv
load_dotenv()


# Set API keys
os.environ['OPENAI_API_KEY'] =  os.getenv("OPENAI_API_KEY")

os.environ['PINECONE_API_KEY'] = os.getenv("PINECONE_API_KEY")

index_name = "branding-course"
embeddings = OpenAIEmbeddings()


folder_path = "./files"


    
 

def create_vectordb(folder_path):
    
    loader = DirectoryLoader(folder_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False
    )
    docs = splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings()
    vectordb = PineconeVectorStore.from_documents(
    docs,
    index_name=index_name,
    namespace= "brandingcourse",
    embedding=embeddings
)
    
    return vectordb

if __name__ == "__main__":
    create_vectordb(folder_path)

