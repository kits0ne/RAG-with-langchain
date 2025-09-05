import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import pandas as pd
import json
from datetime import datetime

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Agent Pédagogique - Données Réelles")
st.title("🎓 Agent Pédagogique Intelligent")
st.subheader("Basé sur des données réelles de Kaggle Learn, Python Documentation et exercices pratiques")

# =============================================================================
# CHARGEMENT DES DONNÉES RÉELLES
# =============================================================================

@st.cache_data
def load_real_data():
    """Charge les données réelles collectées"""
    try:
        # Charger les formations
        if os.path.exists('formations_reelles.csv'):
            formations_df = pd.read_csv('formations_reelles.csv')
            st.success("✅ Formations réelles chargées depuis formations_reelles.csv")
        else:
            st.warning("⚠️ Fichier formations_reelles.csv non trouvé. Exécutez d'abord le script de collecte.")
            return create_sample_data()
        
        # Charger les modules
        if os.path.exists('modules_reels.csv'):
            modules_df = pd.read_csv('modules_reels.csv')
            st.success("✅ Modules réels chargés depuis modules_reels.csv")
        else:
            st.warning("⚠️ Fichier modules_reels.csv non trouvé.")
            modules_df = pd.DataFrame()
        
        # Charger les exercices
        if os.path.exists('exercices_reels.json'):
            with open('exercices_reels.json', 'r', encoding='utf-8') as f:
                exercises_data = json.load(f)
            st.success("✅ Exercices réels chargés depuis exercices_reels.json")
        else:
            st.warning("⚠️ Fichier exercices_reels.json non trouvé.")
            exercises_data = []
        
        return formations_df, modules_df, exercises_data
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {e}")
        return create_sample_data()

def create_sample_data():
    """Crée des données d'exemple si les fichiers réels ne sont pas disponibles"""
    st.info("📝 Utilisation de données d'exemple. Pour utiliser les vraies données, exécutez le script de collecte.")
    
    sample_formations = pd.DataFrame([
        {'formation_id': 1, 'titre': 'Python Basics', 'domaine': 'Programming', 'niveau': 'Beginner', 
         'duree_heures': 8, 'prerequis': 'None', 'source': 'Sample Data'},
        {'formation_id': 2, 'titre': 'Pandas Data Analysis', 'domaine': 'Data Science', 'niveau': 'Intermediate', 
         'duree_heures': 6, 'prerequis': 'Python', 'source': 'Sample Data'},
    ])
    
    sample_modules = pd.DataFrame([
        {'module_id': 1, 'formation_id': 1, 'ordre': 1, 'titre': 'Variables and Types', 
         'duree_minutes': 60, 'concepts_cles': 'int, float, string, boolean'},
        {'module_id': 2, 'formation_id': 2, 'ordre': 1, 'titre': 'DataFrame Basics', 
         'duree_minutes': 90, 'concepts_cles': 'read_csv, head, info, describe'},
    ])
    
    sample_exercises = [
        {'category': 'Python Basics', 'level': 'Beginner', 'exercises': [
            {'title': 'Hello World', 'description': 'Create a program that prints Hello World'}
        ]}
    ]
    
    return sample_formations, sample_modules, sample_exercises

# =============================================================================
# CHARGEMENT ET AFFICHAGE DES DONNÉES
# =============================================================================

# Charger les données
formations_df, modules_df, exercises_data = load_real_data()

# Initialisation session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = StreamlitChatMessageHistory()
if "generated_courses" not in st.session_state:
    st.session_state.generated_courses = []

# Configuration API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("❌ Erreur: Clé 'GEMINI_API_KEY' manquante dans les secrets Streamlit.")
    st.stop()

# =============================================================================
# INTERFACE UTILISATEUR
# =============================================================================

col1, col2 = st.columns([2, 1])

with col1:
    st.write("### 💬 Générateur de contenu pédagogique")
    
    # Options de génération
    generation_type = st.selectbox(
        "Type de contenu à générer:",
        ["Cours complet", "Module spécifique", "Quiz interactif", "Exercices pratiques", "Plan de formation personnalisé"]
    )
    
    # Filtres basés sur les vraies données
    domaines_disponibles = formations_df['domaine'].unique().tolist() if not formations_df.empty else ['Programming']
    niveaux_disponibles = formations_df['niveau'].unique().tolist() if not formations_df.empty else ['Beginner']
    
    with st.expander("⚙️ Paramètres de génération"):
        col_a, col_b = st.columns(2)
        with col_a:
            domaine = st.selectbox("Domaine:", domaines_disponibles)
            niveau = st.selectbox("Niveau:", niveaux_disponibles)
        with col_b:
            duree = st.slider("Durée souhaitée (heures):", 1, 20, 6)
            format_sortie = st.selectbox("Format:", ["Texte structuré", "JSON", "Markdown"])

