import requests

BASE_URL = "http://127.0.0.1:8000/api/auth"

# Utilisateurs à créer
users = [
    {"email": "admin@example.com", "name": "Admin Test", "password": "admin123", "role": "admin"},
    {"email": "moderator@example.com", "name": "Moderator Test", "password": "mod123", "role": "moderator"},
    {"email": "user@example.com", "name": "User Test", "password": "user123", "role": "user"}
]

# 1Créer les utilisateurs (inscription)
for u in users:
    r = requests.post(f"{BASE_URL}/register/", json=u)
    if r.status_code == 201:
        print(f"Utilisateur {u['role']} créé avec succès")
    elif r.status_code == 400 and "email" in r.text:
        print(f"Utilisateur {u['role']} existe déjà")
    else:
        print(f"Erreur lors de la création de {u['role']}: {r.text}")

# Se connecter pour récupérer les tokens
tokens = {}
for u in users:
    login_data = {"email": u["email"], "password": u["password"]}
    r = requests.post(f"{BASE_URL}/login/", json=login_data)
    if r.status_code == 200:
        tokens[u["role"]] = r.json()["access"]
        print(f"Token récupéré pour {u['role']}")
    else:
        print(f"Erreur login {u['role']}: {r.text}")

# Tester les routes protégées
routes = {
    "admin-only": "/admin-only/",
    "moderator-only": "/moderator-only/",
    "user-only": "/user-only/"
}

for route_name, route_path in routes.items():
    print(f"\n=== Test de {route_name} ===")
    for role, token in tokens.items():
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}{route_path}", headers=headers)
        status = response.status_code
        try:
            data = response.json()
        except:
            data = response.text
        print(f"{role.capitalize()} access ({status}): {data}")
