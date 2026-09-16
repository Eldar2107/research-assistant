#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.concurrency.orchestrator import fetch_sources_sequential, gather_sources


DEFAULT_QUESTIONS_PATH = ROOT / "data" / "research_questions.json"
DEFAULT_ARTIFACTS_DIR = ROOT / "artefacts"


def load_questions(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    questions = payload.get("questions", [])
    return [item["text"] for item in questions]


async def benchmark_sequential(questions: list[str]) -> dict:
    started = time.perf_counter()
    results: list[list] = []
    for question in questions:
        result = await fetch_sources_sequential(question, max_results=2)
        results.append(result)
    elapsed = time.perf_counter() - started
    return {
        "mode": "sequential",
        "elapsed_seconds": round(elapsed, 4),
        "total_sources": sum(len(items) for items in results),
        "questions": len(questions),
        "average_seconds_per_question": round(elapsed / len(questions), 4) if questions else 0.0,
    }


async def benchmark_concurrent(questions: list[str]) -> dict:
    started = time.perf_counter()
    results = await asyncio.gather(
        *(gather_sources(question, max_results=2) for question in questions),
        return_exceptions=True,
    )
    elapsed = time.perf_counter() - started
    valid_results = [r for r in results if not isinstance(r, Exception)]
    return {
        "mode": "concurrent",
        "elapsed_seconds": round(elapsed, 4),
        "total_sources": sum(len(items) for items in valid_results),
        "questions": len(questions),
        "average_seconds_per_question": round(elapsed / len(questions), 4) if questions else 0.0,
        "failed_questions": sum(1 for r in results if isinstance(r, Exception)),
    }


def write_report(results: dict, questions_path: Path) -> Path:
    DEFAULT_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = DEFAULT_ARTIFACTS_DIR / f"benchmark_{timestamp}.md"
    json_path = DEFAULT_ARTIFACTS_DIR / f"benchmark_{timestamp}.json"

    sequential = results["sequential"]
    concurrent = results["concurrent"]
    speedup = 0.0
    if concurrent["elapsed_seconds"]:
        speedup = sequential["elapsed_seconds"] / concurrent["elapsed_seconds"]

    markdown = f"""# Research Assistant Benchmark Report

- Generated: {datetime.now(timezone.utc).isoformat()}
- Questions source: {questions_path}

| Mode | Questions | Total sources | Elapsed (s) | Avg / question (s) | Failed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sequential | {sequential['questions']} | {sequential['total_sources']} | {sequential['elapsed_seconds']:.4f} | {sequential['average_seconds_per_question']:.4f} | 0 |
| Concurrent | {concurrent['questions']} | {concurrent['total_sources']} | {concurrent['elapsed_seconds']:.4f} | {concurrent['average_seconds_per_question']:.4f} | {concurrent['failed_questions']} |

## Summary

- Speedup: {speedup:.2f}x faster in the concurrent mode.
- The concurrent pathway runs all source fetches in parallel using the async orchestrator and tolerates individual failures with graceful degradation.
"""

    report_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return report_path


async def main() -> None:
    parser = argparse.ArgumentParser(description="Compare sequential vs concurrent research source fetching.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH, help="Path to the JSON file containing research questions.")
    parser.add_argument("--max-questions", type=int, default=None, help="Optional limit for a quicker benchmark run.")
    args = parser.parse_args()

    questions = load_questions(args.questions)
    if args.max_questions is not None:
        questions = questions[: args.max_questions]

    sequential = await benchmark_sequential(questions)
    concurrent = await benchmark_concurrent(questions)

    report = {"questions_file": str(args.questions), "questions_count": len(questions), "sequential": sequential, "concurrent": concurrent}
    output_path = write_report(report, args.questions)
    print(f"Benchmark complete: {output_path}")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
