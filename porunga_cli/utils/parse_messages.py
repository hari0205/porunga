def parse_messages(messages):
    if isinstance(messages, dict):
        return messages["suggestions"]
