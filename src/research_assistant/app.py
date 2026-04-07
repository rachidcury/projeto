"""Core research assistant logic wrapping notebooklm-py."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from notebooklm import NotebookLMClient, RPCError


@dataclass
class ResearchResult:
    """Container for a research Q&A result."""

    question: str
    answer: str
    citations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"question": self.question, "answer": self.answer, "citations": self.citations}


class ResearchAssistant:
    """High-level helper that orchestrates NotebookLM workflows.

    Usage::

        async with ResearchAssistant() as ra:
            nb_id = await ra.create_project("AI Safety", urls=["https://example.com"])
            results = await ra.ask_questions(nb_id, ["What are the key risks?"])
            await ra.generate_podcast(nb_id, "podcast.mp3")
    """

    def __init__(self, profile: str | None = None):
        self._profile = profile
        self._client: NotebookLMClient | None = None

    async def __aenter__(self) -> ResearchAssistant:
        if self._profile:
            self._client = await NotebookLMClient.from_storage(profile=self._profile)
        else:
            self._client = await NotebookLMClient.from_storage()
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc):
        if self._client:
            await self._client.__aexit__(*exc)
            self._client = None

    @property
    def client(self) -> NotebookLMClient:
        if self._client is None:
            raise RuntimeError("ResearchAssistant must be used as an async context manager")
        return self._client

    # ------------------------------------------------------------------
    # Notebook helpers
    # ------------------------------------------------------------------

    async def create_project(
        self,
        title: str,
        *,
        urls: Sequence[str] | None = None,
        files: Sequence[str | Path] | None = None,
        texts: Sequence[tuple[str, str]] | None = None,
    ) -> str:
        """Create a notebook and populate it with sources.

        Args:
            title: Notebook title.
            urls: Web page or YouTube URLs to add.
            files: Local file paths (PDF, DOCX, TXT, etc.) to upload.
            texts: Pairs of (title, content) for inline text sources.

        Returns:
            The notebook ID.
        """
        nb = await self.client.notebooks.create(title)
        nb_id = nb.id

        tasks: list = []
        if urls:
            for url in urls:
                tasks.append(self.client.sources.add_url(nb_id, url, wait=True))
        if files:
            for fp in files:
                p = Path(fp)
                mime = _guess_mime(p)
                tasks.append(self.client.sources.add_file(nb_id, str(p), mime))
        if texts:
            for t_title, t_content in texts:
                tasks.append(self.client.sources.add_text(nb_id, t_title, t_content))

        if tasks:
            await asyncio.gather(*tasks)

        return nb_id

    async def list_projects(self) -> list[dict]:
        """Return a simplified list of notebooks."""
        notebooks = await self.client.notebooks.list()
        return [{"id": nb.id, "title": nb.title} for nb in notebooks]

    async def delete_project(self, notebook_id: str) -> None:
        """Delete a notebook."""
        await self.client.notebooks.delete(notebook_id)

    # ------------------------------------------------------------------
    # Research / Q&A
    # ------------------------------------------------------------------

    async def ask(self, notebook_id: str, question: str) -> ResearchResult:
        """Ask a single question against notebook sources."""
        result = await self.client.chat.ask(notebook_id, question)
        citations = []
        if hasattr(result, "citations") and result.citations:
            citations = [c.text if hasattr(c, "text") else str(c) for c in result.citations]
        return ResearchResult(question=question, answer=result.answer, citations=citations)

    async def ask_questions(
        self, notebook_id: str, questions: Sequence[str]
    ) -> list[ResearchResult]:
        """Ask multiple questions sequentially and return all results."""
        results = []
        for q in questions:
            r = await self.ask(notebook_id, q)
            results.append(r)
        return results

    async def get_summary(self, notebook_id: str) -> str:
        """Get an AI-generated summary of the notebook."""
        return await self.client.notebooks.get_summary(notebook_id)

    # ------------------------------------------------------------------
    # Artifact generation
    # ------------------------------------------------------------------

    async def generate_podcast(
        self,
        notebook_id: str,
        output_path: str | Path,
        *,
        instructions: str = "",
    ) -> Path:
        """Generate an audio overview and download it."""
        status = await self.client.artifacts.generate_audio(
            notebook_id, instructions=instructions
        )
        await self.client.artifacts.wait_for_completion(notebook_id, status.task_id)
        out = Path(output_path)
        await self.client.artifacts.download_audio(notebook_id, str(out))
        return out

    async def generate_report(
        self,
        notebook_id: str,
        output_path: str | Path,
        *,
        template: str = "briefing_doc",
    ) -> Path:
        """Generate a written report and save it."""
        status = await self.client.artifacts.generate_report(
            notebook_id, template=template
        )
        await self.client.artifacts.wait_for_completion(notebook_id, status.task_id)
        out = Path(output_path)
        reports = await self.client.artifacts.list_reports(notebook_id)
        if reports:
            out.write_text(reports[0].content, encoding="utf-8")
        return out

    async def generate_quiz(
        self,
        notebook_id: str,
        output_path: str | Path | None = None,
        *,
        num_questions: int = 10,
        difficulty: str = "medium",
    ) -> list[dict]:
        """Generate a quiz and optionally save as JSON."""
        status = await self.client.artifacts.generate_quiz(
            notebook_id, num_questions=num_questions, difficulty=difficulty
        )
        await self.client.artifacts.wait_for_completion(notebook_id, status.task_id)
        quizzes = await self.client.artifacts.list_quizzes(notebook_id)
        data = []
        if quizzes:
            for q in quizzes:
                data.append({"question": q.question, "options": q.options, "answer": q.answer}
                            if hasattr(q, "question") else {"raw": str(q)})
        if output_path:
            Path(output_path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return data

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    async def export_research(
        self,
        notebook_id: str,
        questions: Sequence[str],
        output_path: str | Path,
    ) -> Path:
        """Run Q&A and export results as JSON."""
        results = await self.ask_questions(notebook_id, questions)
        out = Path(output_path)
        out.write_text(
            json.dumps([r.as_dict() for r in results], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return out


def _guess_mime(path: Path) -> str:
    """Return a MIME type for common file extensions."""
    mime_map = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".csv": "text/csv",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".mp4": "video/mp4",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    return mime_map.get(path.suffix.lower(), "application/octet-stream")
