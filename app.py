import json
import streamlit as st
import pandas as pd

# --- INTERFACCIA GRAFICA STREAMLIT ---
st.set_page_config(page_title="Chi non mi segue?", page_icon="🕵️", layout="centered")

st.title("🕵️ Analisi Instagram")
st.markdown("Scopri chi non ricambia il follow. I tuoi dati sono sicuri: non salviamo nulla.")

# --- ISTRUZIONI PER L'USO ---
with st.expander("❓ Come scaricare i file JSON da Instagram"):
    st.markdown("""
    Per usare questa app, devi richiedere i tuoi dati ufficiali a Instagram. Segui questi passaggi dal tuo telefono:
    1. Apri l'app di Instagram e vai sul tuo profilo.
    2. Tocca il menu in alto a destra (le tre linee) e vai su **La tua attività**.
    3. Scorri fino in fondo e tocca **Scarica le tue informazioni**.
    4. Tocca **Scarica o trasferisci informazioni**, seleziona il tuo profilo Instagram e scegli **Alcune delle tue informazioni**.
    5. Scorri fino alla sezione *Connessioni*, seleziona **Follower e seguiti** e vai avanti.
    6. Seleziona *Scarica sul dispositivo*. **IMPORTANTE:** cambia il formato da HTML a **JSON** e l'intervallo di date in **Dall'inizio**.
    7. Tocca **Crea file**.
    
    *Instagram ti invierà un'email (di solito entro pochi minuti). Scarica il file ZIP, estrailo, e troverai i due file che ti servono nella cartella `connections/followers_and_following`.*
    """)

st.divider()

# --- CARICAMENTO FILE ---
col1, col2 = st.columns(2)
with col1:
    file_seguiti = st.file_uploader("📂 Carica following.json", type=['json'])
with col2:
    file_follower = st.file_uploader("📂 Carica followers_1.json", type=['json'])

# --- LOGICA DELL'APP ---
if file_seguiti is not None and file_follower is not None:
    dati_seguiti = json.load(file_seguiti)
    dati_follower = json.load(file_follower)
    
    seguiti = set()
    follower = set()

    # Estrazione seguiti
    if isinstance(dati_seguiti, dict) and 'relationships_following' in dati_seguiti:
        for item in dati_seguiti['relationships_following']:
            if 'title' in item:
                nome = item['title'].strip()
                if nome != "" and "deleted" not in nome.lower():
                    seguiti.add(nome)

    # Estrazione follower
    if isinstance(dati_follower, list):
        for item in dati_follower:
            if 'string_list_data' in item and len(item['string_list_data']) > 0:
                dati_stringa = item['string_list_data'][0]
                if 'value' in dati_stringa:
                    nome = dati_stringa['value'].strip()
                    if nome != "" and "deleted" not in nome.lower():
                        follower.add(nome)
    
    st.divider()
    st.subheader("📊 Statistiche Pulite")
    m1, m2 = st.columns(2)
    m1.metric(label="Tu segui", value=len(seguiti))
    m2.metric(label="Ti seguono", value=len(follower))

    st.markdown("### 👻 Controllo account sospesi")
    numero_app = st.number_input("Seguiti sulla tua app di Instagram:", min_value=0, value=394)
    scarto = len(seguiti) - numero_app
    
    if scarto > 0:
        st.warning(f"Nel file ci sono **{scarto} account in più** rispetto all'app. Sono account temporaneamente disabilitati o bloccati da Instagram.")
        with st.expander(f"🔍 Mostra la lista dei tuoi {len(seguiti)} seguiti per trovare i profili bloccati"):
            df_seguiti = pd.DataFrame(sorted(seguiti), columns=["Username"])
            st.dataframe(df_seguiti, use_container_width=True)
    elif scarto < 0:
        st.info("Hai iniziato a seguire persone nuove dopo aver scaricato i dati.")
    else:
        st.success("I numeri combaciano alla perfezione!")

    st.divider()
    non_ricambiano = seguiti - follower
    lista_ordinata = sorted(non_ricambiano)
    
    if len(non_ricambiano) > 0:
        st.error(f"❌ {len(non_ricambiano)} persone che TU segui non ricambiano il follow:")
        for i, utente in enumerate(lista_ordinata, 1):
            st.text(f"{i}. {utente}")
    else:
        st.success("Tutti ricambiano il follow! 🎉")
