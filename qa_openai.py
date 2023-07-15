import openai
import os
from dotenv import load_dotenv
import pandas as pd
from openai.embeddings_utils import distances_from_embeddings

load_dotenv()
openai.api_key = os.getenv('api_key')
completions_model = "gpt-3.5-turbo"
embedding_engine = "text-embedding-ada-002"
data_frame = pd.read_csv('embedded_data.csv')
limit_para = 5

embeddings = []
for embed in data_frame['embeddings'].values:
    embeddings.append( eval(embed) )     
    
def create_context(question, df):
    embedded_question = openai.Embedding.create(
        input=f"{question}",#. Focus on the time, person name or location",
        engine=embedding_engine
    )['data'][0]['embedding']
    df['distances'] = distances_from_embeddings(embedded_question, embeddings, distance_metric='cosine')
    context = ""
    cur_limit_para = limit_para
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        context += row['text']
        cur_limit_para -= 1
        if cur_limit_para == 0: break
    return context
    
def answer_question(question):
    prompt = f"""
            context = {create_context(question, data_frame)}
            question: {question}
        """
    messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role":"user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=completions_model,
        messages=messages,
    )
    return response['choices'][0]['message']['content']
