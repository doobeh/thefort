"""
    sample.py
    ~~~~~~~~~

    Loads the entire site with fake data, to let us really test the UI
    and flow of everything.
"""
import click
from flask.cli import AppGroup
from thefort.database import db
from flask import current_app
import os
import random
from datetime import datetime

sample_cli = AppGroup("sample")


@sample_cli.command('load')
def load():
    proceed = click.prompt('This process wipes existing data (if any) and loads with fake data\n'
                 'Are you sure?', confirmation_prompt=True, default=False)
    if not proceed:
        click.Abort('Exiting')
