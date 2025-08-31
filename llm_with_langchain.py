import os
from tempfile import template
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import pandas as pd

# --- Fonctions pour l'interaction avec le LLM via l'API Google Gemini ---
# Fonction d'appel sans langchain
def get_gemini_response(prompt: str) -> str:
    """
    Appelle l'API de Google Gemini pour obtenir une réponse.
    """
    try:
        # Obtenez votre clé d'API depuis les secrets Streamlit
        api_key = st.secrets["GEMINI_API_KEY"]

        # Appelez le modèle Gemini 1.5 flash test via Langchain
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=api_key)
        response = model.invoke(prompt)
        return response.text()
    
    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API Gemini: {e}")
        st.error("Assurez-vous d'avoir une clé d'API valide et de l'avoir ajoutée à vos secrets Streamlit sous le nom 'GEMINI_API_KEY'.")
        return "Désolé, je ne peux pas générer de réponse pour le moment."

# Fonction d'appel avec LangChain
def get_gemini_response_with_langchain(prompt_template, memory) -> str:
    """
    Appelle le LLM Gemini en utilisant une chaîne LangChain.
    """
    try:
        # Initialisez le modèle avec la clé API
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=st.secrets["GEMINI_API_KEY"], temperature=0)

        # Créez la chaîne (Chain)
        chain = LLMChain(
            prompt=prompt_template,
            llm=llm,
            memory=memory
        )
        response = chain.invoke({
        "dataframe_context": dataframe_context,
        "user_question": user_question,
        })
        return response['text']

    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API via LangChain: {e}")
        return "Désolé, je ne peux pas générer de réponse pour le moment."

# --- Prompt Generation ---

def create_prompt(user_question: str, dataframe_context: str, chat_history: list) -> str:
    """Crée le prompt pour le LLM."""
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    prompt_template = f"""
[INST]
You are a helpful AI chat assistant. Answer the user's question based on the provided
chat history and the context data from datas provided.

Use the data in the <context> section to inform your answer about customer reviews or sentiments
if the question relates to it. If the question is general and not answerable from the context
or chat history, answer naturally. Do not explicitly mention "based on the context" unless necessary for clarity.

<chat_history>
{history_str}
</chat_history>

<context>
{dataframe_context}
</context>

<question>
{user_question}
</question>
[/INST]

Answer:
"""
    prompt = prompt_template.strip()
    return prompt

def create_prompt_for_langchain(user_question: str, dataframe_context: str, chat_history: list) -> str:
    # --- Prompt Generation avec LangChain ---
    # Créez le modèle de prompt pour la chaîne
    template = """
You are a helpful AI chat assistant. Answer the user's question based on the provided chat history and the context data from the <context> section.
Use the data in the <context> section to inform your answer about customer reviews or sentiments if the question relates to it. If the question is general and not answerable from the context or chat history, answer naturally. Do not explicitly mention "based on the context" unless necessary for clarity.

chat history : {chat_history}
<context>
{dataframe_context}
</context>

user's question : '''{user_question}'''
Answer:
"""
    prompt_template = ChatPromptTemplate.from_template(template)
    return prompt_template


# --- Configuration et variables d'état ---
st.set_page_config(layout="wide")
st.title("LLM with langchain")
st.subheader("Chatbot utilisant Gemini pour analyser les données et fournir une réponse.")

# Initialiser l'état de session sans langchain si ce n'est pas déjà fait
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "df_context" not in st.session_state:
    st.session_state.df_context = "Pas de données de contexte pour le moment."

# Obtenez votre clé d'API depuis les secrets Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Erreur: La clé 'GEMINI_API_KEY' n'est pas trouvée dans vos secrets Streamlit.")
    st.stop() # Arrête l'exécution si la clé n'est pas trouvée


# --- Interface utilisateur de streamlit ---
user_question = st.text_input("Posez votre question:")
dataframe_context = st.session_state.df_context
df = pd.read_csv("C:/Users/ambre/Documents/GenAI APP/Student Stress Monitoring Datasets/Stress_Dataset.csv")
st.session_state.df_context = df.head().to_string()  # Met à jour le contexte avec les lignes du DataFrame

# --- Prompt Generation sans langchain ---
prompt = create_prompt(user_question, dataframe_context, st.session_state.chat_history)
st.session_state.chat_history.append({"role": "user", "content": user_question})
st.write(get_gemini_response(prompt))


# --- L'approche avec LangChain ---
# Initialiser l'état de session avec langchain si ce n'est pas déjà fait
if "chat_history_with_langchain" not in st.session_state:
    st.session_state.chat_history_with_langchain = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=st.session_state.chat_history_with_langchain,
    memory_key="chat_history_with_langchain",
    input_key="user_question"  # La clé de la question de l'utilisateur
)
# Créer la chaîne LangChain en dehors de la boucle d'interaction et la stocker dans l'état de la session Streamlit
if "llm_chain" not in st.session_state:
    # Définir le template directement ici pour inclure l'historique
    template = """
You are a helpful AI chat assistant. Answer the user's question based on the provided chat history and the context data from the <context> section.
Use the data in the <context> section to inform your answer about customer reviews or sentiments if the question relates to it. If the question is general and not answerable from the context or chat history, answer naturally. Do not explicitly mention "based on the context" unless necessary for clarity.

chat history : {chat_history_with_langchain}
<context>
{dataframe_context}
</context>

user's question : '''{user_question}'''
Answer:
"""
    prompt_template = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=st.secrets["GEMINI_API_KEY"], temperature=0)
    st.session_state.llm_chain = LLMChain(
        prompt=prompt_template,
        llm=llm,
        memory=memory
   )
if user_question:
    # Exécutez la chaîne avec les variables
    st.write(st.session_state.llm_chain.invoke({
        "dataframe_context": dataframe_context,
        "user_question": user_question,
    })["text"])