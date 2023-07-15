import openai
import os
import glob, re, pandas as pd
from dotenv import load_dotenv
from openai.embeddings_utils import get_embedding
import shutil
import numpy as np

load_dotenv()
openai.api_key = os.getenv('api_key')
embedding_engine = "text-embedding-ada-002"
data_dir = glob.glob("data/*")

try:
    data_frame = pd.read_csv("embedded_data.csv")
except:
    data_frame = pd.DataFrame(columns=['text', 'embeddings'])

def refine_str(text_str):
    text_str = text_str.lstrip()
    text_str = re.sub(r'\n\s*\n', '\n', text_str, flags=re.MULTILINE) # remove multilines
    text_str = re.sub(r" {2,}", "", text_str) # remove consecutive space
    return text_str

def get_file_name(file_path):
    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0] 
    return file_name

def split_to_paragraphs(text_str, min_len=300):
    lines = text_str.splitlines()
    paragraphs = []
    paragraph = ""
    for line in lines:
        paragraph += line.rstrip() + " "  
        if len(paragraph) > min_len:
            paragraphs.append(paragraph)
            paragraph = ""

    if len(paragraph) > 0:
        paragraphs.append(paragraph)
    return paragraphs

paragraphs = []
for file_path in data_dir:
    file_name = get_file_name(file_path)
    with open(file_path, "r") as file:
        context = refine_str( file.read() )
        paragraphs += split_to_paragraphs(context)
    shutil.move(file_path, "data_embedded")

batch_size = 50
for i in range(0, len(paragraphs), batch_size):
    batch_paragraphs = paragraphs[i:i+batch_size]
    batch_embeddings = openai.Embedding.create(input=batch_paragraphs,engine=embedding_engine)['data']
    batch_rows = []
    for i, paragraph in enumerate(batch_paragraphs):
        new_row = {
            "text": paragraph,
            "embeddings": batch_embeddings[i]['embedding']
        }
        batch_rows.append(new_row)
    data_frame = pd.concat([data_frame, pd.DataFrame(batch_rows)], ignore_index=True)
data_frame.to_csv('embedded_data.csv')