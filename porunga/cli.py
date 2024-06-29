import subprocess
import click
import os
from InquirerPy import prompt
import keyring

from porunga.utils.parse_messages import parse_messages

SERVICEID = "PORUNGA_APP"


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
def suggest(file_path, num_messages):
    """Suggest commit message.

    Usage:

        >>>    ```bash
            porunga suggest [PATH]
            ```
    """
    from .llm import suggest_commit_message

    openai_api_key = keyring.get_password(SERVICEID, "OPENAI_KEY")
    if openai_api_key is None:
        click.secho("Error: The environment variable OPENAI_KEY is not set.", fg="red")
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

        # Generate initial commit message suggestions
        messages = suggest_commit_message(diff_output, num_messages)
        messages = parse_messages(messages)

        while True:
            # Prepare choices for InquirerPy
            choices = [
                {"name": msg["message"], "value": msg["message"]}
                for msg in messages
                if "message" in msg
            ]

            choices.append(
                {"name": "Regenerate suggestions", "value": "Regenerate suggestions"}
            )

            # Display the messages and get user selection
            questions = [
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
                messages = parse_messages(messages)
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

            edited_answer = prompt(edit_question).get("edited_message")

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
@click.option(
    "--set-venv",
    type=click.Tuple([str, str]),
    multiple=True,
    help="Set environment variables (e.g., --set-env VAR_NAME VAR_VALUE).",
)
def set_env(set_env):
    """Set environment variables and store them securely using keyring."""
    for var, value in set_env:
        keyring.set_password(SERVICEID, var, value)
        click.echo(f"Stored {var} securely.")


if __name__ == "main":
    cli()
