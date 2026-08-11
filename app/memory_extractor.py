from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field


class MemoryDecision(BaseModel):
    should_save: bool = Field(
        description="Whether this message contains useful long-term information about the user."
    )
    memory: str | None = Field(
        default=None,
        description="A concise statement of the user information worth remembering.",
    )


llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

memory_llm = llm.with_structured_output(MemoryDecision)

memory_prompt = ChatPromptTemplate.from_template("""
You are a memory extraction system.

Decide whether the user's message contains useful long-term information
about the user.

SAVE information such as:
- User preferences
- User interests
- User goals
- User skills
- Technology preferences
- Important user-specific facts

DO NOT SAVE:
- Questions
- Greetings
- Jokes
- Temporary requests
- General knowledge
- Information that is not about the user

If the information should be saved, rewrite it as one concise statement.

User message:
{message}
""")


async def extract_memory(message: str) -> MemoryDecision:
    prompt = memory_prompt.invoke({"message": message})

    return await memory_llm.ainvoke(prompt)
