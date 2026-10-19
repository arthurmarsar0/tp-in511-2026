# TP ESISAR — Agents IA — LLM

Déploiement d'un serveur LLM local (Gemma 4 E2B) via llama.cpp dans Docker, avec API compatible OpenAI.

## Prérequis

- `docker`, `make`, `wget`, `curl`, `jq`

## Sommaire

- [0. Préparation : `make setup`](#étape-0--préparation--make-setup)
- [1. Lancement du serveur : `make start`](#étape-1--lancement-du-serveur--make-start)
- [2. Test de l'API](#étape-2--test-de-lapi)
- [3. Arrêt du serveur : `make stop`](#étape-3--arrêt-du-serveur--make-stop)
- [Dépannage](#dépannage)

---

## Étape 0 — Préparation : `make setup`

```bash
make setup
```

Installe les dépendances manquantes et prépare l'environnement. La commande est idempotente : les étapes déjà satisfaites sont ignorées.

| Cible | Action |
|-------|--------|
| `deps` | Vérifie `docker`, `curl`, `wget`, `jq`. Installe via `apt` ce qui manque. Démarre le daemon Docker. Ajoute l'utilisateur au groupe `docker` si nécessaire. |
| `pull` | Télécharge l'image `ghcr.io/ggml-org/llama.cpp:server`. |
| `model` | Télécharge le modèle GGUF Q4 (~2,8 Go) dans `models/`. |
| `template` | Vérifie la présence du chat template dans `chat-templates/`. |

### Éléments déployés

- **Image Docker** : `ghcr.io/ggml-org/llama.cpp:server` — serveur HTTP avec API compatible OpenAI.
- **Modèle** : [ggml-org/gemma-4-E2B-it-GGUF](https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF), quantification `Q4_0`. Stocké dans `models/`, monté en lecture dans le conteneur à `/models`.
- **Chat template** : `chat-templates/gemma-template.jinja` (fork `custom_pub_chat_template_gemma4.jinja`). Monté en lecture seule à `/template/gemma-template.jinja`.

---

## Étape 1 — Lancement du serveur : `make start`

```bash
make start
```

Démarre le serveur llama.cpp dans un conteneur Docker sur le port 7700.

Paramètres appliqués :

- Réseau Docker dédié `tp-llama` (`10.244.77.0/24`)
- Volumes : `models/` → `/models`, `chat-templates/gemma-template.jinja` → `/template/gemma-template.jinja`
- Décodage spéculatif par n-grammes, 2 threads
- Contexte 16 000 tokens, KV cache quantifié (`q8_0`/`q4_0`)

### Endpoints

| URL | Description |
|-----|-------------|
| `http://localhost:7700/` | Interface web de chat |
| `http://localhost:7700/health` | Sonde de disponibilité |
| `http://localhost:7700/v1/models` | Liste des modèles |
| `http://localhost:7700/v1/chat/completions` | API de chat (compatible OpenAI) |

---

## Étape 2 — Test de l'API

**Vérifier la disponibilité :**

```bash
curl http://localhost:7700/health
```

**Tester l'API de chat :**

```bash
curl http://localhost:7700/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @- <<'EOF' | jq '.choices[0].message.content'
{
  "model": "gemma-4-E2B-it-Q4_0",
  "messages": [{"role": "user", "content": "Qu'est-ce qu'un agent IA ?"}],
  "max_tokens": 512
}
EOF
```

**Note sur le thinking** : ce modèle raisonne nativement. Le raisonnement apparaît dans le champ `reasoning_content`, la réponse finale dans `content`. Utiliser `max_tokens` ≥ 512 pour laisser le raisonnement se terminer.

---

## Étape 3 — Arrêt du serveur : `make stop`

```bash
make stop
```

Le conteneur est lancé avec `--rm` : il est supprimé automatiquement à l'arrêt.

---

## Dépannage

**Conteneur `(unhealthy)` malgré une API fonctionnelle**

Le `HEALTHCHECK` de l'image teste `localhost:8080` en dur. `make start` le remplace par un test sur le port 7700.

**Connexion bloquée depuis l'hôte, `curl` fonctionne dans le conteneur**

1. Vérifier le chargement du modèle : `make logs` (rechercher `listening on`)
2. Vérifier les variables proxy : `env | grep -i proxy`. Si un proxy est défini, ajouter `localhost,127.0.0.1` à `NO_PROXY`
3. Vérifier le routage VPN : `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' llama-server` puis `ip route get <IP>`. Relancer avec `make stop && make start` pour utiliser le réseau dédié `tp-llama`
