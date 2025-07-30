
import click
from ebix.commands.init_command import run_init

@click.group()
def cli():
    pass

@cli.command()
def init():
    run_init()
