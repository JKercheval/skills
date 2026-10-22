# Personal agent skills for Claude Code (~/.claude/skills) and Codex (~/.agents/skills).
# Each skill in a source folder is symlinked into both tools' personal skill folders.
# global/ is copied into ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md.
#
# Per-machine settings go in local.mk (gitignored). See local.mk.example.

-include local.mk

SOURCES ?= skills
ALL_SOURCES := $(SOURCES) $(EXTRA_SOURCES)
SKILLS := uv run --quiet python scripts/skills.py $(foreach s,$(ALL_SOURCES),--source $(s)) $(foreach f,$(GLOBAL_EXTRA),--global-extra $(f))

.DEFAULT_GOAL := help
.PHONY: help status check-global link sync unlink validate new adopt pull test

help:  ## Show the available commands
	@grep -hE '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-13s %s\n", $$1, $$2}'

status:  ## Show each skill's link state in Claude Code and Codex
	@$(SKILLS) status

check-global:  ## Before a sync: show how existing CLAUDE.md and AGENTS.md files differ from what sync writes
	@$(SKILLS) check-global

link:  ## Link every skill into both tools (add DRY_RUN=1 to preview)
	@$(SKILLS) link $(if $(DRY_RUN),--dry-run)

sync:  ## Link every skill and generate the global files (run after git pull or editing global/)
	@$(SKILLS) sync $(if $(DRY_RUN),--dry-run)

unlink:  ## Remove every link this repo created (real directories are never touched)
	@$(SKILLS) unlink $(if $(DRY_RUN),--dry-run)

validate:  ## Check skills against the spec and authoring best practices
	@$(SKILLS) validate

new:  ## Create a skill: make new NAME=my-skill (add MANUAL=1 for invoke-only)
	@$(if $(NAME),,$(error NAME is required, e.g. make new NAME=my-skill))
	@$(SKILLS) new $(NAME) $(if $(MANUAL),--manual)

adopt:  ## Move a skill from ~/.claude/skills or ~/.agents/skills into the repo: make adopt NAME=x
	@$(if $(NAME),,$(error NAME is required, e.g. make adopt NAME=my-skill))
	@$(SKILLS) adopt $(NAME)

pull:  ## git pull, then sync
	git pull --ff-only
	@$(MAKE) --no-print-directory sync

test:  ## Run the tooling tests
	uv run --quiet pytest -q
