# 🌺 Méli-Mélo 973 — Synchronisation automatique Blogger → Netlify

Ce projet synchronise automatiquement vos poèmes de **melimelo973.blogspot.com**
vers un site Hugo hébergé sur **Netlify**, via **GitHub Actions**.

**Fréquence :** chaque nuit à minuit (heure de la Martinique), et à la demande.

---

## 🗺️ Vue d'ensemble

```
Blogger  ──(API)──▶  GitHub Actions  ──(Hugo)──▶  Netlify
  Blog                 (chaque nuit)               Site web
```

---

## 🛠️ Installation (une seule fois)

### Étape 1 — Installer les outils sur Windows

1. **Git** : https://git-scm.com/download/win  
   Installez avec toutes les options par défaut.

2. **Python 3** : https://www.python.org/downloads/  
   ⚠️ Cochez "Add Python to PATH" lors de l'installation.

3. **Hugo** : https://gohugo.io/installation/windows/  
   La méthode la plus simple : `winget install Hugo.Hugo.Extended`  
   (dans PowerShell ou l'invite de commandes)

---

### Étape 2 — Créer un compte GitHub

1. Allez sur https://github.com et créez un compte (gratuit)
2. Cliquez sur **"New repository"**
3. Nommez-le `melimelo973-site`
4. Choisissez **Public** (requis pour GitHub Actions gratuit)
5. Cliquez **"Create repository"**

---

### Étape 3 — Mettre le projet sur GitHub

Ouvrez PowerShell dans le dossier `poemes-auto/` et tapez :

```powershell
git init
git add .
git commit -m "Premier commit"
git branch -M main
git remote add origin https://github.com/VOTRE_PSEUDO/melimelo973-site.git
git push -u origin main
```

Remplacez `VOTRE_PSEUDO` par votre pseudo GitHub.

---

### Étape 4 — Créer le site sur Netlify

1. Allez sur https://app.netlify.com et connectez-vous avec Google
2. Cliquez **"Add new site"** → **"Import an existing project"**
3. Choisissez **GitHub** → autorisez l'accès → sélectionnez `melimelo973-site`
4. Laissez les paramètres par défaut (le fichier `netlify.toml` s'en occupe)
5. Cliquez **"Deploy site"**
6. **Copiez le "Site ID"** affiché dans *Site configuration > General*

---

### Étape 5 — Créer un token Netlify

1. Sur Netlify : cliquez sur votre avatar (en haut à droite) → **"User settings"**
2. Allez dans **"Applications"** → **"Personal access tokens"**
3. Cliquez **"New access token"** → nommez-le `github-actions`
4. **Copiez le token** (il ne sera affiché qu'une fois !)

---

### Étape 6 — Ajouter les secrets dans GitHub

Sur votre dépôt GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Ajoutez ces 3 secrets :

| Nom | Valeur |
|-----|--------|
| `BLOGGER_API_KEY` | `AIzaSyAlZcoFvzlr7KaMzyfL4L6vYEvMj2QQLyE` |
| `NETLIFY_AUTH_TOKEN` | *(token copié à l'étape 5)* |
| `NETLIFY_SITE_ID` | *(Site ID copié à l'étape 4)* |

---

### Étape 7 — Premier import (lancement manuel)

1. Sur GitHub, allez dans **Actions** → **"Sync Blogger → Netlify"**
2. Cliquez **"Run workflow"** → **"Run workflow"**
3. Attendez ~2 minutes ✅

Votre site est en ligne ! L'URL s'affiche sur Netlify.

---

## ✨ Fonctionnement automatique

À partir de maintenant, **chaque nuit à minuit** :
- GitHub Actions vérifie s'il y a de nouveaux poèmes sur Blogger
- Si oui, il les convertit et reconstruit le site
- Le site Netlify est mis à jour automatiquement

Vous pouvez aussi déclencher une synchro manuellement depuis **GitHub → Actions → Run workflow**.

---

## 📁 Structure du projet

```
poemes-auto/
├── .github/
│   └── workflows/
│       └── sync.yml              ← Automatisation GitHub Actions
├── scripts/
│   ├── import_blogger.py         ← Script d'import
│   └── imported_ids.json         ← Mémorise les articles déjà importés
└── hugo-site/
    ├── hugo.toml                 ← Configuration du site
    ├── netlify.toml              ← Configuration Netlify
    ├── content/
    │   └── poemes/               ← Vos poèmes (générés automatiquement)
    └── themes/
        └── poemes-theme/         ← Thème personnalisé
```

---

## ✏️ Ajouter un poème manuellement

Créez un fichier dans `hugo-site/content/poemes/` :

```markdown
---
title: "Mon poème"
date: 2024-06-01T10:00:00+00:00
tags:
  - "amour"
draft: false
---

Les vers de votre poème ici...
```

Puis `git add . && git commit -m "nouveau poème" && git push` — le site se met à jour en 2 minutes.

---

## 🎨 Personnaliser

Modifiez `hugo-site/hugo.toml` pour changer le titre, la description, l'URL...
