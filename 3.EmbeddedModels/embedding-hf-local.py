from langchain_huggingface import HuggingFaceEmbeddings

"""
You need to install sentence-transformers as well:
pip3 install -U sentence-transformers

"""

embedding = HuggingFaceEmbeddings(model = 'sentence-transformers/all-MiniLM-L6-v2')

# text = "The capital of France is Paris."

documents = [
    "Delhi is the capital of India",
    "Kolkata is the capital of West Bengal",
    "Paris is the capital of France"
]

# vector = embedding.embed_query(text)

vector = embedding.embed_documents(documents)

print(str(vector))