from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

loader=DirectoryLoader('data/', glob='**/*.pdf', loader_cls=PyMuPDFLoader)
documents=loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)
print("Total chunks:", len(chunks))
print(chunks[1].page_content)
print(chunks[1].metadata)
embeddings=HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en",
    encode_kwargs={"normalize_embeddings": True}
)

vector_db=Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="vector_db"
) 
vector_db.persist()