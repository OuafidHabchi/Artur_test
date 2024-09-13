import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import requests  # Pour envoyer la requête au webhook
import json
import math

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

# Fonction pour nettoyer les données avant l'envoi au webhook
def clean_data(data):
    def sanitize_value(value):
        if isinstance(value, float):
            if math.isinf(value) or math.isnan(value):
                return None  # Remplacer NaN ou Infinity par None
        return value
    
    if isinstance(data, list):
        return [{k: sanitize_value(v) for k, v in client.items()} for client in data]
    elif isinstance(data, dict):
        return {k: sanitize_value(v) for k, v in data.items()}
    return data

# Fonction pour envoyer les données au webhook
def send_to_webhook(clients, webhook_url):
    cleaned_clients = clean_data(clients)  # Nettoyer les données avant de les envoyer
    try:
        response = requests.post(webhook_url, json=cleaned_clients)  # Envoyer la liste des clients au webhook
        if response.status_code == 200:
            st.success(f"Liste des clients envoyée avec succès à {webhook_url}")
        else:
            st.error(f"Erreur lors de l'envoi au webhook : {response.status_code}")
    except Exception as e:
        st.error(f"Erreur lors de la requête webhook : {str(e)}")

# Interface principale pour l'automatisation
def automation_page():
    st.title("Automatisation des contacts")

    # Récupérer tous les clients depuis MongoDB
    clients = get_clients()

    # Extraire les mois disponibles à partir des dates d'insertion
    months = get_months_from_clients(clients)

    # Si des mois existent
    if months:
        # Afficher un selectbox pour choisir un mois
        selected_month = st.selectbox("Choisissez un mois", months)

        # Afficher un selectbox pour choisir le type de contact
        contact_method = st.selectbox("Choisissez un mode de contact", ["Email", "LinkedIn", "Email + LinkedIn"])

        # Définir les URLs des webhooks pour chaque type de contact
        webhook_urls = {
            "Email": "https://hooks.zapier.com/hooks/catch/19888094/2hf4v87/",  # Remplacer par l'URL du webhook Email
            "LinkedIn": "https://webhook.site/linkedin-webhook-url",  # Remplacer par l'URL du webhook LinkedIn
            "Email + LinkedIn": "https://webhook.site/email-linkedin-webhook-url"  # Remplacer par l'URL du webhook Email + LinkedIn
        }

        # Bouton pour lancer l'automatisation
        if st.button("Automatiser"):
            filtered_clients = filter_clients_by_month(clients, selected_month)
            if filtered_clients:
                # Envoyer la liste des clients au webhook correspondant
                webhook_url = webhook_urls[contact_method]
                send_to_webhook(filtered_clients, webhook_url)
            else:
                st.warning(f"Aucun client trouvé pour {selected_month}.")
    else:
        st.warning("Aucun client trouvé dans la base de données.")

# Appel de la page principale
automation_page()
