"""Batch research: ask multiple questions and export results as JSON."""

import asyncio

from research_assistant import ResearchAssistant

QUESTIONS = [
    "What are the key benefits of renewable energy?",
    "What are the main challenges in transitioning to renewable energy?",
    "Which countries lead in renewable energy adoption?",
    "What role does solar energy play compared to wind energy?",
]


async def main():
    async with ResearchAssistant() as ra:
        # Create notebook
        nb_id = await ra.create_project(
            "Renewable Energy Research",
            urls=["https://en.wikipedia.org/wiki/Renewable_energy"],
        )
        print(f"Notebook: {nb_id}")

        # Ask all questions and export
        results = await ra.ask_questions(nb_id, QUESTIONS)
        for r in results:
            print(f"\nQ: {r.question}")
            print(f"A: {r.answer[:200]}...")

        # Save full results
        output = await ra.export_research(nb_id, QUESTIONS, "research_results.json")
        print(f"\nFull results exported to: {output}")


if __name__ == "__main__":
    asyncio.run(main())
