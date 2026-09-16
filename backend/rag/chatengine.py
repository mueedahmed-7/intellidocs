from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import re

from backend.rag.promptbuilder import PromptBuilder
from backend.rag.reteriver import Retriever


class ChatEngine:
    DOCUMENT_REFERENCE_PATTERN = re.compile(
        r"\b(this|my|the|an|a)\s+(document|pdf|file|report|voucher)\b|"
        r"\b(uploaded|selected)\s+(document|pdf|file|report|voucher)\b|"
        r"\baccording to\b|\bin the (document|pdf|file|report|voucher)\b|"
        r"\bfrom the (document|pdf|file|report|voucher)\b|"
        r"\bsummarize (this|my|the)?\s*(document|pdf|file|report|voucher)\b",
        re.IGNORECASE,
    )
    # These are common general-knowledge topics, not document routing keywords.
    # They prevent an unrelated selected file from taking over a normal AI chat.
    GENERIC_KNOWLEDGE_PATTERN = re.compile(
        r"\b(ai|artificial intelligence|machine learning|deep learning|python|cnn|"
        r"logistic regression|sorting algorithm|fyp|capital of france|write an email)\b",
        re.IGNORECASE,
    )
    # A small set of factual fields commonly asked about in uploaded paperwork.
    DOCUMENT_FACT_PATTERN = re.compile(
        r"\b(voucher|invoice|receipt|statement|form|fee|due date|deadline|amount|"
        r"voucher number|reference number|page|signed|signature|roadmap|semester|"
        r"course|courses|subject|subjects|curriculum|prerequisite|prerequisites|"
        r"credit hours|elective|program|degree|module|schedule)\b",
        re.IGNORECASE,
    )
    DOCUMENT_FOLLOW_UP_PATTERN = re.compile(
        r"\b(its|it|that|this|there|the amount|the date|the deadline|the second one)\b",
        re.IGNORECASE,
    )
    def __init__(self, retriever: Retriever, prompt_builder: PromptBuilder, api_key: str,
                 model_name: str = "openai/gpt-oss-120b", temperature: float = 0.2):
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm = ChatGroq(api_key=api_key, model=model_name, temperature=temperature,
                            reasoning_effort="low", reasoning_format="hidden")

    @classmethod
    def is_explicit_document_request(cls, question: str) -> bool:
        return bool(cls.DOCUMENT_REFERENCE_PATTERN.search(question))

    @classmethod
    def is_document_follow_up(cls, question: str, history_messages: list[dict]) -> bool:
        """Recognize a short reference only when the immediately prior answer was sourced."""
        last_assistant = next(
            (item for item in reversed(history_messages) if item.get("role") == "assistant"),
            None,
        )
        return bool(
            last_assistant
            and last_assistant.get("sources")
            and cls.DOCUMENT_FOLLOW_UP_PATTERN.search(question)
        )

    @classmethod
    def should_use_document_mode(
        cls,
        question: str,
        has_selected_documents: bool,
        history_messages: list[dict],
    ) -> bool:
        """Choose RAG per message; selected documents provide scope, never intent alone."""
        if cls.is_explicit_document_request(question):
            return True
        if cls.GENERIC_KNOWLEDGE_PATTERN.search(question):
            return False
        # Selecting one or more documents is an explicit request to ask those
        # documents. This works for every supported file type and avoids
        # relying on document-specific keyword lists (for example, a roadmap
        # versus a contract). Clear general-knowledge prompts still use chat.
        if has_selected_documents:
            # Do not let a vague "it/that" after a general answer switch the
            # conversation back to RAG merely because a document is selected.
            if cls.DOCUMENT_FOLLOW_UP_PATTERN.search(question):
                return cls.is_document_follow_up(question, history_messages)
            return True
        return bool(
            cls.DOCUMENT_FACT_PATTERN.search(question)
            or cls.is_document_follow_up(question, history_messages)
        )

    def _invoke(self, prompt: str) -> str:
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
        except Exception as error:
            raise RuntimeError("The language model is temporarily unavailable. Please try again.") from error
        return response.content

    def chat(self, question: str, top_k: int = 5, user_id: str | None = None,
             document_ids: list[str] | None = None, conversation_history: str = "",
             document_mode: bool = True) -> dict:
        """Use strict RAG in document mode, otherwise provide general AI chat."""
        retrieved_chunks = []
        if document_mode and document_ids:
            retrieved_chunks = self.retriever.retrieve(
                query=question, top_k=top_k, user_id=user_id, document_ids=document_ids
            )
        if retrieved_chunks:
            prompt = self.prompt_builder.build_prompt(question, retrieved_chunks, conversation_history)
            return {
                "answer": self._invoke(prompt),
                "sources": [
                    {"document_id": item.document_id, "filename": item.filename,
                     "chunk_index": item.chunk_index, "page": item.page, "distance": item.distance}
                    for item in retrieved_chunks
                ],
            }
        if document_mode:
            return {
                "answer": "I couldn't find that information in the selected documents.",
                "sources": [],
            }
        return {"answer": self._invoke(self.prompt_builder.build_generic_prompt(question, conversation_history)), "sources": []}
