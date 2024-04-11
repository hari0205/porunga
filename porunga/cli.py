import subprocess
import click


class CustomGroup(click.Group):
    def parse_args(self, ctx, args):
        if args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0,".")
        super(CustomGroup, self).parse_args(ctx, args)


@click.group()
def cli():
    pass

@cli.command("show-diff")
@click.argument('file_path', type=click.Path(exists=True),required=False)
def show_diff(file_path):
    """Show the git diff.
    
    Usage: 
    
    ```bash
    porunga show-diff [PATH]
    ```
    """
    try:
        # Run the git diff command and capture its output
        diff_process = subprocess.Popen(['git', 'diff', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Print the git diff output
        
        # Capture the stdout and stderr streams
        diff_output_bytes, _ = diff_process.communicate()

        # Decode the byte output to string using UTF-8 encoding
        diff_output = diff_output_bytes.decode('utf-8')
        
        # Check for length of differences
        if len(diff_output) == 0:
            click.echo("No difference detected. Start making changes to files")
            return
        else:
            click.echo(diff_output)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running git diff: {e}")

if __name__ == "main":
    cli()