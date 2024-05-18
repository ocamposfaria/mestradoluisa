import streamlit as st
import pandas as pd 
import concurrent.futures
from config import *

st.set_page_config(layout="wide")
df = pd.read_csv('data.csv', delimiter=';')
ai_answers = [None] * len(df['Pergunta'])

col01, col02, col03, col04 = st.columns(4)

with col01:
  st.image('image.png')
st.header('Proposta de algoritmo para análise de formulários do CADE com LLM e LangChain')

col11, col12, col13, col14 = st.columns(4)
with col11:
  pdf = st.file_uploader("suba o arquivo PDF aqui", type="pdf", label_visibility='hidden')

col21, col22, col23, col24 = st.columns(4)

with col21:
  generate = st.button('Gerar respostas do LLM', use_container_width=True)


if pdf:
  text = pdf_text_extraction(pdf)
  knowledge_base = load_knowledge_base(text)


if generate:
  if not pdf:
    st.error('Você precisa subir um PDF antes de fazer isso.')
  else:
    st.success('Extraindo informações do PDF...')
    
    with concurrent.futures.ThreadPoolExecutor() as executor:

        future_to_index = {
            executor.submit(lambda idx, i: (idx, question_over_vector_database(user_question=i, knowledge_base=knowledge_base)[0]), idx, i): idx
            for idx, i in enumerate(df['Pergunta'].to_list())
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
          idx, response = future.result()
          ai_answers[idx] = response

if ai_answers != []:
  df['Resposta do Large Language Model'] = ai_answers

df.index += 1
st.dataframe(df, use_container_width=True, height=650)