with col2:
    st.write("### 📊 Base de données réelle")
    
    # Statistiques des données
    if not formations_df.empty:
        st.metric("Formations disponibles", len(formations_df))
        st.metric("Modules documentés", len(modules_df) if not modules_df.empty else 0)
        st.metric("Sources de données", len(formations_df['source'].unique()) if 'source' in formations_df.columns else 1)
        
        # Répartition par source
        if 'source' in formations_df.columns:
            st.write("**Répartition par source:**")
            source_counts = formations_df['source'].value_counts()
            for source, count in source_counts.items():
                st.write(f"• {source}: {count}")
        
        # Aperçu des formations
        st.write("**Formations disponibles:**")
        display_cols = ['titre', 'niveau', 'duree_heures']
        if 'source' in formations_df.columns:
            display_cols.append('source')
        st.dataframe(formations_df[display_cols].head(8), use_container_width=True)
    else:
        st.warning("Aucune formation chargée")

# =============================================================================
# TEMPLATE POUR L'AGENT AVEC VRAIES DONNÉES
# =============================================================================

pedagogical_template_real = """
Tu es un expert pédagogique qui génère des contenus de formation de haute qualité à partir de tes données.

DONNÉES RÉELLES DISPONIBLES:
=== FORMATIONS ===
{formations_data}

=== MODULES DÉTAILLÉS ===
{modules_data}

=== EXERCICES PRATIQUES ===
{exercises_data}

PARAMÈTRES DE GÉNÉRATION:
- Type de contenu: {generation_type}
- Domaine: {domaine}
- Niveau: {niveau}
- Durée: {duree}h
- Format: {format_sortie}

HISTORIQUE: {chat_history}

DEMANDE UTILISATEUR: {user_input}

INSTRUCTIONS SPÉCIALES:
1. Utilise tes données pour générer un contenu pédagogique précis et structuré.
2. Cite les sources exactes (Kaggle Learn, Python Documentation, etc.)
3. Intègre les exercices et exemples de code fournis
4. Respecte les durées réelles des modules
5. Mentionne les prérequis exacts des formations réelles
6. Si tu génères un cours, base-toi sur les vrais modules de la base de données

Si tu génères un COURS COMPLET, structure ainsi:
# titre du cours basé sur les vraies données

## 📋 Source et informations
- **Source**: [Source exacte des données]
- **Durée réelle**: durée basée sur les vraies données
- **Niveau**: niveau des vraies données
- **Prérequis**: prérequis réels

## 🎯 Objectifs
objectifs tirés des données réelles

## 📚 Programme
utilise les vrais modules avec leurs durées et concepts exacts

## 💻 Exercices pratiques
utilise les vrais exercices collectés

## 🔗 Références
- Basé sur les données de: sources utilisées

GÉNÈRE LE CONTENU:
"""

# =============================================================================
# INITIALISATION LLM
# =============================================================================

if "llm_chain_real" not in st.session_state:
    memory = ConversationBufferMemory(
        chat_memory=st.session_state.chat_history,
        memory_key="chat_history",
        input_key="user_input"
    )
    
    prompt_template = ChatPromptTemplate.from_template(pedagogical_template_real)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", 
        google_api_key=api_key, 
        temperature=0.2  # Moins créatif, plus factuel
    )
    
    st.session_state.llm_chain_real = LLMChain(
        prompt=prompt_template,
        llm=llm,
        memory=memory
    )

# =============================================================================
# INTERFACE DE GÉNÉRATION
# =============================================================================

user_input = st.text_area(
    "Décrivez le contenu pédagogique souhaité:", 
    placeholder="Ex: Crée un cours complet sur Python basé sur les données Kaggle Learn",
    height=100
)

# Boutons d'exemples avec vraies données
st.write("### 💡 Exemples basés sur les vraies données")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📚 Cours Python Kaggle"):
        st.session_state.example_query = "Génère un cours complet sur Python basé sur les données Kaggle Learn avec tous les modules réels et exercices"

with col2:
    if st.button("📊 Formation Pandas"):
        st.session_state.example_query = "Crée une formation Pandas en utilisant les vrais modules et exercices de la base de données"

with col3:
    if st.button("❓ Quiz ML réel"):
        st.session_state.example_query = "Génère un quiz sur Machine Learning basé sur les vraies leçons Kaggle collectées"

# Afficher l'exemple sélectionné
if "example_query" in st.session_state:
    user_input = st.text_area("Exemple sélectionné:", value=st.session_state.example_query, height=80, key="example_display")

