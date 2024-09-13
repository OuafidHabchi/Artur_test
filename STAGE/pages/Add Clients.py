import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["ARTUR"]
collection_name = "Clients"

# Fonction pour récupérer les colonnes de la base MongoDB sans la colonne "_id"
def get_mongo_fields():
    collection = db[collection_name]
    document = collection.find_one()
    if document:
        fields = list(document.keys())
        # Exclure le champ "_id"
        if '_id' in fields:
            fields.remove('_id')
        return fields
    return []


# Fonction pour ajouter des employés depuis un fichier CSV et faire correspondre les colonnes
def upload_csv_and_add_to_mongo():
    # Uploader un fichier CSV
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Vérifier si la collection MongoDB est vide
        mongo_fields = get_mongo_fields()
        if not mongo_fields:  # Si aucun champ MongoDB n'est trouvé, prendre les champs du CSV
            st.info("La collection MongoDB est vide. Sélectionnez les colonnes du CSV que vous souhaitez insérer.")
            available_fields = df.columns.tolist()

            # Afficher une liste multiselect pour permettre à l'utilisateur de choisir les champs à insérer
            selected_fields = st.multiselect("Sélectionnez les champs à insérer dans MongoDB", available_fields)

            if selected_fields:
                # Insérer les données dans MongoDB uniquement pour les champs sélectionnés
                if st.button("Insérer dans MongoDB"):
                    data_to_insert = []
                    for _, row in df[selected_fields].iterrows():
                        # Créer un dictionnaire avec les champs sélectionnés
                        filtered_row = {field: row[field] for field in selected_fields}
                        
                        # Ajouter la date d'insertion automatiquement (sans l'heure)
                        filtered_row["date_insertion"] = datetime.now().strftime("%Y-%m-%d")
                        
                        data_to_insert.append(filtered_row)

                    # Insérer les données dans MongoDB
                    collection = db[collection_name]
                    collection.insert_many(data_to_insert)

                    st.success(f"Données insérées avec succès dans la collection {collection_name} avec la date d'insertion.")
            else:
                st.warning("Veuillez sélectionner au moins un champ à insérer.")
        else:
            # Faire correspondre les colonnes CSV avec les champs MongoDB
            mapping = {}
            for mongo_field in mongo_fields:
                csv_col = st.selectbox(f"Choisir une colonne CSV pour le champ '{mongo_field}'", df.columns.tolist(), key=mongo_field)
                mapping[mongo_field] = csv_col

            # Insérer les données dans MongoDB
            if st.button("Insérer dans MongoDB"):
                # Construire un dictionnaire avec uniquement les colonnes sélectionnées qui existent dans MongoDB
                data_to_insert = []
                for _, row in df.iterrows():
                    # Créer un dictionnaire pour chaque ligne, seulement avec les colonnes mappées
                    filtered_row = {mongo_field: row[mapping[mongo_field]] for mongo_field in mapping}
                    
                    # Ajouter la date d'insertion automatiquement (sans l'heure)
                    filtered_row["date_insertion"] = datetime.now().strftime("%Y-%m-%d")
                    
                    data_to_insert.append(filtered_row)

                # Insérer les données dans MongoDB
                collection = db[collection_name]
                collection.insert_many(data_to_insert)

                st.success(f"Données insérées avec succès dans la collection {collection_name} avec la date d'insertion.")
            else:
                st.warning("Cliquez sur le bouton pour insérer les données.")


# Fonction pour ajouter un employé manuellement
def add_client_manually():
    st.subheader("Ajouter un employé manuellement")

    # Récupérer les champs MongoDB (sans "_id" et sans "date_insertion")
    mongo_fields = get_mongo_fields()
    if "date_insertion" in mongo_fields:
        mongo_fields.remove("date_insertion")

    if mongo_fields:
        # Créer un formulaire pour remplir les informations des employés
        employee_data = {}
        for mongo_field in mongo_fields:
            employee_data[mongo_field] = st.text_input(f"Entrer une valeur pour '{mongo_field}'")

        # Bouton pour soumettre les informations
        if st.button("Enregistrer dans MongoDB"):
            # Vérifier si toutes les valeurs sont remplies
            if all(employee_data.values()):
                # Ajouter la date d'insertion automatiquement (sans que l'utilisateur ne voie ce champ)
                employee_data["date_insertion"] = datetime.now().strftime("%Y-%m-%d")

                # Insérer les données dans MongoDB
                collection = db[collection_name]
                collection.insert_one(employee_data)
                st.success(f"Employé ajouté avec succès dans la collection {collection_name} avec la date d'insertion.")
            else:
                st.warning("Veuillez remplir tous les champs avant de soumettre.")
    else:
        st.warning("Aucun champ trouvé dans la collection MongoDB.")


# Interface principale
st.title("Ajouter des employés")

# Option pour ajouter via CSV ou manuellement
option = st.radio("Choisir une méthode pour ajouter des employés", ("Via CSV", "Manuellement"))

if option == "Via CSV":
    upload_csv_and_add_to_mongo()
else:
    add_client_manually()
