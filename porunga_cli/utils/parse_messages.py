from typing import Any, Union, Dict


def parse_messages(messages: Union[Dict, Any, None]):
    if isinstance(messages, dict):
        return messages["suggestions"]
