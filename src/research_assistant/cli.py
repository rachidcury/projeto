"""CLI entry-point for the research assistant."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from research_assistant.app import ResearchAssistant


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-assistant",
        description="Automate Google NotebookLM research workflows.",
    )
    parser.add_argument(
        "--profile", default=None, help="NotebookLM auth profile name"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- list ---
    sub.add_parser("list", help="List all notebooks")

    # --- create ---
    p_create = sub.add_parser("create", help="Create a notebook with sources")
    p_create.add_argument("title", help="Notebook title")
    p_create.add_argument("--url", action="append", default=[], help="Add a URL source (repeatable)")
    p_create.add_argument("--file", action="append", default=[], help="Add a local file source (repeatable)")

    # --- ask ---
    p_ask = sub.add_parser("ask", help="Ask questions about a notebook")
    p_ask.add_argument("notebook_id", help="Notebook ID")
    p_ask.add_argument("questions", nargs="+", help="Questions to ask")
    p_ask.add_argument("-o", "--output", default=None, help="Save results as JSON")

    # --- summary ---
    p_summary = sub.add_parser("summary", help="Get notebook summary")
    p_summary.add_argument("notebook_id", help="Notebook ID")

    # --- podcast ---
    p_podcast = sub.add_parser("podcast", help="Generate an audio podcast")
    p_podcast.add_argument("notebook_id", help="Notebook ID")
    p_podcast.add_argument("-o", "--output", default="podcast.mp3", help="Output file path")
    p_podcast.add_argument("--instructions", default="", help="Custom instructions for audio style")

    # --- report ---
    p_report = sub.add_parser("report", help="Generate a written report")
    p_report.add_argument("notebook_id", help="Notebook ID")
    p_report.add_argument("-o", "--output", default="report.txt", help="Output file path")
    p_report.add_argument(
        "--template",
        default="briefing_doc",
        choices=["briefing_doc", "study_guide", "blog_post"],
        help="Report template",
    )

    # --- quiz ---
    p_quiz = sub.add_parser("quiz", help="Generate a quiz")
    p_quiz.add_argument("notebook_id", help="Notebook ID")
    p_quiz.add_argument("-o", "--output", default=None, help="Save quiz as JSON")
    p_quiz.add_argument("-n", "--num-questions", type=int, default=10, help="Number of questions")
    p_quiz.add_argument(
        "--difficulty",
        default="medium",
        choices=["easy", "medium", "hard"],
        help="Quiz difficulty",
    )

    # --- delete ---
    p_delete = sub.add_parser("delete", help="Delete a notebook")
    p_delete.add_argument("notebook_id", help="Notebook ID to delete")

    return parser


async def _run(args: argparse.Namespace) -> None:
    async with ResearchAssistant(profile=args.profile) as ra:
        if args.command == "list":
            projects = await ra.list_projects()
            if not projects:
                print("No notebooks found.")
                return
            for p in projects:
                print(f"  {p['id']}  {p['title']}")

        elif args.command == "create":
            nb_id = await ra.create_project(
                args.title,
                urls=args.url or None,
                files=args.file or None,
            )
            print(f"Created notebook: {nb_id}")

        elif args.command == "ask":
            results = await ra.ask_questions(args.notebook_id, args.questions)
            for r in results:
                print(f"\nQ: {r.question}")
                print(f"A: {r.answer}")
                if r.citations:
                    print(f"   Citations: {', '.join(r.citations)}")
            if args.output:
                await ra.export_research(args.notebook_id, args.questions, args.output)
                print(f"\nResults saved to {args.output}")

        elif args.command == "summary":
            summary = await ra.get_summary(args.notebook_id)
            print(summary)

        elif args.command == "podcast":
            out = await ra.generate_podcast(
                args.notebook_id, args.output, instructions=args.instructions
            )
            print(f"Podcast saved to {out}")

        elif args.command == "report":
            out = await ra.generate_report(
                args.notebook_id, args.output, template=args.template
            )
            print(f"Report saved to {out}")

        elif args.command == "quiz":
            data = await ra.generate_quiz(
                args.notebook_id,
                args.output,
                num_questions=args.num_questions,
                difficulty=args.difficulty,
            )
            if not args.output:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"Quiz saved to {args.output}")

        elif args.command == "delete":
            await ra.delete_project(args.notebook_id)
            print(f"Deleted notebook {args.notebook_id}")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        asyncio.run(_run(args))
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
