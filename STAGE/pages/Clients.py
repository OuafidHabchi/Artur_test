import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime import datetime

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["ARTUR"]
collection_name = "Clients"

# Fonction pour récupérer les clients depuis MongoDB
def get_clients():
    collection = db[collection_name]
    clients = list(collection.find({}, {"_id": 0}))  # Exclure l'_id pour simplifier l'affichage
    return clients

# Fonction pour extraire les mois et années uniques à partir des dates d'insertion
def get_months_from_clients(clients):
    months = []
    for client in clients:
        if "date_insertion" in client:
            # Extraire le mois et l'année de la date d'insertion
            date_obj = datetime.strptime(client["date_insertion"], "%Y-%m-%d")
            month_year = date_obj.strftime("%B-%Y")  # Exemple : "Août-2024"
            if month_year not in months:
                months.append(month_year)
    return sorted(months, reverse=True)  # Trier par date, du plus récent au plus ancien

# Fonction pour filtrer les clients par mois
def filter_clients_by_month(clients, selected_month):
    filtered_clients = []
    for client in clients:
        if "date_insertion" in client:
            date_obj = datetime.strptime(client["date_insertion"], "%Y-%m-%d")
            month_year = date_obj.strftime("%B-%Y")
            if month_year == selected_month:
                filtered_clients.append(client)
    return filtered_clients

# Interface principale
def display_clients_by_month():
    st.title("Visualiser les clients par mois d'insertion")

    # Récupérer tous les clients depuis MongoDB
    clients = get_clients()

    # Extraire les mois disponibles à partir des dates d'insertion
    months = get_months_from_clients(clients)

    # Si des mois existent
    if months:
        # Afficher un selectbox pour choisir un mois
        selected_month = st.selectbox("Choisissez un mois", months)

        # Afficher les clients du mois sélectionné
        if selected_month:
            filtered_clients = filter_clients_by_month(clients, selected_month)
            if filtered_clients:
                st.subheader(f"Clients insérés en {selected_month} :")
                df = pd.DataFrame(filtered_clients)
                st.dataframe(df)  # Afficher les clients sous forme de tableau
            else:
                st.warning(f"Aucun client trouvé pour {selected_month}.")
    else:
        st.warning("Aucun client trouvé dans la base de données.")

# Appel de la fonction principale
display_clients_by_month()
