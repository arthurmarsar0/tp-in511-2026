IMAGE      := ghcr.io/ggml-org/llama.cpp:server
CONTAINER  := llama-server
PORT       := 7700
MODEL      := models/gemma-4-E2B-it-Q4_0.gguf
MODEL_URL  := https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_0.gguf?download=true
TEMPLATE   := chat-templates/gemma-template.jinja
NETWORK    := tp-llama
NET_SUBNET := 10.244.77.0/24

# docker accessible without sudo only if daemon is running AND user is in the group
DOCKER := $(shell docker info >/dev/null 2>&1 && echo docker || echo "sudo docker")

# Required Ubuntu packages
# Format: binary:package (check binary) or package only (check via dpkg)
APT_DEPS := docker:docker.io curl:curl wget:wget jq:jq

# llama.cpp server parameters
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

# Server arguments (1 parameter = 1 variable)
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

help: ## Show this help
	@echo "TP ESISAR - AI Agents - LLM"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-8s %s\n", $$1, $$2}'

setup: deps pull model template ## Full setup (packages, image, model, template)

deps: ## Install required packages and start Docker
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
		echo "Installing via apt:$$missing"; \
		sudo apt-get update && sudo apt-get install -y $$missing; \
	else \
		echo "Packages already present."; \
	fi
	@docker info >/dev/null 2>&1 || { \
		echo "Starting Docker daemon..."; \
		sudo systemctl enable --now docker; \
	}
	@if ! groups | grep -qw docker; then \
		sudo usermod -aG docker $$USER 2>/dev/null && \
		echo "[$$USER added to docker group - logout required; Makefile uses 'sudo docker' meanwhile]"; \
	fi
	@$(DOCKER) --version

template: ## Copy chat template from /tmp to the repository
	@if [ -f $(TEMPLATE) ]; then \
		echo "Chat template already present: $(TEMPLATE)"; \
	elif [ -f /tmp/gemma-template.jinja ]; then \
		mkdir -p chat-templates && cp /tmp/gemma-template.jinja $(TEMPLATE) && \
		echo "Chat template copied from /tmp/gemma-template.jinja"; \
	else \
		echo "ERROR: /tmp/gemma-template.jinja not found (ask your teacher for the file)"; exit 1; \
	fi

pull: ## Download llama.cpp:server image
	$(DOCKER) pull $(IMAGE)

model: ## Download GGUF model (Q4) to models/
	@if [ -f $(MODEL) ]; then \
		echo "Model already present: $(MODEL)"; \
	else \
		mkdir -p models && \
		wget -c -O $(MODEL) "$(MODEL_URL)"; \
	fi

start: ## Start llama.cpp server (Gemma model) on port 7700
	@if ! $(DOCKER) image inspect $(IMAGE) >/dev/null 2>&1; then \
		echo "ERROR: image missing - run 'make setup' (or 'make pull')"; exit 1; \
	fi
	@if [ ! -f $(MODEL) ]; then \
		echo "ERROR: model missing - run 'make setup' (or 'make model')"; exit 1; \
	fi
	@if [ ! -f $(TEMPLATE) ]; then \
		echo "ERROR: chat template missing - run 'make template'"; exit 1; \
	fi
	@if [ -n "$$($(DOCKER) ps -q -f name=^$(CONTAINER)$$)" ]; then \
		echo "Container '$(CONTAINER)' is already running."; \
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
		echo "llama-server started on http://localhost:$(PORT)"; \
	fi

stop: ## Stop (and remove) the llama-server container
	$(DOCKER) stop $(CONTAINER)

status: ## Show container status
	@$(DOCKER) ps -a --filter name=^$(CONTAINER)$$ --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

logs: ## Show server logs
	$(DOCKER) logs --tail 100 $(CONTAINER)

test: ## Send a test request to /v1/chat/completions (answer via jq)
	curl -s http://localhost:$(PORT)/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model": "gemma", "messages": [{"role": "user", "content": "Define an AI agent in one sentence."}], "max_tokens": 512}' | jq '.choices[0].message.content'
