# Commandes de projet. Voir docs/PROTOCOL.md.
LOT ?= lot
BASE ?= HEAD~1
HEAD_SHA ?= HEAD
CRITERIA ?=

.PHONY: review review-prepare test-review test-app

review:
	python3 scripts/request_codex_review.py --lot "$(LOT)" --base "$(BASE)" --head "$(HEAD_SHA)" $(if $(CRITERIA),--criteria-file "$(CRITERIA)")

review-prepare:
	python3 scripts/request_codex_review.py --prepare-only --lot "$(LOT)" --base "$(BASE)" --head "$(HEAD_SHA)" $(if $(CRITERIA),--criteria-file "$(CRITERIA)")

test-review:
	python3 -m unittest scripts/tests/test_request_codex_review.py

test-app:
	cd muraja && npm test && npm run typecheck
