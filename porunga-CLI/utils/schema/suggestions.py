from typing import List
from langchain_core.pydantic_v1 import BaseModel


class CommitMessage(BaseModel):
    message: str


class CommitMessageSuggestions(BaseModel):
    suggestions: List[str]
