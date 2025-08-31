# 🤖 Chatbot d'Analyse du Stress Étudiant
=> llm_with_langchain.py

Ce projet est un **chatbot conversationnel** propulsé par le modèle de langage **Gemini 1.5 Flash**. Il est conçu pour interagir avec l'utilisateur tout en s'appuyant sur des données relatives au stress des étudiants. L'interface utilisateur est construite avec **Streamlit**, ce qui le rend accessible et facile à utiliser.

## ✨ Fonctionnalités

- **Chatbot intelligent** : Utilise **Google Gemini 1.5 Flash** pour des réponses pertinentes et naturelles.
- **Mémoire de conversation** : Le chatbot se souvient des échanges précédents grâce à la gestion de la mémoire de **LangChain**, permettant des conversations fluides et contextuelles.
- **Analyse de données** : Le modèle prend en compte deux jeux de données (`Student Stress Monitoring Datasets`) pour répondre aux questions spécifiques sur le stress des étudiants.
- **Interface utilisateur simple** : L'application est présentée sous forme d'une interface web interactive développée avec **Streamlit**.
- **Gestion des dépendances** : Le fichier `requirements.txt` liste toutes les bibliothèques nécessaires pour garantir un environnement d'exécution stable.

## 🛠️ Technologies et Bibliothèques

- **Python** : Le langage de programmation principal.
- **Google Gemini 1.5 Flash** : Le modèle de langage utilisé pour les conversations.
- **LangChain** : Un framework puissant pour la création d'applications basées sur les LLM. Il gère notamment la mémoire de la conversation et les chaînes de traitement.
- **Streamlit** : Le framework pour la création de l'interface utilisateur web.
- **Pandas** : Utilisé pour manipuler et lire les fichiers de données CSV.
- **`langchain-google-genai`** : La bibliothèque spécifique pour l'intégration de Gemini avec LangChain.
- **`docarray`** : Pour la création de la base de données vectorielle en mémoire.

## 🚀 Installation et Lancement

Pour lancer l'application sur votre machine locale, suivez ces étapes :

1.  **Clonez le dépôt Git** (si nécessaire).

2.  **Installez les dépendances** :
    Exécutez la commande suivante pour installer toutes les bibliothèques nécessaires :

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurez votre clé d'API** :
    Le chatbot nécessite une clé d'API Google Gemini. Vous devez la configurer en tant que secret Streamlit.

    -   Créez un dossier `.streamlit` à la racine de votre projet.
    -   À l'intérieur de ce dossier, créez un fichier `secrets.toml`.
    -   Ajoutez votre clé d'API dans ce fichier sous la forme suivante :

    ```toml
    GEMINI_API_KEY="votre_clé_api"
    ```

    > **Note** : Remplacez `"votre_clé_api"` par votre véritable clé.

4.  **Lancez l'application** :
    Depuis le terminal, exécutez le script principal avec Streamlit :

    ```bash
    streamlit run votre_fichier.py
    ```

    > **Note** : Remplacez `votre_fichier.py` par le nom de votre fichier Python principal.

L'application s'ouvrira automatiquement dans votre navigateur web. Vous pouvez alors commencer à interagir avec le chatbot.