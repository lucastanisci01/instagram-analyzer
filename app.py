import json
import streamlit as st
import pandas as pd

# --- INTERFACCIA GRAFICA STREAMLIT ---
st.set_page_config(page_title="Chi non mi segue?", page_icon="🕵️", layout="centered")

st.title("🕵️ Analisi Instagram")
st.markdown("Scopri chi non ricambia il follow. Dati estratti in modo chirurgico.")

col1, col2 = st.columns(2)
with col1:
    file_seguiti = st.file_uploader("📂 Carica following.json", type=['json'])
with col2:
    file_follower = st.file_uploader("📂 Carica followers_1.json", type=['json'])

if file_seguiti is not None and file_follower is not None:
    dati_seguiti = json.load(file_seguiti)
    dati_follower = json.load(file_follower)

    seguiti = set()
    follower = set()

    # 1. ESTRAZIONE SEGUITI (Mirata alla chiave 'title')
    if isinstance(dati_seguiti, dict) and 'relationships_following' in dati_seguiti:
        for item in dati_seguiti['relationships_following']:
            if 'title' in item:
                nome = item['title'].strip()
                # Filtro: Ignora stringhe vuote e account eliminati
                if nome != "" and "deleted" not in nome.lower():
                    seguiti.add(nome)

    # 2. ESTRAZIONE FOLLOWER (Mirata alla chiave 'value')
    if isinstance(dati_follower, list):
        for item in dati_follower:
            if 'string_list_data' in item and len(item['string_list_data']) > 0:
                dati_stringa = item['string_list_data'][0]
                if 'value' in dati_stringa:
                    nome = dati_stringa['value'].strip()
                    if nome != "" and "deleted" not in nome.lower():
                        follower.add(nome)

    # --- DASHBOARD STATISTICHE ---
    st.divider()
    st.subheader("📊 Statistiche Pulite")
    m1, m2 = st.columns(2)
    m1.metric(label="Tu segui", value=len(seguiti))
    m2.metric(label="Ti seguono", value=len(follower))

    # --- RICERCA FANTASMI ---
    st.markdown("### 👻 Controllo account sospesi")
    numero_app = st.number_input("Seguiti sulla tua app di Instagram:", min_value=0, value=394)
    scarto = len(seguiti) - numero_app

    if scarto > 0:
        st.warning(
            f"Nel file ci sono **{scarto} account in più** rispetto all'app. Sono quasi sicuramente account disabilitati/bloccati da Instagram che non hanno il tag 'deleted'.")
        with st.expander(f"🔍 Mostra la lista dei tuoi {len(seguiti)} seguiti per trovare i profili bloccati"):
            df_seguiti = pd.DataFrame(sorted(seguiti), columns=["Username (Cerca nomi strani o 'instagrammer')"])
            st.dataframe(df_seguiti, use_container_width=True)
    elif scarto < 0:
        st.info("Hai iniziato a seguire persone nuove dopo aver scaricato i dati.")
    else:
        st.success("I numeri combaciano alla perfezione!")

    # --- IL CALCOLO FINALE ---
    st.divider()
    non_ricambiano = seguiti - follower
    lista_ordinata = sorted(non_ricambiano)

    if len(non_ricambiano) > 0:
        st.error(f"❌ {len(non_ricambiano)} persone che TU segui non ricambiano il follow:")
        for i, utente in enumerate(lista_ordinata, 1):
            st.text(f"{i}. {utente}")
    else:
        st.success("Tutti ricambiano il follow! 🎉")