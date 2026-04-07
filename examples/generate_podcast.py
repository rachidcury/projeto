"""Generate a podcast from multiple sources."""

import asyncio

from research_assistant import ResearchAssistant


async def main():
    async with ResearchAssistant() as ra:
        # Create notebook with multiple sources
        nb_id = await ra.create_project(
            "Climate Change Overview",
            urls=[
                "https://en.wikipedia.org/wiki/Climate_change",
                "https://en.wikipedia.org/wiki/Paris_Agreement",
            ],
        )
        print(f"Notebook created: {nb_id}")

        # Generate a podcast-style audio overview
        output = await ra.generate_podcast(
            nb_id,
            "climate_podcast.mp3",
            instructions="Make it conversational and engaging, suitable for a general audience.",
        )
        print(f"Podcast saved to: {output}")


if __name__ == "__main__":
    asyncio.run(main())
