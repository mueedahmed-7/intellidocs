"""Grounded prompt construction for managed user documents."""

from backend.rag.reteriver import RetrievalResult


class PromptBuilder:
    system_prompt = """You answer using only the retrieved document context as factual evidence.
Conversation history helps interpret follow-up questions but is not evidence.
Do not invent facts not supported by the sources. If the sources are insufficient,
say so clearly. Keep answers concise and do not claim a source supports something it does not."""

    def build_prompt(
        self,
        query: str,
        retrieved_chunks: list[RetrievalResult],
        conversation_history: str = "",
    ) -> str:
        history = conversation_history or "No previous conversation."
        context_parts = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            page = f"Page: {chunk.page}\n" if chunk.page is not None else ""
            context_parts.append(
                f"[SOURCE {index}]\nDocument: {chunk.filename}\nChunk: {chunk.chunk_index}\n"
                f"{page}Content:\n{chunk.content[:4000]}"
            )
        context = "\n\n".join(context_parts)
        return (
            f"{self.system_prompt}\n\nRECENT CONVERSATION (not evidence):\n{history}\n\n"
            f"DOCUMENT EVIDENCE:\n{context}\n\nQUESTION:\n{query}\n\nANSWER:"
        )

    def build_generic_prompt(self, query: str, conversation_history: str = "") -> str:
        history = conversation_history or "No previous conversation."
        return (
            "You are a helpful general-purpose AI assistant. Answer clearly and accurately. "
            "Use recent conversation only as conversational context.\n\n"
            f"RECENT CONVERSATION:\n{history}\n\nQUESTION:\n{query}\n\nANSWER:"
        )
