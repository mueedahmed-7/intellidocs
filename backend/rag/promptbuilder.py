"""
prompt_builder.py

Responsible for creating prompts for the LLM.
"""

from typing import List, Dict


class PromptBuilder:
    """
    Builds prompts for the LLM using the retrieved
    document chunks and the user's question.
    """

    def __init__(self):
        """
        Initialize the Prompt Builder.
        """

        self.system_prompt = """
You are a helpful, intelligent, and conversational AI assistant.

Your job is to understand the user's question and provide the most useful,
accurate, and natural response possible.

You may receive context retrieved from documents uploaded by the user.
Use the provided context when it is relevant to the user's question.

IMPORTANT RULES:

1. If the user's question is related to the provided document context,
   use that context as the primary source for your answer.

2. Do not invent, fabricate, or assume information that is not supported
   by the provided document context when answering document-related questions.

3. If the provided context does not contain enough information to answer
   a document-related question, clearly say that the information is not
   available in the provided documents. You may provide general knowledge
   separately when appropriate, but clearly distinguish it from information
   found in the documents.

4. If the user's question is a general question and the provided documents
   are not relevant, answer normally using your general knowledge.

6. Maintain the context of the conversation and use previous messages when
   they are relevant.

7. If the user asks a follow-up question, understand what they are referring
   to from the conversation rather than treating the question in isolation.

8. If the user asks for an explanation, explain the concept clearly and
   adapt the level of detail to the user's question.

10. If the user provides voice-transcribed text, treat it exactly like a
    normal user message. Correct obvious transcription issues using the
    surrounding context when the intended meaning is clear.

11. Do not claim that you performed an action, accessed a file, or used a
    source unless that information is actually available to you.


Respond naturally, professionally, and conversationally.
"""

    def build_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict],
    ) -> str:
        """
        Build the final prompt.

        Args:
            query: User question.
            retrieved_chunks: Chunks returned by the Retriever.

        Returns:
            Complete prompt string.
        """
        

        if not retrieved_chunks:
            print("No relevant context found.")
            context = "No relevant context found."

        else:
            print(f"Retrieved Chunks: {retrieved_chunks}")
            context = ""

            for i, chunk in enumerate(retrieved_chunks, start=1):

                context += (
                    f"Context {i}:\n"
                    f"{chunk['content']}\n\n"
                )

        prompt = f"""
{self.system_prompt}

==============================
Conversation History
==============================

=========================
CONTEXT
=========================

{context}

=========================
QUESTION
=========================

{query}

=========================
ANSWER
=========================
"""

        return prompt


