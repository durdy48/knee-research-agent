# KRA — common tasks. Run `make help` to list them.
.PHONY: help test benchmark run report insights stats

help:
	@echo "make test       - run every test suite"
	@echo "make benchmark  - benchmark the manual provider vs the Gold Standard"
	@echo "make run        - run the full pipeline (ResearchRun: consolidate + report + insight)"
	@echo "make report     - regenerate the current month's Executive Report"
	@echo "make insights   - regenerate the current month's Personal Insight"
	@echo "make stats      - show the knowledge-base dashboard"

test:
	@for t in src/tests/test_*.py; do python3 "$$t" || exit 1; done

benchmark:
	./kra benchmark --model manual

run:
	./kra run research

report:
	./kra report-month

insights:
	./kra insights-month

stats:
	./kra stats
