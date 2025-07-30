import click
import subprocess
from pathlib import Path
from tellabot.utils import copy_template
import webbrowser
import time
import sys
import shutil
from tellabot import __version__  # import your version here

@click.group()
@click.version_option(version=__version__, prog_name="tellabot")
def cli():
    pass

@cli.command()
@click.argument('project_name')
def init(project_name):
    """Scaffold a new bot project."""
    target = Path.cwd() / project_name
    if target.exists() and any(target.iterdir()):
        click.echo(f"❌ Directory '{project_name}' already exists and is not empty.")
        return
    src = Path(__file__).parent / "templates" / "main_template"
    copy_template(src, target)
    click.echo(f"✅ Project '{project_name}' created at {target}")

@cli.command()
def install():
    """Install required Python packages using pip."""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        click.echo("❌ No requirements.txt found in the current directory.")
        return
    click.echo("📦 Installing dependencies...")
    try:
        subprocess.check_call(["pip", "install", "-r", str(req_file)])
        click.echo("✅ All dependencies installed.")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Installation failed: {e}")

@cli.command()
def run():
    """
    Run both the Telegram bot and admin panel,
    then open the admin panel in the default web browser.
    """
    bot_script = Path.cwd() / "run.py"  # The unified run script

    if not bot_script.exists():
        click.echo(f"❌ Run script not found at {bot_script}")
        return

    click.echo("🚀 Starting bot and admin panel via run.py...")

    # Start run.py as subprocess
    proc = subprocess.Popen([sys.executable, str(bot_script)])

    # Give some time for the server to start
    time.sleep(3)

    url = "http://localhost:5000"
    click.echo(f"🌐 Opening admin panel in browser at {url}")
    webbrowser.open(url)

    try:
        proc.wait()
    except KeyboardInterrupt:
        click.echo("\n🛑 Stopping the process...")
        proc.terminate()
        click.echo("✅ Stopped the bot and admin panel.")

@cli.command()
def update():
    """
    Update core framework files in the current project.
    Only overwrites boilerplate files and backs up old ones.
    """
    project_root = Path.cwd()
    template_root = Path(__file__).parent / "templates" / "main_template"

    # List of core files to update
    core_files = [
        "app/__init__.py",
        "app/bot.py",
        "run.py"
    ]

    click.echo("🔄 Updating core framework files...")

    for file in core_files:
        src = template_root / file
        dst = project_root / file

        if not src.exists():
            click.echo(f"⚠️  Template file missing: {file}")
            continue

        # Backup old file
        if dst.exists():
            backup_path = dst.with_suffix(dst.suffix + ".bak")
            shutil.copy2(dst, backup_path)
            click.echo(f"📦 Backup created: {backup_path}")

        # Make sure the directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Overwrite with new template
        shutil.copy2(src, dst)
        click.echo(f"✅ Updated: {file}")

    click.echo("🎉 Framework update complete! Review .bak files if needed.")

if __name__ == "__main__":
    cli()
