import streamlit as st
from config import *

pdf = False
is_file_valid = False

st.image('image.png')

st.markdown('### Proposta de Sistema para Decisões Automatizadas')

st.markdown('---')

css='''
<style>
[data-testid="stFileUploaderDropzone"] div div::before {content:"Clique aqui para importar seu formulário."}
[data-testid="stFileUploaderDropzone"] div div span{display:none;}
[data-testid="stFileUploaderDropzone"] div div::after {font-size: .8em; content:"Ele precisa ser um PDF que contenha textos."}
[data-testid="stFileUploaderDropzone"] div div small{display:none;}
[data-testid="stFileUploaderDropzone"] button{display:none;}
.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}
</style>
'''

st.markdown(css, unsafe_allow_html=True)


if not pdf:
  pdf = st.file_uploader(label=" ")

  col11, col12, col13 = st.columns(3)
  
  with col12:
    run_button = st.button('Gerar decisão', use_container_width=True)

if not pdf and run_button:
  st.error('Você precisa subir um PDF antes de fazer isso.')

if pdf and run_button:
    st.success('Trabalhando, aguarde...')

    st.session_state['respostas'] = {}
    text = pdf_text_extraction(pdf)
    knowledge_base = load_knowledge_base(text)

    resposta1 = question_over_vector_database('Você é um assistente do CADE, e precisa passar informações a um operador. A partir do formulário que eu enviei, descreva em detalhes (até 10 linhas) a descrição da operação. Na sua reposta, cite as requerentes, e o fim que pretendem atingir com a operação.', knowledge_base)[0]
    st.session_state['respostas']['resposta1'] = resposta1

    resposta2 = question_over_vector_database("""Você é um assistente do CADE, e precisa passar informações a um operador. Preciso que você analise os seguintes critérios e escreva um texto de 20 linhas ou mais, com base no formulário que eu te enviei. Ao final, responda se a operação pode ser aprovada.
      - Justificativa estratégica e econômica para a operação;
      - Natureza da operação;
      - Abrangência das atividades das partes; (pode ser total, parcial ou não se aplica)
      - Se é aquisição de ativos, aquisição de participação societária, e/ou joint venture;
      - Se houve notificações em outras jurisdições; (Sim ou Não)
      - Se há cláusula de não concorrência; (Sim ou Não)
      - Definição dos mercados relevantes afetados sob as dimensões de produto e geográfica, descrevendo detalhadamente os produtos fornecidos bem como as localidades (cidade, estado, bairro ou país) onde são fornecidos;
      - Grau (percentual aproximado) substitutibilidade dos produtos;
      - Existência de sobreposição horizontal e grau aproximado em percentual (se houver o mesmo produto oferecido na mesma localidade);
      - Existe integração vertical e grau aproximado em percentual (se houver o fornecimento de serviços complementares numa mesma localidade);
      - Suas observações finais.
    No final, formate o texto para uma leitura em texto corrido, evite a estrutura de tópicos.""", knowledge_base)[0]
    st.session_state['respostas']['resposta2'] = resposta2

    resposta3 = question_over_vector_database(f"""Com base no texto a seguir, escreva se a operação pode ou não ser aprovada sem restrições, ou se merece melhor análise: {resposta2}""", knowledge_base)[0]
    st.session_state['respostas']['resposta3'] = resposta3

if pdf and 'respostas' in st.session_state:

    st.markdown('---')

    st.markdown('### Descrição da operação')

    st.markdown(st.session_state['respostas']['resposta1'])

    st.markdown('### Considerações sobre a operação')

    st.markdown(st.session_state['respostas']['resposta2'])

    st.markdown('### Conclusão')

    st.markdown(st.session_state['respostas']['resposta3'])

    st.markdown('---')

    st.markdown('### Envie seu feedback')

    with st.form(key='my_form'):
      feedback_slider = st.select_slider("Com uma nota de 1 a 10, avalie a decisão gerada automaticamente", options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
      
      feedback_text = st.text_area('Utilize o espaço abaixo para tecer comentários e/ou sugerir melhorias')

      col21, col22, col23 = st.columns(3)
      
      with col22:
        feedbacks_button = st.form_submit_button('Enviar feedback', use_container_width=True)

      if feedbacks_button:
        insert_feedback(feedback_slider, feedback_text)
        st.success('Feedback enviado com sucesso!')