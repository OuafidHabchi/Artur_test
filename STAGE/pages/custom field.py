import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["ARTUR"]

# Fonction pour récupérer les noms des collections disponibles dans la base de données
def get_collection_names():
    return db.list_collection_names()

# Fonction pour récupérer les champs d'une collection MongoDB en excluant "date_insertion"
def get_collection_fields(collection_name):
    collection = db[collection_name]
    document = collection.find_one()  # Obtenir un document pour récupérer les champs
    if document:
        fields = list(document.keys())
        if "date_insertion" in fields:
            fields.remove("date_insertion")  # Exclure "date_insertion"
        return fields
    return []

# Fonction pour ajouter une colonne personnalisée à une collection
def add_custom_column(collection_name, column_name, column_type):
    collection = db[collection_name]

    # Définir la valeur par défaut en fonction du type choisi
    if column_type == "String":
        default_value = ""
    elif column_type == "Number":
        default_value = 0
    elif column_type == "Boolean":
        default_value = False
    elif column_type == "Date":
        default_value = datetime.now().strftime("%Y-%m-%d")
    elif column_type == "Array":
        default_value = []
    else:
        default_value = None

    # Mettre à jour tous les documents de la collection avec la nouvelle colonne et sa valeur par défaut
    collection.update_many({}, {"$set": {column_name: default_value}})

    st.success(f"La colonne '{column_name}' de type '{column_type}' a été ajoutée à la collection '{collection_name}'.")

# Fonction pour supprimer une colonne d'une collection
def delete_custom_column(collection_name, column_name):
    collection = db[collection_name]

    # Utiliser $unset pour supprimer un champ
    collection.update_many({}, {"$unset": {column_name: ""}})
    
    st.success(f"La colonne '{column_name}' a été supprimée de la collection '{collection_name}'.")

# Interface principale pour ajouter ou supprimer une colonne
def custom_field_page():
    st.title("Gérer les colonnes personnalisées")

    # Choisir l'action: Ajouter ou Supprimer une colonne
    action = st.radio("Choisissez une action", ["Ajouter une colonne", "Supprimer une colonne"])

    # Si l'utilisateur choisit d'ajouter une colonne
    if action == "Ajouter une colonne":
        # Étape 1: Sélectionner une collection existante
        collections = get_collection_names()
        if collections:
            selected_collection = st.selectbox("Choisissez une collection", collections)

            # Étape 2: Entrer le nom de la nouvelle colonne
            column_name = st.text_input("Nom de la nouvelle colonne")

            # Étape 3: Choisir le type de la nouvelle colonne
            column_type = st.selectbox("Choisissez un type pour la nouvelle colonne", ["String", "Number", "Boolean", "Date", "Array"])

            # Bouton pour ajouter la colonne
            if st.button("Ajouter la colonne"):
                if column_name and column_type:
                    add_custom_column(selected_collection, column_name, column_type)
                else:
                    st.warning("Veuillez entrer un nom de colonne et choisir un type.")
        else:
            st.warning("Aucune collection trouvée dans la base de données.")

    # Si l'utilisateur choisit de supprimer une colonne
    elif action == "Supprimer une colonne":
        # Étape 1: Sélectionner une collection existante
        collections = get_collection_names()
        if collections:
            selected_collection = st.selectbox("Choisissez une collection", collections)

            # Étape 2: Sélectionner un champ à supprimer en excluant "date_insertion"
            fields = get_collection_fields(selected_collection)
            if fields:
                selected_field = st.selectbox("Choisissez une colonne à supprimer", fields)

                # Bouton pour supprimer la colonne
                if st.button("Supprimer la colonne"):
                    if selected_field:
                        delete_custom_column(selected_collection, selected_field)
                    else:
                        st.warning("Veuillez sélectionner une colonne à supprimer.")
            else:
                st.warning(f"Aucune colonne trouvée dans la collection '{selected_collection}'.")
        else:
            st.warning("Aucune collection trouvée dans la base de données.")

# Appel de la page principale
custom_field_page()
