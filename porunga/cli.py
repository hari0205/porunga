import subprocess
from typing import Annotated, Any, Dict, List, Optional, Union
import click
from InquirerPy import prompt
import keyring
from porunga.utils.parse_messages import parse_messages

SERVICEID = "PORUNGA_APP"

Choice = Annotated[List[Union[str, None]], "Suggestions for user choice"]


class CustomGroup(click.Group):
    def parse_args(self, ctx, args):
        if args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, ".")
        super(CustomGroup, self).parse_args(ctx, args)


@click.group()
def cli():
    pass


@cli.command("show-diff")
@click.argument("file_path", type=click.Path(exists=True))
def show_diff(file_path):
    """Show the git diff.

    Usage:

        >>>    ```bash
            porunga show-diff [PATH]
            ```
    """
    try:
        # Run the git diff command and capture its output
        diff_process = subprocess.Popen(
            ["git", "diff", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Capture the stdout and stderr streams
        diff_output_bytes, _ = diff_process.communicate()

        # Decode the byte output to string using UTF-8 encoding
        diff_output = diff_output_bytes.decode("utf-8")

        # Check for length of differences
        if len(diff_output) == 0:
            click.echo("No difference detected. Start making changes to files")
            return
        else:
            click.echo(diff_output)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running git diff: {e}")


@cli.command("suggest")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--num-messages",
    "-n",
    default=3,
    help="Number of suggested commit messages to display.",
)
def suggest(file_path: str, num_messages: Optional[int]):
    """Suggest commit message.

    Usage:

        >>>    ```bash
            porunga suggest [PATH]
            ```
    """
    from .llm import suggest_commit_message

    openai_api_key = keyring.get_password(SERVICEID, "OPENAI_API_KEY")
    if openai_api_key is None:
        click.secho(
            "Error: The environment variable OPENAI_API_KEY is not set. Please set the key using the setenv command.",
            fg="red",
        )
        return

    try:
        # Run the git diff command and capture its output
        diff_process = subprocess.Popen(
            ["git", "diff", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Capture the stdout and stderr streams
        diff_output_bytes, _ = diff_process.communicate()

        # Decode the byte output to string using UTF-8 encoding
        diff_output = diff_output_bytes.decode("utf-8")
        # Check for length of differences
        if len(diff_output) == 0:
            click.echo("No difference detected. Start making changes to files")
            return

        # Get the mode
        mode: Union[str, None] = (
            keyring.get_password(SERVICEID, "PORUNGA_MODE") or "precise"
        )
        model: Union[str, None] = (
            keyring.get_password(SERVICEID, "PORUNGA_MODEL_NAME") or "gpt-4o"
        )

        # If diff is too large (saving api costs)
        if model.startswith("gpt-4"):
            match mode:
                # If you care about cost
                case "cost":
                    if len(diff_output) > 16000:
                        diff_output = diff_output[:16000]

                # If you care about precision
                case "precise":
                    if len(diff_output) > 60000:
                        diff_output = diff_output[:60000]

                case _:
                    if len(diff_output) > 30000:
                        diff_output = diff_output[:30000]

        elif model.startswith("gpt-3"):
            match (mode):
                # If you care about cost
                case "cost":
                    if len(diff_output) > 3000:
                        diff_output = diff_output[:3000]

                # If you care about precision
                case "precise":
                    if len(diff_output) > 7000:
                        diff_output = diff_output[:7000]

                case _:
                    if len(diff_output) > 5000:
                        diff_output = diff_output[:5000]

        # Generate initial commit message suggestions
        messages = suggest_commit_message(diff_output, num_messages)
        if isinstance(messages, (Exception)):
            click.secho(
                f"An error occurred when trying to generate suggestions {messages}",
                err=True,
                color=True,
                fg="red",
            )
            return
        messages = parse_messages(messages=messages)
        if isinstance(messages, (Exception)):
            click.secho(
                "An error occurred when trying to parse suggestions", err=True, fg="red"
            )
            return

        while True:
            # Prepare choices for InquirerPy
            choices: Choice = [
                {"name": msg["message"], "value": msg["message"]}
                for msg in messages
                if "message" in msg
            ]

            choices.append(
                {"name": "Regenerate suggestions", "value": "Regenerate suggestions"}
            )

            # Display the messages and get user selection
            questions: List[Dict[str, Any]] = [
                {
                    "type": "list",
                    "message": "Please choose a selection",
                    "choices": choices,
                }
            ]
            answers = prompt(questions)

            selected_message = answers[0]

            if selected_message == "Regenerate suggestions":
                messages = suggest_commit_message(diff_output, num_messages)
                if isinstance(messages, (Exception)):
                    click.secho(
                        f"An error occurred when trying to generate suggestions {messages}",
                        err=True,
                        fg="red",
                    )
                    return
                messages = parse_messages(messages)
                if isinstance(messages, (Exception)):
                    click.secho(
                        "An error occurred when trying to parse suggestions",
                        err=True,
                        fg="red",
                    )
                    return
                continue

            # Prompt user to edit the selected message
            edit_question = [
                {
                    "type": "input",
                    "name": "edited_message",
                    "message": "Edit the commit message:",
                    "default": selected_message,
                }
            ]

            edited_answer: Union[str, List[Any], bool, None] = prompt(
                edit_question
            ).get("edited_message")

            if click.confirm(
                f"Do you want to commit and push with the following message? {edited_answer}",
                default=True,
            ):
                # Commit to git and push to git
                subprocess.run(["git", "add", file_path])
                subprocess.run(["git", "commit", "-m", edited_answer])

                # push to the remote repository
                subprocess.run(["git", "push"])
                break  # Exit the loop after successful commit and push
            else:
                click.echo("Let's try again.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running git diff: {e}")


@cli.command("set-env")
@click.argument(
    "env_vars",
    nargs=-1,
)
def setenv(env_vars):
    """Set environment variables and store them securely.

    Usage:

        >>>    ```bash
            porunga setenv VAR_NAME=VAR_VALUE [VAR_NAME=VAR_VALUE...]
            ```
    """
    for env_var in env_vars:
        try:
            # Split each env_var by '=' to separate variable name and value
            var, value = env_var.split("=", 1)
            keyring.set_password(SERVICEID, var, value)
            click.echo(f"Stored {var} securely.")
        except ValueError:
            click.secho(f"Invalid format for environment variable: {env_var}", fg="red")


if __name__ == "main":
    cli()
