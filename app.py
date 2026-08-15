import os
import sys
from odf.opendocument import load
from odf.text import ListItem
from odf.teletype import extractText
from google import genai
from google.genai import types
import streamlit as st


# Page Configuration & Setup

st.set_page_config(page_title="ABC Communication Assistant", page_icon="💬")
st.title("💬 ABC Communication")


@st.cache_data
def load_data_and_prompt():
    Infos =['Numéro pour appeler l’agence ABC communication: +229555 ou 555',
     'Code pour se rappeler de son numéro : *5550#',
     'Crédit simple: vous pouvez acheter pour tout montant',
     'Forfait appel : 100f, 150f, 500f,5000f,10000f',
     'Forfait internet : 100f, 150f, 500f,5000f,10000f',
     'illimité 30 jours: 5000f,10000f,15000f',
     'Acheter de crédit à partir de son compte Mobile mony',
     'Code pour achat credit simple :composez *5551*1# et ecrivez le montant puis envoyez. Vous serez demandé à mentionner votre code PIN. Ecrivez votre code PIN en toute securité puis envoyez.',
     'Code pour achat forfait appel :composez *5551*2*1# . Dans le menu suivant, sélectionnez parmi les offres de forfait appel disponible, celle qui correspond à votre besion.Vous serez demandé à mentionner votre code PIN. Ecrivez votre code PIN en toute securité puis envoyez.',
     'Code pour achat forfait internet :composez *5551*2*2# . Dans le menu suivant, sélectionnez parmi les offres de forfait internet disponible, celle qui correspond à votre besion.Vous serez demandé à mentionner votre code PIN. Ecriver votre code PIN en toute securité puis envoyez.',
     'Code pour achat illimite :composez *5551*2*3# . Dans le menu suivant, sélectionnez parmi les offres d’illimité disponibles, celle qui correspond à votre besion.Vous serez demandé à mentionnervotre code PIN. Ecriver votre code PIN en toute securité puis envoyez.',
     'Vérifier sa solde',
     'Code balance check Crédit simple :composez *5552*1# ',
     'Code balance check forfait appel :composez *5552*2*1# ',
     'Code balance check forfait internet: composez *5552*2*2# ',
     'Code balance check illimité: ccomposez *5552*2*3# '
    ]
    # Load system prompt from ODT file
    odt_path = "system_prompt.odt"
    doc = load(odt_path)
    system_prompt_list = [extractText(i) for i in doc.getElementsByType(ListItem)]
    
    return Infos, system_prompt_list

Infos, system_prompt = load_data_and_prompt()

#  core pipeline functions
def build_gemini_contents(messages, infos):
    contents=[]
    # Fold reference info into the first user turn's parts, not as a separate fake message
    for i, msg in enumerate(messages):
        role = "model" if msg["role"] == "assistant" else "user"
        text = msg["content"]
        if i == 0:
            text = "Informations disponibles : " + " ".join(infos) + "\n\nQuestion : " + text
        contents.append({"role":role,"parts":[{"text":text}]})
    return contents

def improve_prompt(system_prompt):
    return " ".join(system_prompt)
    

def run_pipeline(system_prompt, content):
    client=genai.Client(api_key="Your API key")
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=content,
        config=types.GenerateContentConfig(
            system_instruction=improve_prompt(system_prompt=system_prompt)
        )
    )
    return response.text

# Chat History Initialization

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous conversation history on app refresh
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#  User Interaction & Query Execution
user_input = st.chat_input("Posez votre question ici...")
if user_input:
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    #  Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours..."):
            response_text = run_pipeline(
                system_prompt=system_prompt, 
                content=build_gemini_contents(st.session_state.messages, Infos)
            )
            st.markdown(response_text)

    #  Save assistant message to session history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
