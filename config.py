from dotenv import load_dotenv
from typing import Tuple
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import OpenAI
from pandas import DataFrame
from langchain.chains.qa_with_sources.vector_db import VectorDBQAWithSourcesChain
from langchain.chains.question_answering.chain import load_qa_chain
from langchain.callbacks import get_openai_callback
import duckdb
from datetime import datetime

load_dotenv()

config_params = {
    "TEXT_CHUNK_SIZE": 1000,
    "TEXT_CHUNK_OVERLAP": 0,
    "MODEL_MAX_TOKENS": -1,
    "MODEL_TEMPERATURE": 0,
    "CONTEXTO": "Você irá responder as perguntas de um usuário sobre arquivos PDF."
}

def pdf_text_extraction(pdf: str) -> str:
    """
    Extrai texto do arquivo PDF.

    Args:
        pdf (str): Caminho para o arquivo PDF.

    Returns:
        str: Texto extraído do PDF.
    """
    pdf_reader = PdfReader(pdf)
    text = ""

    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

def load_knowledge_base(
        text: str, 
        chunk_size: int = config_params["TEXT_CHUNK_SIZE"],
        chunk_overlap: int = config_params["TEXT_CHUNK_OVERLAP"]
    ) -> FAISS:
    """
    Divide o texto em chunks para inputar no modelo
    de IA generativa - máximo de 4.096 tokens (aprox. 2.000 palavras) - e
    carrega no FAISS (vector store).

    Args:
        text (str): Texto a ser dividido.
        chunk_size (int, optional): Tamanho dos chunks.
        chunk_overlap (int, optional): Intervalo entre chunks.

    Returns:
        FAISS: Vector store com os chunks de texto embutidos.
    """
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base


def question_over_vector_database(
        user_question: str,
        knowledge_base: FAISS = None, 
        max_tokens: int = config_params["MODEL_MAX_TOKENS"],
        temperature: int = config_params["MODEL_TEMPERATURE"],
        context: int = config_params["CONTEXTO"]
    ) -> Tuple[str, any]:
    """
    Usa uma vector store FAISS para responder uma pergunta de um usuário
    usando o modelo da OpenAI (ChatGPT 3.5).

    Args:
        knowledge_base (FAISS): 

    Returns:
        Tuple: Tupla contando a resposta e o callback de custos.
    """
    
    docs = knowledge_base.similarity_search(user_question)

    llm = OpenAI(max_tokens=max_tokens, temperature=temperature)

    chain = load_qa_chain(llm, chain_type="stuff")

    with get_openai_callback() as cb:
        response = chain.run(input_documents=docs, context=context, question=user_question)
    
    return response, cb

def insert_feedback(feedback_slider, feedback_text, original_decision, ai_description, ai_considerations, ai_conclusion):
    conn = duckdb.connect('feedback.db')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS feedbacks (
        feedback_slider INTEGER,
        feedback_text TEXT,
        timestamp TIMESTAMP,
        original_decision TEXT,
        ai_description TEXT, 
        ai_considerations TEXT, 
        ai_conclusion TEXT
    )
    ''')
    
    current_timestamp = datetime.now()
    
    conn.execute('''
    INSERT INTO feedbacks (feedback_slider, feedback_text, timestamp, original_decision, ai_description, ai_considerations, ai_conclusion)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (feedback_slider, feedback_text, current_timestamp, original_decision, ai_description, ai_considerations, ai_conclusion))
    
    conn.close()