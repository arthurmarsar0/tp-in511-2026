IMAGE      := ghcr.io/ggml-org/llama.cpp:server
CONTAINER  := llama-server
PORT       := 7700
MODEL      := models/gemma-4-E2B-it-Q4_0.gguf
MODEL_URL  := https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_0.gguf?download=true
TEMPLATE   := chat-templates/gemma-template.jinja
NETWORK    := tp-llama
NET_SUBNET := 10.244.77.0/24

# docker accessible sans sudo seulement si le daemon tourne ET l'utilisateur est dans le groupe
DOCKER := $(shell docker info >/dev/null 2>&1 && echo docker || echo "sudo docker")

# Paquets Ubuntu requis
# Format: binaire:paquet (vérifie le binaire) ou paquet seul (vérifie via dpkg)
APT_DEPS := docker:docker.io curl:curl wget:wget jq:jq

# Paramètres du serveur llama.cpp
MODEL_FILE       := /models/$(notdir $(MODEL))
TEMPLATE_FILE    := /template/gemma-template.jinja
HOST             := 0.0.0.0
THREADS          := 2
CONTEXT_SIZE     := 16000
SPEC_TYPE        := ngram-mod
SPEC_N_MATCH     := 24
SPEC_N_MIN       := 48
SPEC_N_MAX       := 64
CTK              := q8_0
CTV              := q4_0
LM               := mmap
TEMP             := 1.0
TOP_K            := 64
TOP_P            := 0.95
MIN_P            := 0.0
REPEAT_PENALTY   := 1.0
PRESENCE_PENALTY := 0.0

# Arguments du serveur (1 paramètre = 1 variable)
ARG_MODEL            := -m $(MODEL_FILE)
ARG_TEMPLATE         := --chat-template-file $(TEMPLATE_FILE)
ARG_HOST             := --host $(HOST)
ARG_PORT             := --port $(PORT)
ARG_SPEC_TYPE        := --spec-type $(SPEC_TYPE)
ARG_THREADS          := -t $(THREADS)
ARG_SPEC_N_MATCH     := --spec-ngram-mod-n-match $(SPEC_N_MATCH)
ARG_SPEC_N_MIN       := --spec-ngram-mod-n-min $(SPEC_N_MIN)
ARG_SPEC_N_MAX       := --spec-ngram-mod-n-max $(SPEC_N_MAX)
ARG_CTK              := -ctk $(CTK)
ARG_CTV              := -ctv $(CTV)
ARG_LM               := -lm $(LM)
ARG_CONTEXT          := -c $(CONTEXT_SIZE)
ARG_TEMP             := --temp $(TEMP)
ARG_TOP_K            := --top-k $(TOP_K)
ARG_TOP_P            := --top-p $(TOP_P)
ARG_MIN_P            := --min-p $(MIN_P)
ARG_REPEAT_PENALTY   := --repeat-penalty $(REPEAT_PENALTY)
ARG_PRESENCE_PENALTY := --presence-penalty $(PRESENCE_PENALTY)

SERVER_ARGS := $(ARG_MODEL) $(ARG_TEMPLATE) $(ARG_HOST) $(ARG_PORT) \
	$(ARG_SPEC_TYPE) $(ARG_THREADS) \
	$(ARG_SPEC_N_MATCH) $(ARG_SPEC_N_MIN) $(ARG_SPEC_N_MAX) \
	$(ARG_CTK) $(ARG_CTV) $(ARG_LM) $(ARG_CONTEXT) \
	$(ARG_TEMP) $(ARG_TOP_K) $(ARG_TOP_P) $(ARG_MIN_P) \
	$(ARG_REPEAT_PENALTY) $(ARG_PRESENCE_PENALTY)

.PHONY: help setup deps template pull model start stop status logs test

help: ## Affiche cette aide
	@echo "TP ESISAR - Agents IA - LLM"
	@echo ""
	@echo "Cibles disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-8s %s\n", $$1, $$2}'

setup: deps pull model template ## Préparation complète (paquets, image, modèle, template)

