"""Quick-start example: create a notebook, add a URL, and ask a question."""

import asyncio

from research_assistant import ResearchAssistant


async def main():
    async with ResearchAssistant() as ra:
        # 1. Create a notebook with a web source
        nb_id = await ra.create_project(
            "AI Research",
            urls=["https://en.wikipedia.org/wiki/Artificial_intelligence"],
        )
        print(f"Notebook created: {nb_id}")

        # 2. Ask a question
        result = await ra.ask(nb_id, "What are the main branches of AI?")
        print(f"\nQ: {result.question}")
        print(f"A: {result.answer}")

        # 3. Get a summary
        summary = await ra.get_summary(nb_id)
        print(f"\nSummary:\n{summary}")


if __name__ == "__main__":
    asyncio.run(main())
