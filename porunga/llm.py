import keyring
import os
from langchain.prompts import PromptTemplate
from langchain.output_parsers import XMLOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv
from porunga.utils.exceptions.parse_error import ParseError
from porunga.utils.examples.few_shot_examples import examples
from langchain.chains.llm import LLMChain

dotenv_path = find_dotenv(raise_error_if_not_found=False)
load_dotenv(dotenv_path)

SERVICEID = "PORUNGA_APP"


def suggest_commit_message(diff, x):
    """LLM call to suggest commit message(s)"""

    FEW_SHOT_PROMPT = """
    You are a master at reading git diff messages. Based on the given git diff {diff}, suggest {x} commit messages. Keep the messages clean and concise. Follow these rules:
    1. Messages must be no longer than 60 characters.
    2. Include the general objective of the messages at the beginning:
        - [fix] for bug fixes
        - [feat] for feature addition
        - [ref] for code refactor
        - [docs] for documentation
    3. Return ONLY the suggestions in XML wrapped in a single root element <suggestions>.
    4. Return only the suggestions and no other text
    """

    example_formatter_template = """Diff: {diff}\n
                        Number of messages: {x}\n
                        Suggestions: {suggestions}
                       """

    ex_prompt = PromptTemplate(
        input_variables=["diff", "x", "suggestions"],
        template=example_formatter_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=ex_prompt,
        prefix=FEW_SHOT_PROMPT,
        suffix="Diff: {diff}\nNumber of messages: {x}\n",
        input_variables=["diff", "x"],
        example_separator="\n\n",
    )

    llm = ChatOpenAI(
        temperature=0,
        model_name=keyring.get_password(SERVICEID, "MODEL_NAME")
        or os.environ.get("MODEL_NAME")
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
        print(e)
        return ParseError()
    except Exception as e:
        print(e)
        return Exception
    else:
        return op