# =============================================================================
# GÉNÉRATION DE CONTENU
# =============================================================================

if st.button("🚀 Générer le contenu avec les vraies données", type="primary"):
    if user_input:
        with st.spinner("🤖 Génération basée sur les données réelles collectées..."):
            try:
                # Préparer le contexte avec les vraies données
                formations_context = formations_df.to_string(index=False) if not formations_df.empty else "Aucune formation chargée"
                modules_context = modules_df.to_string(index=False) if not modules_df.empty else "Aucun module chargé"
                exercises_context = json.dumps(exercises_data, ensure_ascii=False, indent=2) if exercises_data else "Aucun exercice chargé"
                
                # Filtrer les données selon les paramètres
                filtered_formations = formations_df
                if domaine and domaine in formations_df['domaine'].values:
                    filtered_formations = formations_df[formations_df['domaine'] == domaine]
                if niveau and niveau in formations_df['niveau'].values:
                    filtered_formations = filtered_formations[filtered_formations['niveau'] == niveau]
                
                # Générer la réponse avec les vraies données
                response = st.session_state.llm_chain_real.invoke({
                    "formations_data": filtered_formations.to_string(index=False),
                    "modules_data": modules_context,
                    "exercises_data": exercises_context,
                    "generation_type": generation_type,
                    "domaine": domaine,
                    "niveau": niveau,
                    "duree": duree,
                    "format_sortie": format_sortie,
                    "user_input": user_input
                })
                
                # Afficher la réponse
                st.write("### 📝 Contenu généré à partir des données réelles:")
                st.write(response["text"])
                
                # Informations sur les sources utilisées
                with st.expander("🔍 Sources de données utilisées"):
                    if not filtered_formations.empty and 'source' in filtered_formations.columns:
                        sources_used = filtered_formations['source'].unique()
                        st.write("**Sources réelles utilisées pour cette génération :**")
                        for source in sources_used:
                            count = len(filtered_formations[filtered_formations['source'] == source])
                            st.write(f"• **{source}**: {count} formation(s)")
                    
                    st.write("**Statistiques de génération :**")
                    st.write(f"• Formations filtrées: {len(filtered_formations)}")
                    st.write(f"• Modules disponibles: {len(modules_df) if not modules_df.empty else 0}")
                    st.write(f"• Exercices disponibles: {len(exercises_data)}")
                
                # Sauvegarder le cours généré
                course_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "type": generation_type,
                    "domaine": domaine,
                    "niveau": niveau,
                    "duree": duree,
                    "demande": user_input,
                    "contenu": response["text"],
                    "sources_utilisees": filtered_formations['source'].unique().tolist() if not filtered_formations.empty and 'source' in filtered_formations.columns else [],
                    "nb_formations_source": len(filtered_formations)
                }
                st.session_state.generated_courses.append(course_data)
                
                # Bouton de téléchargement
                filename = f"cours_reel_{datetime.now().strftime('%Y%m%d_%H%M')}"
                if format_sortie == "Markdown":
                    st.download_button(
                        "📥 Télécharger (MD)",
                        response["text"],
                        file_name=f"{filename}.md",
                        mime="text/markdown"
                    )
                elif format_sortie == "JSON":
                    st.download_button(
                        "📥 Télécharger (JSON)",
                        json.dumps(course_data, ensure_ascii=False, indent=2),
                        file_name=f"{filename}.json",
                        mime="application/json"
                    )
                
                st.success("✅ Contenu généré avec succès à partir des données réelles !")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
                st.write("**Détails de l'erreur pour debugging:**")
                st.write(f"Formations disponibles: {len(formations_df) if not formations_df.empty else 0}")
                st.write(f"Modules disponibles: {len(modules_df) if not modules_df.empty else 0}")
    else:
        st.warning("⚠️ Veuillez saisir une demande")

# =============================================================================
# DASHBOARD DES DONNÉES RÉELLES
# =============================================================================

st.write("---")
st.write("## 📊 Dashboard des données réelles collectées")

tab1, tab2, tab3 = st.tabs(["📚 Formations", "📝 Modules", "💪 Exercices"])

with tab1:
    if not formations_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Répartition par niveau")
            if 'niveau' in formations_df.columns:
                niveau_counts = formations_df['niveau'].value_counts()
                st.bar_chart(niveau_counts)
        
        with col2:
            st.write("### Répartition par domaine")
            if 'domaine' in formations_df.columns:
                domaine_counts = formations_df['domaine'].value_counts()
                st.bar_chart(domaine_counts)
        
        st.write("### Tableau détaillé des formations")
        st.dataframe(formations_df, use_container_width=True)
    else:
        st.warning("⚠️ Aucune donnée de formation disponible")

