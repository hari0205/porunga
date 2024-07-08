# Porunga - A CLI tool to suggest commit messages

A simple tool to suggest commit messages.

![Porunga Usage](./assets/porunga-use-ezgif.com-speed.gif)

## Prerequisites

- Make sure you are using Python version >3.11
- This tool requires OPENAI API Key to work. Please see [this](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key)

## Installation

`pip install porunga`

## Usage

- To see a list of commands availabe to use:

```sh
porunga --help
```

- To get information about a specific command , use:

```sh
porunga COMMAND --help
```

Example:

```sh
porunga set-env --help
```

- To set env variables, it is **recommended** to use set-env command

```sh
porunga set-env OPENAI_API_KEY=sk-....
```

You can set the following env variables that this tool uses:

- `OPENAI_API_KEY` : API key from OpenAI
- `PORUNGA_MODEL_NAME` : Open AI Model to use
- `PORUNGA_MODE` : Either `cost` or `precise` or `balanced`. It is **recommended** to precise for the best results

> This CLI tool uses gpt-4o by default, which is recommended.

- To get suggestions

```sh
porunga suggest FILEPATH -n 2
```

This generates 2 suggestions for the particular uncommitted changes.

## Warning

The results generated by this tool can be unpredictable and may produce inconsistent results. Users are advised to review and verify the suggestions before using them.
