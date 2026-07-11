#!/usr/bin/env python3
"""kra — the Knee Research Agent command line interface (MVP).

Reproduces the manual pipeline validated in RUN-2026-07-001:

    kra ingest --title "..." --doi 10.x/y --topic TOPIC-PRP
    kra review PAPER-2026-0002
    kra consolidate TOPIC-PRP
    kra report TOPIC-PRP
    kra insight TOPIC-PRP
    kra list
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the top-level packages (core, agents, workflows, cli) importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pipeline import stages  # noqa: E402
from core.storage import registry  # noqa: E402


def cmd_ingest(args: argparse.Namespace) -> int:
    entry = stages.ingest(
        title=args.title,
        doi=args.doi,
        pmid=args.pmid,
        year=args.year,
        study_type=args.study_type,
        topics_list=args.topic,
    )
    print(f"Ingested {entry['paper_id']} (status: {entry['status']})")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    path = stages.review(args.paper_id)
    print(f"Reviewed {args.paper_id} -> {path}")
    return 0


def cmd_consolidate(args: argparse.Namespace) -> int:
    result = stages.consolidate(args.topic_id)
    print(
        f"Consolidated {args.topic_id}: "
        f"{len(result['papers_consolidated'])} paper(s) -> {result['current']}"
    )
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    path = stages.report(args.topic_id)
    print(f"Report for {args.topic_id} -> {path}")
    return 0


def cmd_insight(args: argparse.Namespace) -> int:
    path = stages.insight(args.topic_id)
    print(f"Insight for {args.topic_id} -> {path}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    reg = registry.load()
    if not reg["papers"]:
        print("(registry is empty)")
        return 0
    for p in reg["papers"]:
        print(f"{p['paper_id']}  [{p['status']:<12}]  {p.get('title', '')}")
    return 0


def cmd_run_paper(args: argparse.Namespace) -> int:
    from application.workflows import PaperIngestionWorkflow
    from infrastructure.ai.stub import StubAIReviewer
    from infrastructure.repositories.json_registry import JsonPaperRepository
    from infrastructure.repositories.file_review_store import FileReviewStore

    workflow = PaperIngestionWorkflow(JsonPaperRepository(), StubAIReviewer(), FileReviewStore())
    summary = workflow.run(
        doi=args.doi, title=args.title, pmid=args.pmid, year=args.year, topics=args.topic
    )
    for i, step in enumerate(summary["steps"], 1):
        print(f"{i}. {step}")
    print("")
    print(f"Workflow: {summary['state']} in {summary['duration_s']}s")
    print(f"Done: {summary['paper_id']} [{summary['status']}] — {summary['n_claims']} claim(s)")
    print(f"  review: {summary['review']}")
    print(f"  claims: {summary['claims']}")
    return 0


def cmd_review_package(args: argparse.Namespace) -> int:
    from pathlib import Path

    from benchmark import load_dataset
    from core.models import Paper
    from infrastructure.ai import build_review_package

    gold = load_dataset(name=args.dataset)
    out = Path(args.out)
    n = 0
    for entry in gold.curated():
        paper = Paper(
            paper_id=entry.gold_id, title=entry.title, doi=entry.doi, pmid=entry.pmid,
            year=entry.year, abstract=entry.abstract or None, study_type=entry.study_type,
            topics=[entry.area],
        )
        build_review_package(paper, out)
        n += 1
    print(f"Wrote {n} review packages under {out}/<gold_id>/ (prompt.md, schema.json, metadata.json).")
    print("Fill each answer as runs/manual/reviews/<gold_id>.json (or a single reviews.json "
          "map), then run: kra benchmark --model manual")
    return 0


def cmd_report_month(args: argparse.Namespace) -> int:
    from datetime import date
    from application.use_cases.executive_report import generate_executive_report

    month = args.month or date.today().strftime("%Y-%m")
    out = generate_executive_report(month)
    print(f"Executive report written: {out}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    from application.use_cases.stats import format_stats, gather_stats

    print(format_stats(gather_stats()))
    return 0


def cmd_insights_month(args: argparse.Namespace) -> int:
    from datetime import date
    from application.use_cases.personal_insights import generate_personal_insights

    month = args.month or date.today().strftime("%Y-%m")
    out = generate_personal_insights(month)
    print(f"Personal insight written: {out}")
    return 0


def cmd_run_research(args: argparse.Namespace) -> int:
    from application.research_run import ResearchRun, default_areas

    areas = args.area or default_areas()
    print(f"ResearchRun (Phase 1) over {len(areas)} area(s): {', '.join(areas)}")
    manifest = ResearchRun().run(areas, resume=args.resume)
    print(f"Run {manifest['run_id']} — status: {manifest['status']}")
    for s in manifest["stages"]:
        if s.get("status") == "completed":
            print(f"  {s['area']:<32} v{s.get('version','?')}  {s.get('deltas',0)} delta(s)"
                  f"{'' if s.get('changed') else '  (no change)'}")
        else:
            print(f"  {s['area']:<32} {s.get('status')}")
    print(f"Recorded: runs/{manifest['month']}/{manifest['run_id']}/ (manifest, metrics, logs, outputs)")
    return 0 if manifest["status"] == "completed" else 1


def cmd_consolidate_topic(args: argparse.Namespace) -> int:
    from application.use_cases.consolidate_knowledge import consolidate_topic_knowledge

    print("Reading validated reviews...")
    print("Merging evidence...")
    print("Updating consensus...")
    print("Updating controversies...")
    run = consolidate_topic_knowledge(args.area)
    if not run.changed:
        print(f"No new evidence for {run.topic_id} — nothing to consolidate (idempotent).")
        if run.skipped_gate:
            print(f"Skipped (failed Quality Gates): {', '.join(run.skipped_gate)}")
        return 0
    print(f"Confidence: {run.confidence_before} -> {run.confidence_after}")
    print(f"Knowledge Delta(s) created: {len(run.ledger_ids)}")
    print(f"Topic version: v{run.version}")
    print(f"Ledger entries: {', '.join(run.ledger_ids)}")
    print(f"Saved: knowledge/en/topics/{run.topic_id}/ (+ obsidian/{run.topic_id}.md)")
    if run.skipped_gate:
        print(f"Skipped (failed Quality Gates): {', '.join(run.skipped_gate)}")
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    from benchmark import BenchmarkRunner, load_dataset
    from benchmark.models import available, get_reviewer

    gold = load_dataset(name=args.dataset)
    try:
        if args.model == "manual":
            from pathlib import Path
            from infrastructure.ai import ManualAIProvider
            reviewer = ManualAIProvider(Path(args.reviews) if args.reviews else None)
        else:
            reviewer = get_reviewer(args.model)
        result = BenchmarkRunner(reviewer, args.model).run(gold)
    except (ValueError, RuntimeError) as e:
        print(f"Cannot run model '{args.model}': {e}")
        print(f"Available providers: {', '.join(available())}")
        return 1

    curated = len(gold.curated())
    reviewed = result.n_entries
    gv = getattr(gold, "gold_version", "?")
    print(f"Dataset: {gold.name} v{gv}  ({curated} curated / {len(gold.entries)} entries)")
    if result.pending:
        print(f"Reviewed: {reviewed}/{curated}  ({len(result.pending)} pending manual reviews)")
    print("")
    print("Headline KPI")
    print(f"  GRSS (Gold Review Similarity Score) : {result.grss * 100:5.1f}%")
    print(f"  CDR  (Controversy Detection Rate)   : {result.cdr * 100:5.1f}%")
    print(f"  UCR  (Unsupported Claim Rate)       : {result.ucr * 100:5.1f}%   (lower is better)")
    if result.grss_components:
        print("")
        print("  GRSS breakdown (where the reviewer succeeds/fails)")
        for k, v in result.grss_components.items():
            print(f"    {k:<18}: {v * 100:5.1f}%")
    print("")
    print("Supporting metrics")
    print(f"  Coverage        : {result.coverage * 100:5.1f}%")
    print(f"  Traceability    : {result.traceability * 100:5.1f}%")
    print(f"  Hallucinations  : {result.hallucinations}")
    print(f"  Quality gates   : {result.gate_pass_rate * 100:5.1f}% passed")
    print(f"  Cost / Time     : ${result.cost_usd:.3f} / {result.time_s:.4f}s")
    if args.model in ("stub", "fake"):
        print("")
        print(f"Note: '{args.model}' is a key-free provider (no real extraction). Use "
              "--model manual (Claude Code as engine) or --model claude (with an API key).")
    if result.pending:
        print("")
        print(f"Pending manual reviews: {', '.join(result.pending)}")
        print("Generate them with: kra review-package  (then fill runs/manual/reviews/).")
    if curated < 30:
        print("")
        print(f"Note: gold standard has {curated}/30 curated entries — expand only when the "
              "metrics reveal a gap (benchmark drives the corpus, not the other way around).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kra", description="Knee Research Agent (MVP)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest", help="register a paper (status: pending_review)")
    p.add_argument("--title", required=True)
    p.add_argument("--doi")
    p.add_argument("--pmid")
    p.add_argument("--year", type=int)
    p.add_argument("--study-type", dest="study_type")
    p.add_argument("--topic", action="append", default=[], help="related topic id (repeatable)")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("review", help="scaffold a Paper Review and mark it reviewed")
    p.add_argument("paper_id")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("consolidate", help="consolidate reviewed papers into a Living Clinical Topic")
    p.add_argument("topic_id")
    p.set_defaults(func=cmd_consolidate)

    p = sub.add_parser("report", help="scaffold the monthly Executive Report")
    p.add_argument("topic_id")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("insight", help="scaffold a Personal Insight")
    p.add_argument("topic_id")
    p.set_defaults(func=cmd_insight)

    p = sub.add_parser("list", help="list the papers in the registry")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("run", help="run a full workflow (vertical slice)")
    runsub = p.add_subparsers(dest="target", required=True)
    pp = runsub.add_parser("paper", help="ingest one paper end to end")
    pp.add_argument("--doi")
    pp.add_argument("--title")
    pp.add_argument("--pmid")
    pp.add_argument("--year", type=int)
    pp.add_argument("--topic", action="append", default=[])
    pp.set_defaults(func=cmd_run_paper)

    pr = runsub.add_parser("research", help="ResearchRun: drive the whole pipeline (Phase 1)")
    pr.add_argument("--area", action="append", default=[], help="area to run (repeatable; default: all)")
    pr.add_argument("--resume", default=None, help="resume an existing run id, e.g. RUN-0001")
    pr.set_defaults(func=cmd_run_research)

    p = sub.add_parser("benchmark", help="benchmark the pipeline over a dataset")
    p.add_argument("--dataset", default="gold-standard")
    p.add_argument("--model", default="stub", help="stub | fake | manual | claude")
    p.add_argument("--reviews", default=None, help="reviews dir for --model manual")
    p.set_defaults(func=cmd_benchmark)

    p = sub.add_parser("review-package", help="emit review packages for manual (key-free) reviewing")
    p.add_argument("--dataset", default="gold-standard")
    p.add_argument("--out", default="runs/manual/packages")
    p.set_defaults(func=cmd_review_package)

    p = sub.add_parser("consolidate-topic", help="consolidate a topic's validated reviews into a Living Topic + Ledger")
    p.add_argument("area", help="clinical area, e.g. 'PRP' or 'Mesenchymal Stem Cells'")
    p.set_defaults(func=cmd_consolidate_topic)

    p = sub.add_parser("report-month", help="generate the monthly Executive Report from the Knowledge Ledger")
    p.add_argument("--month", default=None, help="YYYY-MM (default: current month)")
    p.set_defaults(func=cmd_report_month)

    p = sub.add_parser("insights-month", help="generate the monthly Personal Insight ('¿Ha cambiado algo para mí?')")
    p.add_argument("--month", default=None, help="YYYY-MM (default: current month)")
    p.set_defaults(func=cmd_insights_month)

    p = sub.add_parser("stats", help="show a one-glance dashboard of the knowledge base and runs")
    p.set_defaults(func=cmd_stats)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
