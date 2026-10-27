SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

SECRETS   := secrets.local.yml
SCRAMBLED := secrets.scrambled.yml
ENCRYPTED := secrets.age
AGE_KEY   ?= secrets.key
FORCE     ?= 0
MSG       ?= docs: update
REMOTE    ?= origin
FONT      ?= Inter
CODE_FONT ?= Fira Code
MKDOCS    := $(if $(wildcard .venv/bin/mkdocs),.venv/bin/mkdocs,mkdocs)

export DOCS_FONT := $(FONT)
export DOCS_CODE_FONT := $(CODE_FONT)

.PHONY: help setup unlock scramble lock serve build check publish clean fonts

setup: ## create .venv and install requirements
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

fonts: ## list interchangeable fonts (FONT=... CODE_FONT=...)
	@echo "JetBrains Mono, Fira Code, IBM Plex Mono, Source Code Pro, Ubuntu Mono, Inconsolata"
	@echo "Material default: Roboto / Roboto Mono"
	@echo "Usage: make serve FONT=\"Fira Code\""
	@echo "       make serve FONT=Roboto CODE_FONT=\"Roboto Mono\""

help: ## show targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

unlock: ## decrypt secrets.age -> secrets.local.yml (needs secrets.key)
	@command -v age >/dev/null || { echo "install age"; exit 1; }
	@test -f "$(AGE_KEY)" || { echo "missing $(AGE_KEY); restore it from your backup"; exit 1; }
	@test -f "$(ENCRYPTED)" || { echo "missing $(ENCRYPTED)"; exit 1; }
	@if [ -e "$(SECRETS)" ] && [ "$(FORCE)" != "1" ]; then \
		echo "$(SECRETS) already exists; use 'make unlock FORCE=1' to overwrite"; \
		exit 1; \
	else \
		tmp=$$(mktemp) && \
		age -d -i "$(AGE_KEY)" "$(ENCRYPTED)" > "$$tmp" && \
		chmod 600 "$$tmp" && \
		mv "$$tmp" "$(SECRETS)" || { rm -f "$$tmp"; echo "decrypt failed"; exit 1; }; \
		echo "decrypted -> $(SECRETS)"; \
	fi

scramble: ## regenerate public scrambled values from secrets.local.yml
	@test -f "$(SECRETS)" || { echo "missing $(SECRETS); run make unlock"; exit 1; }
	@test -f "$(AGE_KEY)" || { echo "missing $(AGE_KEY); restore it from your backup"; exit 1; }
	@python3 scripts/scramble.py

lock: scramble ## encrypt secrets.local.yml -> secrets.age
	@command -v age >/dev/null || { echo "install age"; exit 1; }
	@command -v age-keygen >/dev/null || { echo "install age-keygen"; exit 1; }
	@test -f "$(AGE_KEY)" || { echo "missing $(AGE_KEY); restore it from your backup"; exit 1; }
	@recipient=$$(age-keygen -y "$(AGE_KEY)") || { echo "cannot derive public key from $(AGE_KEY)"; exit 1; }; \
	age -r "$$recipient" -o "$(ENCRYPTED).tmp" "$(SECRETS)" || { rm -f "$(ENCRYPTED).tmp"; exit 1; }
	@mv "$(ENCRYPTED).tmp" "$(ENCRYPTED)"
	@echo "encrypted -> $(ENCRYPTED)"

serve: ## local preview with real values
	@command -v $(MKDOCS) >/dev/null 2>&1 || { echo "mkdocs not installed; run 'make setup'"; exit 1; }
	@test -f "$(SECRETS)" || echo "note: $(SECRETS) missing; using $(SCRAMBLED) if present"
	$(MKDOCS) serve

build: ## build with real values -> site/
	@command -v $(MKDOCS) >/dev/null 2>&1 || { echo "mkdocs not installed; run 'make setup'"; exit 1; }
	@test -f "$(SECRETS)" || echo "note: $(SECRETS) missing; using $(SCRAMBLED) if present"
	$(MKDOCS) build -d site

check: ## leak / placeholder check
	@python3 scripts/check.py

publish: lock check ## lock + check + commit/push
	git add -u
	git add docs scripts Makefile README.md mkdocs.yml .gitignore .github .gitlab-ci.yml secrets.age secrets.scrambled.yml
	@if ! git diff --cached --quiet; then \
		git commit -m "$(MSG)"; \
	else \
		echo "nothing to commit"; \
	fi
	git push "$(REMOTE)" HEAD

clean: ## remove build output (keeps secrets)
	rm -rf site public
