from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embedding = OpenAIEmbeddings(model = 'text-embedding-3-large', dimension = 32)

result = embedding.embed_query("Who is the president of the United States?")

print(str(result))