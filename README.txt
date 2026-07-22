============================================================
  Générateur de Documentation ABAP
  Guide d'installation et d'utilisation
============================================================

PRÉREQUIS
---------
Cette application utilise un modèle d'IA local (Ollama)
pour générer la documentation ABAP. Vous devez installer
Ollama une seule fois avant de lancer l'application.


ÉTAPE 1 — Installer Ollama
---------------------------
Téléchargez et installez Ollama depuis :
  https://ollama.com/download

Lancez l'installateur et suivez les instructions à l'écran.
Ollama démarrera automatiquement en tant que service
en arrière-plan après l'installation.


ÉTAPE 2 — Télécharger le modèle IA (une seule fois, ~4 Go)
------------------------------------------------------------
Ouvrez un terminal (Invite de commandes ou PowerShell)
et exécutez :

  ollama pull mistral:7b-instruct

Attendez la fin du téléchargement. Cette étape est unique.
Vous n'aurez pas à la répéter lors des prochains lancements.


ÉTAPE 3 — Construire l'application (première fois uniquement)
--------------------------------------------------------------
Si vous avez cloné ce projet depuis GitHub et que vous
n'avez pas encore le fichier ABAPDocGenerator.exe,
vous devez d'abord construire l'application :

  1. Assurez-vous que Python et le .venv sont configurés :
       python -m venv .venv
       .venv\Scripts\activate
       pip install -r requirements.txt

  2. Double-cliquez sur build.bat  (ou lancez-le dans un terminal)

  Le script de construction va :
    - Installer PyInstaller et Pillow automatiquement
    - Convertir le logo en icône
    - Tout regrouper dans le dossier dist\ABAPDocGenerator\
    - Copier tous les fichiers de données nécessaires

  Cette opération prend 5 à 15 minutes selon votre machine.
  Vous n'avez besoin de le faire QU'UNE SEULE FOIS
  (ou après une modification du code source).


ÉTAPE 4 — Lancer l'application
--------------------------------
Double-cliquez sur :  dist\ABAPDocGenerator\ABAPDocGenerator.exe

L'application va :
  1. Vérifier qu'Ollama est en cours d'exécution
  2. Vérifier que le modèle IA est disponible
  3. Démarrer le serveur web local
  4. Ouvrir votre navigateur automatiquement sur http://localhost:8503

Si le navigateur ne s'ouvre pas automatiquement, accédez à :
  http://localhost:8503


RÉSOLUTION DES PROBLÈMES
-------------------------

Problème : "OLLAMA IS NOT RUNNING"
  Solution : Assurez-vous qu'Ollama est installé et en cours
  d'exécution. Ouvrez un terminal et exécutez : ollama serve
  Ou redémarrez l'application de bureau Ollama.

Problème : "MODEL NOT FOUND: mistral:7b-instruct"
  Solution : Ouvrez un terminal et exécutez :
  ollama pull mistral:7b-instruct

Problème : L'application s'ouvre mais l'IA ne génère rien
  Solution : Assurez-vous qu'Ollama n'est pas surchargé.
  Essayez de le redémarrer : ouvrez un terminal et exécutez :
  ollama serve

Problème : Le port 8503 est déjà utilisé
  Solution : Fermez toute autre instance de l'application
  en cours d'exécution, ou redémarrez votre ordinateur.

Problème : build.bat échoue
  Solution : Assurez-vous que le .venv existe et est activé.
  Exécutez : python -m venv .venv && .venv\Scripts\activate
  Puis relancez build.bat.


CONFIGURATION REQUISE
----------------------
  - Windows 10 ou Windows 11 (64 bits)
  - Au moins 8 Go de RAM (16 Go recommandés pour mistral:7b-instruct)
  - Au moins 10 Go d'espace disque libre (Ollama + modèle + build)
  - Python 3.10 ou supérieur (uniquement pour l'étape de build)
  - Ollama installé : https://ollama.com/download


REMARQUES
---------
  - L'application fonctionne entièrement en local. Aucune
    connexion Internet n'est requise après l'installation
    (sauf pour le téléchargement initial du modèle).
  - Vos fichiers ABAP ne sont jamais envoyés à un serveur
    externe.
  - Le dossier chroma_db stocke les embeddings de vos
    documents. Ne le supprimez pas sauf si vous souhaitez
    réinitialiser la base de connaissances.
  - Le dossier dist\ n'est PAS inclus dans le dépôt GitHub
    (trop volumineux). Utilisez toujours build.bat pour
    construire l'application localement.

============================================================
