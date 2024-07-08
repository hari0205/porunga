from typing import Any, Dict, Optional
import keyring
import os
from langchain.prompts import PromptTemplate
from langchain.output_parsers import XMLOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import FewShotPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv
from .utils.exceptions.parse_error import ParseError
from .utils.examples.few_shot_examples import examples

# from langchain.chains.llm import LLMChain

dotenv_path = find_dotenv(raise_error_if_not_found=False)
load_dotenv(dotenv_path)

SERVICEID = "PORUNGA_APP"


def suggest_commit_message(
    diff: str, x: Optional[int] = 3
) -> Dict[Any, Any] | ParseError | Exception:
    """LLM call to suggest commit message(s)"""

    FEW_SHOT_PROMPT = """
Task: Based on the provided git diff, suggest concise commit messages.

Context: You are analyzing git diff messages to create clear and concise commit messages for a code repository. The commit messages should reflect the changes made, be easy to understand, and follow a standard format.

Persona: You are a meticulous and experienced software developer who values clarity and precision in commit messages. You aim to create messages that are helpful for the whole development team.

Example:
git diff: diff --git a/file1.txt b/file1.txt
          index 83db48f..e8a56b3 100644
          --- a/file1.txt
          +++ b/file1.txt
          @@ -1 +1,2 @@
          +Added new feature

<suggestions>
    <message>[feat] Add new feature to file1</message>
</suggestions>

Tone: Professional and precise.

Format:
1. Messages must be no longer than 60 characters.
2. Start with the type of change:
    - [fix] for bug fixes
    - [feat] for new features
    - [ref] for refactoring
    - [docs] for documentation
3. Return ONLY the suggestions in XML wrapped in a single root element <suggestions>.

Remember, return only the XML with the suggestions. No other text or explanation is allowed.
"""

    example_formatter_template: str = """Diff: {diff}\n
                        Number of messages: {x}\n
                        Suggestions: {suggestions}
                       """

    ex_prompt: PromptTemplate = PromptTemplate(
        input_variables=["diff", "x", "suggestions"],
        template=example_formatter_template,
    )

    few_shot_prompt: FewShotPromptTemplate = FewShotPromptTemplate(
        examples=examples,
        example_prompt=ex_prompt,
        prefix=FEW_SHOT_PROMPT,
        suffix="Diff: {diff}\nNumber of messages: {x}\n",
        input_variables=["diff", "x"],
        example_separator="\n\n",
    )

    llm = ChatOpenAI(
        temperature=0,
        model_name=keyring.get_password(SERVICEID, "PORUNGA_MODEL_NAME")
        or os.environ.get("MODEL_NAME")
        or keyring.get_password(SERVICEID, "PORUNGA_MODE")
        or "gpt-4o",
        api_key=keyring.get_password(SERVICEID, "OPENAI_API_KEY"),
        timeout=1500,
        max_retries=3,
        request_timeout=120,
        max_tokens=1500,
    )
    try:
        # Method 1 (Legacy)
        # chain = LLMChain(
        #     llm=llm, prompt=few_shot_prompt, output_parser=XMLOutputParser()
        # )
        # res = chain.invoke({"diff": diff, "x": x})
        # print(res.get("text"))

        # Method 2 (Shortcut)
        # res = llm.invoke(few_shot_prompt.format(diff=diff, x=x))
        # print(res)

        # Method 3 (Recommended)
        chain = few_shot_prompt | llm | XMLOutputParser()
        op = chain.invoke({"diff": diff, "x": x})
    except OutputParserException as e:
        # Custom Error class
        return ParseError(e.args[0])
    except Exception as e:
        return Exception(e.args[0])
    else:
        return op
