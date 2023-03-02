"""Chain that carries on a conversation and calls an LLM."""
from typing import Dict, List, Any

from pydantic import BaseModel, Extra, Field, root_validator

from langchain.chat.base import BaseChatChain
from langchain.chains.conversation.prompt import PROMPT
from langchain.chains.llm import LLMChain
from langchain.prompts.base import BasePromptTemplate
from langchain.chat.memory import SimpleChatMemory
from langchain.chat_models.base import BaseChat
from langchain.schema import ChatMessage


class ConversationChain(BaseChatChain, BaseModel):
    """Chain to have a conversation and load context from memory.

    Example:
        .. code-block:: python

            from langchain import ConversationChain, OpenAI
            conversation = ConversationChain(llm=OpenAI())
    """

    model: BaseChat
    memory: SimpleChatMemory = Field(default_factory=SimpleChatMemory)
    """Default memory store."""
    prompt: BasePromptTemplate = PROMPT
    """Default conversation prompt to use."""
    input_key: str = "input"  #: :meta private:
    output_key: str = "response"  #: :meta private:
    starter_messages: List[ChatMessage] = Field(default_factory=list)

    @classmethod
    def from_model(cls, model: BaseModel, **kwargs: Any):
        """From model. Future proofing."""
        return cls(model=model, **kwargs)

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        new_message = ChatMessage(text = inputs[self.input_key], role=self.human_prefix)
        messages = self.starter_messages + self.memory.messages + [new_message]
        output = self.model.run(messages)
        return {self.output_key: output.text}



    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Use this since so some prompt vars come from history."""
        return [self.input_key]