with tab2:
    if not modules_df.empty:
        st.write("### Modules par formation")
        if 'formation_id' in modules_df.columns:
            modules_per_formation = modules_df['formation_id'].value_counts().sort_index()
            st.bar_chart(modules_per_formation)
        
        st.write("### Durée moyenne des modules")
        if 'duree_minutes' in modules_df.columns:
            avg_duration = modules_df['duree_minutes'].mean()
            st.metric("Durée moyenne", f"{avg_duration:.0f} minutes")
        
        st.write("### Tableau des modules")
        display_modules = modules_df[['titre', 'duree_minutes', 'concepts_cles']].head(20) if len(modules_df.columns) > 3 else modules_df.head(20)
        st.dataframe(display_modules, use_container_width=True)
    else:
        st.warning("⚠️ Aucune donnée de module disponible")

with tab3:
    if exercises_data:
        st.write("### Exercices par catégorie")
        for category_data in exercises_data:
            with st.expander(f"📁 {category_data['category']} - {category_data['level']}"):
                st.write(f"**Nombre d'exercices:** {len(category_data['exercises'])}")
                for i, exercise in enumerate(category_data['exercises'][:3]):  # Afficher les 3 premiers
                    st.write(f"**{i+1}. {exercise['title']}**")
                    st.write(f"Description: {exercise['description']}")
                    if len(category_data['exercises']) > 3:
                        st.write(f"... et {len(category_data['exercises']) - 3} autres exercices")
    else:
        st.warning("⚠️ Aucun exercice disponible")

# =============================================================================
# HISTORIQUE DES GÉNÉRATIONS
# =============================================================================

if st.session_state.generated_courses:
    st.write("---")
    st.write("### 📚 Historique des contenus générés (avec sources réelles)")
    
    for i, course in enumerate(reversed(st.session_state.generated_courses[-5:])):  # 5 derniers
        with st.expander(f"🎯 {course['type']} - {course['timestamp']} (Sources: {', '.join(course.get('sources_utilisees', ['N/A']))})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Domaine:** {course.get('domaine', 'N/A')}")
                st.write(f"**Niveau:** {course.get('niveau', 'N/A')}")
                st.write(f"**Durée:** {course.get('duree', 'N/A')}h")
            
            with col2:
                st.write(f"**Sources utilisées:** {', '.join(course.get('sources_utilisees', ['N/A']))}")
                st.write(f"**Nb formations source:** {course.get('nb_formations_source', 0)}")
            
            st.write(f"**Demande:** {course['demande']}")
            st.write("**Aperçu du contenu généré:**")
            preview = course['contenu'][:500] + "..." if len(course['contenu']) > 500 else course['contenu']
            st.text(preview)

# =============================================================================
# INSTRUCTIONS POUR RÉCUPÉRER LES DONNÉES
# =============================================================================

with st.sidebar:
    st.write("### 📋 Instructions")
    
    if formations_df.empty or len(formations_df) < 5:  # Si peu de données
        st.warning("⚠️ Données limitées détectées")
        st.write("""
        **Pour récupérer les vraies données :**
        
        1. **Créez le fichier `collecte_donnees.py`** avec le script fourni
        
        2. **Exécutez la collecte :**
        ```bash
        python collecte_donnees.py
        ```
        
        3. **Redémarrez l'application :**
        ```bash
        streamlit run agent_pedagogique.py
        ```
        
        **Sources récupérées :**
        • Kaggle Learn (Python, Pandas, ML, SQL)
        • Documentation Python officielle  
        • Exercices pratiques structurés
        """)
    else:
        st.success("✅ Données réelles chargées")
        st.write(f"**{len(formations_df)}** formations disponibles")
        st.write("**Sources actives :**")
        if 'source' in formations_df.columns:
            for source in formations_df['source'].unique():
                st.write(f"• {source}")

    st.write("---")
    st.write("### 📈 Statistiques")
    st.metric("Contenus générés", len(st.session_state.generated_courses))
    if not formations_df.empty:
        st.metric("Formations disponibles", len(formations_df))
        if 'duree_heures' in formations_df.columns:
            total_hours = formations_df['duree_heures'].sum()
            st.metric("Heures de formation", f"{total_hours}h")

# Footer
st.write("---")
st.write("🤖 **Agent Pédagogique avec Données Réelles** - Basé sur Kaggle Learn, Python Documentation, et exercices pratiques")
st.write("💡 *Génération automatisée de contenus pédagogiques à partir de sources authentiques et vérifiées*")