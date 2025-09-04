# Gestion_Presence - Test Collaboration
# 📌 API de Gestion des Présences

Ce projet est une API REST développée avec **Django et **Django REST Framework (DRF)**.  
Elle permet de gérer les employés, leurs présences quotidiennes et la génération de rapports, avec une sécurité basée sur **JWT Authentication**.



## Fonctionnalités principales

- **Gestion des employés** (CRUD : créer, lire, modifier, supprimer).
- **Gestion des présences** (enregistrement des arrivées et sorties).
- **Rapports de présence** (journalier, hebdomadaire, etc.).
- **Authentification sécurisée avec JWT** :
  - Inscription / Connexion des utilisateurs.
  - Attribution de tokens d’accès et de rafraîchissement.
  - Protection des endpoints sensibles.



## Structure du projet

### 1. **Création du projet et de l’application**
- `django-admin startproject`
- `python manage.py startapp api`
- Ajout de `api` dans `INSTALLED_APPS`.

### 2. **Modélisation des données**
Dans `api/models.py` :
- **Employe** : infos des employés (nom, email, rôle).
- **Presence** : suivi des présences (date, heure arrivée, heure sortie, employé).
- **Rapport** : génération des rapports.

Chaque modèle intègre des méthodes métiers utiles  
(ex: `enregistrer_arrivee()`, `enregistrer_sortie()`).

### 3. **Sérialisation**
Dans `api/serializers.py` :
- `EmployeSerializer`
- `PresenceSerializer`
- `RapportSerializer`  

⚡ `EmployeSerializer` inclut l’historique des présences.

### 4. **Vues et API**
Dans `api/views.py` :
- `EmployeViewSet`
- `PresenceViewSet`
- `RapportViewSet`  

Ajout d’**actions personnalisées** avec `@action`  
(ex: `enregistrer_arrivee`, `enregistrer_sortie`).

### 5. **Routage**
Dans `urls.py` :
- `DefaultRouter` pour générer les endpoints.
- Endpoints accessibles sous `/api/`.

### 6. **Documentation interactive**
- Swagger activé via **drf-yasg**.
- Accessible sur : [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)


## Authentification JWT

L’authentification est implémentée via **djangorestframework-simplejwt**.  

Endpoints disponibles :  
- `/api/token/` → Récupérer un token d’accès et de rafraîchissement.
- `/api/token/refresh/` → Rafraîchir le token.
- `/api/token/verify/` → Vérifier la validité d’un token.



Actions personnalisées disponibles :

/api/presences/{id}/enregistrer_arrivee/

/api/presences/{id}/enregistrer_sortie/

**Prochaines étapes**

Amélioration de la gestion des permissions (rôles Admin, RH, Employé).

Ajout de filtres avancés pour les rapports.

Mise en place de tests automatisés.

