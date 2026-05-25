import os
import time
from dotenv import load_dotenv
from datetime import datetime
from groq import Groq
import pandas as pd
import plotly.express as px
import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Running app - Zona 2", layout="centered")

st.title("🏃‍♂️ Running App — Test Progressi Zona 2")
st.write("Monitora i procesi di allenamento")


import os
from dotenv import load_dotenv

load_dotenv()
Chiave = os.getenv("GROQ_API_KEY")
NOME_DATABASE = "diario_running.csv"


# FUNZIONE PER SALVARE I DATI NEL FILE CSV (Aggiornata per Zona 2)
def salva_dati_su_csv(ore_s, qualita_s, acqua, km, tempo_min, passo_medio, fc_zona2, note):
    data_oggi = datetime.now().strftime("%Y-%m-%d %H:%M")

    nuovo_dato = pd.DataFrame(
        [
            {
                "Data": data_oggi,
                "Ore Sonno": ore_s,
                "Qualità Sonno": qualita_s,
                "Idratazione (L)": acqua,
                "Km Corsi": km,
                "Tempo (Minuti)": tempo_min,
                "Passo Medio (min/km)": passo_medio,
                "FC Media Zona 2": fc_zona2,
                "Note": note,
            }
        ]
    )

    if os.path.exists(NOME_DATABASE):
        nuovo_dato.to_csv(NOME_DATABASE, mode="a", header=False, index=False)
    else:
        nuovo_dato.to_csv(NOME_DATABASE, mode="w", header=True, index=False)


# FUNZIONE INTERROGAZIONE GROQ
def interroga_groq(dati_atleta):
    client = Groq(api_key=Chiave)
    prompt_sistema = """
    Sei il Coach AI personale di un uomo di 32 anni che pesa 77,5 kg , un runner esperto focalizzato sull'allenamento in Zona 2 e sulla costruzione della base aerobica. 
    Il tuo tono deve essere tecnico, preciso, motivante e orientato ai dati fisiologici.

    Analizza i dati odierni (sonno, idratazione, km, passo al km e battiti medi in Zona 2) e rispondi in 3 risposte frasi concise e dirette di una 2 righe strutturando il testo in questo modo:

    📈 **EFFICIENZA AEROBICA**: Analizza la relazione tra il Passo Medio e i Battiti in Zona 2 di oggi. Spiega se ci sono miglioramenti/peggioramento
    🔋 **RECUPERO & DIETA**: Valuta se il sonno e l'idratazione hanno supportato la corsa o se hanno penalizzato i battiti.
    📋 **CONSIGLIO TARGET**: Indica quale deve essere il focus del prossimo allenamento (es. mantenere i battiti sotto una certa soglia, allungare la distanza o riposare).

    Chiudi con una domanda tecnica sui suoi parametri o sulle sensazioni muscolari durante la Zona 2.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": dati_atleta},
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=400,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Errore API: {e}"


# --- INTERFACCIA GRAFICA STREAMLIT ---

# Sezione 1: Parametri di Salute
st.subheader("🌙 1. Recupero (Sonno e Idratazione)")
col1, col2 = st.columns(2)
with col1:
    ore_sonno = st.slider("Ore di sonno stanotte:", 3.0, 10.0, 7.0, step=0.5)
    idratazione = st.slider("Acqua bevuta oggi (Litri):", 0.5, 4.0, 2.0, step=0.5)
with col2:
    qualita_sonno = st.select_slider(
        "Qualità del sonno:", options=["Pessima", "Scarsa", "Nella Media", "Buona", "Ottima"]
    )

# Sezione 2: Allenamento e Zona 2 SPECIFICA
st.subheader("🏃‍♂️ 2. Dati della Corsa in Zona 2")
col3, col4, col5 = st.columns(3)

with col3:
    km_corsa = st.number_input("Chilometri corsi oggi:", value=0.0, step=0.1)
with col4:
    tempo_minuti = st.number_input("Tempo totale (in minuti):", value=0, step=1)
with col5:
    fc_zona2 = st.number_input(
        "Battiti Medi della corsa (BPM):", value=135, step=1
    )

# Inserimento del passo medio come stringa per comodità (es: 5:45)
passo_medio_input = st.text_input(
    "Passo Medio al km (Formato Minuti:Secondi, es. 5:30):", value="5:30"
)

# Sezione 3: Note Libere
st.subheader("📝 Note su Dieta e Sensazioni")
note_giornata = st.text_area(
    "Scrivi cosa hai mangiato prima di correre o se avevi dolori:",
    placeholder="Esempio: Pranzo 3 ore prima con riso in bianco. Zona 2 tenuta facilmente, nessuna fatica muscolare.",
)

# BOTTONE DI SALVATAGGIO E ANALISI
if st.button("💾 Salva la sessione e analizza con il Coach"):
    if Chiave == "INSERISCI_QUI_LA_TUA_CHIAVE_GROQ":
        st.error("Ops! Ricordati di inserire la tua chiave Groq nel codice.")
    else:
        # 1. Salvataggio su file
        salva_dati_su_csv(
            ore_sonno,
            qualita_sonno,
            idratazione,
            km_corsa,
            tempo_minuti,
            passo_medio_input,
            fc_zona2,
            note_giornata,
        )
        st.success("✅ Corsa registrata nel database!")

        # 2. Preparazione dati per l'AI
        stringa_per_ai = f"""
        Dati Atleta di oggi:
        - Km Corsi: {km_corsa} km
        - Tempo totale: {tempo_minuti} minuti
        - Passo Medio: {passo_medio_input} min/km
        - Battiti Medi in Corsa: {fc_zona2} BPM
        - Ore Sonno: {ore_sonno} (Qualità: {qualita_sonno})
        - Idratazione: {idratazione} L
        - Note extra: {note_giornata}
        """

        # 3. Chiamata a Groq
        with st.spinner("Il Coach sta calcolando l'efficienza aerobica..."):
            verdetto = interroga_groq(stringa_per_ai)

        st.subheader("📋 Il verdetto sul tuo motore Aerobico:")
        st.info(verdetto)

# --- VISUALIZZAZIONE GRAFICI & DATABASE ---
st.write("---")
st.subheader("📊 Analisi Progressi nel Tempo")

if os.path.exists(NOME_DATABASE):
    df = pd.read_csv(NOME_DATABASE)

    if len(df) > 0:
        # Mostriamo il grafico dell'andamento dei battiti cardiaci durante le corse
        fig_fc = px.line(
            df,
            x="Data",
            y="FC Media Zona 2",
            title="Andamento dei Battiti Medi in Corsa (L'obiettivo è tenerli stabili o calanti a parità di ritmo)",
            markers=True,
        )
        st.plotly_chart(fig_fc, use_container_width=True)

    st.subheader("📋 Storico Allenamenti Zona 2")
    st.dataframe(df.iloc[::-1], use_container_width=True)
else:
    st.info(
        "Database pronto per la Zona 2. Registra il primo allenamento per vedere i grafici!"
    )