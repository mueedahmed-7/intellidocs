from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from rag.reteriver import Retriever
from rag.promptbuilder import PromptBuilder

class ChatEngine:
    """
    Orchestrates the complete RAG workflow.

    Workflow:
        User Question
              │
              ▼
        Save User Message
              │
              ▼
        Retriever
              │
              ▼
        Prompt Builder
              │
              ▼
           Groq LLM
              │
              ▼
        Save Assistant Message
              │
              ▼
         Final Response
    """

    def __init__(
        self,
        retriever: Retriever,
        prompt_builder: PromptBuilder,
        api_key: str,
        model_name: str = "openai/gpt-oss-120b",
        temperature: float = 0.2,
    ):
        """
        Initialize Chat Engine.

        Args:
            retriever: Retriever instance.
            prompt_builder: PromptBuilder instance.
            api_key: Groq API key.
            model_name: Groq model.
            temperature: LLM temperature.
        """

        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm = ChatGroq(
            api_key=api_key,
            model=model_name,
            temperature=temperature,
            reasoning_effort="low",
            reasoning_format="hidden",
        )

    def chat(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:
        """
        Complete RAG pipeline.

        Args:
            question: User question.
            top_k: Number of retrieved chunks.

        Returns:
            LLM response.
        """
        # -----------------------------
        # Retrieve relevant chunks
        # -----------------------------

        retrieved_chunks = self.retriever.retrieve(
                        query=question,
                        top_k=top_k,
                    )
            
        # -----------------------------
        # Build prompt
        # -----------------------------
        prompt = self.prompt_builder.build_prompt(
            query=question,
            retrieved_chunks=retrieved_chunks,
        )

        # -----------------------------
        # Send prompt to Groq
        # -----------------------------
        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        )

        answer = response.content

        
        
        return {
            "answer": answer,
        }