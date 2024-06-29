from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import XMLOutputParser
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv


dotenv_path = find_dotenv(raise_error_if_not_found=False)
load_dotenv(dotenv_path)


def suggest_commit_message(diff, x):
    """LLM call to suggest commit message(s)"""

    PROMPT = """
    You are a master at reading git diff messages. Based on the given git diff {diff}, suggest {x} commit messages. Keep the messages clean and concise. Follow the following rules
    1. Messages must no longer be more than 60 characters
    2. Include the general objective of the messages in the beginning of message
        - [fix] for bug fixes
        - [feat] for feature addition
        - [ref] for Code refactor
        - [docs] for documentation
    3. Return your suggestions in XML format, wrapped in a single root element <suggestions> 
    """

    prompt_message = PromptTemplate.from_template(PROMPT)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    chain = prompt_message | llm | XMLOutputParser()
    op = chain.invoke({"diff": diff, "x": x})
    return op
