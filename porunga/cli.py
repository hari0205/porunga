import subprocess
import click
from InquirerPy import prompt

from porunga.utils.parse_messages import parse_messages


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

    from .llm import suggest_commit_message

    """Suggest commit message.

    Usage:

        >>>    ```bash
            porunga suggest [PATH]
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
            messages = suggest_commit_message(diff_output, num_messages)

            messages = parse_messages(messages)

            # Prepare choices for InquirerPy
            choices = [
                {"name": msg["message"], "value": msg["message"]}
                for msg in messages
                if "message" in msg
            ]

            # Display the messages and get user selection
            questions = [
                {
                    "type": "list",
                    "message": "Please select a commit message:",
                    "choices": choices,
                }
            ]
            answers = prompt(questions)

            selected_message = answers[0]

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

            click.echo(f"You selected: {edited_answer}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running git diff: {e}")


if __name__ == "main":
    cli()