deps: ## Installe les paquets requis et démarre Docker
	@missing=""; \
	for dep in $(APT_DEPS); do \
		case $$dep in \
			*:*) bin=$${dep%%:*}; pkg=$${dep##*:}; \
				command -v $$bin >/dev/null 2>&1 || missing="$$missing $$pkg" ;; \
			*)   pkg=$$dep; \
				dpkg -s $$pkg >/dev/null 2>&1 || missing="$$missing $$pkg" ;; \
		esac; \
	done; \
	if [ -n "$$missing" ]; then \
		echo "Installation via apt :$$missing"; \
		sudo apt-get update && sudo apt-get install -y $$missing; \
	else \
		echo "Paquets déjà présents."; \
	fi
	@docker info >/dev/null 2>&1 || { \
		echo "Démarrage du daemon Docker..."; \
		sudo systemctl enable --now docker; \
	}
	@if ! groups | grep -qw docker; then \
		sudo usermod -aG docker $$USER 2>/dev/null && \
		echo "[$$USER ajouté au groupe docker — reconnexion requise ; le Makefile utilise 'sudo docker' en attendant]"; \
	fi
	@$(DOCKER) --version

template: ## Copie le chat template depuis /tmp dans le dépôt
	@if [ -f $(TEMPLATE) ]; then \
		echo "Chat template déjà présent : $(TEMPLATE)"; \
	elif [ -f /tmp/gemma-template.jinja ]; then \
		mkdir -p chat-templates && cp /tmp/gemma-template.jinja $(TEMPLATE) && \
		echo "Chat template copié depuis /tmp/gemma-template.jinja"; \
	else \
		echo "ERREUR : /tmp/gemma-template.jinja introuvable (demander le fichier au prof)"; exit 1; \
	fi

pull: ## Télécharge l'image llama.cpp:server
	$(DOCKER) pull $(IMAGE)

model: ## Télécharge le modèle GGUF (Q4) dans models/
	@if [ -f $(MODEL) ]; then \
		echo "Modèle déjà présent : $(MODEL)"; \
	else \
		mkdir -p models && \
		wget -c -O $(MODEL) "$(MODEL_URL)"; \
	fi

start: ## Démarre le serveur llama.cpp (modèle Gemma) sur le port 7700
	@if ! $(DOCKER) image inspect $(IMAGE) >/dev/null 2>&1; then \
		echo "ERREUR : image absente — lancez 'make setup' (ou 'make pull')"; exit 1; \
	fi
	@if [ ! -f $(MODEL) ]; then \
		echo "ERREUR : modèle absent — lancez 'make setup' (ou 'make model')"; exit 1; \
	fi
	@if [ ! -f $(TEMPLATE) ]; then \
		echo "ERREUR : chat template absent — lancez 'make template'"; exit 1; \
	fi
	@if [ -n "$$($(DOCKER) ps -q -f name=^$(CONTAINER)$$)" ]; then \
		echo "Le conteneur '$(CONTAINER)' est déjà en cours d'exécution."; \
	else \
		$(DOCKER) rm -f $(CONTAINER) >/dev/null 2>&1 || true; \
		$(DOCKER) network inspect $(NETWORK) >/dev/null 2>&1 || $(DOCKER) network create --subnet $(NET_SUBNET) $(NETWORK); \
		$(DOCKER) run -d --rm --name $(CONTAINER) \
			-v "$(CURDIR)/models:/models" \
			-v "$(CURDIR)/$(TEMPLATE):/template/gemma-template.jinja:ro" \
			--network $(NETWORK) -p $(PORT):$(PORT) \
			--health-cmd "curl -sf -m 5 http://localhost:$(PORT)/health" \
			--health-interval 30s --health-start-period 90s \
			$(IMAGE) $(SERVER_ARGS); \
		echo "llama-server démarré sur http://localhost:$(PORT)"; \
	fi

stop: ## Arrête (et supprime) le conteneur llama-server
	$(DOCKER) stop $(CONTAINER)

status: ## Affiche l'état du conteneur
	@$(DOCKER) ps -a --filter name=^$(CONTAINER)$$ --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

logs: ## Affiche les journaux du serveur
	$(DOCKER) logs --tail 100 $(CONTAINER)

test: ## Envoie une requête de test sur /v1/chat/completions (réponse via jq)
	curl -s http://localhost:$(PORT)/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model": "gemma", "messages": [{"role": "user", "content": "D\u00e9finis un agent IA en une phrase."}], "max_tokens": 512}' | jq '.choices[0].message.content'
