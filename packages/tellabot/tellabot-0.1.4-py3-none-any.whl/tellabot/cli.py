import click
import subprocess
from pathlib import Path
from tellabot.utils import copy_template
import webbrowser
import time
import sys
import shutil
from tellabot import __version__

# --- Styling Helpers ---
def echo_success(message):
    click.echo(click.style(f"✓ {message}", fg='green', bold=True))

def echo_error(message):
    click.echo(click.style(f"✗ {message}", fg='red', bold=True))

def echo_warning(message):
    click.echo(click.style(f"⚠️  {message}", fg='yellow', bold=True))

def echo_info(message):
    click.echo(click.style(f"• {message}", fg='blue'))

def echo_header(message):
    click.echo(click.style(f"\n{message}", fg='bright_magenta', bold=True))

def echo_step(message):
    click.echo(click.style(f"  → {message}", fg='cyan'))

def echo_progress(message):
    with click.progressbar(label=click.style(f"⏳ {message}", fg='bright_blue'), 
                          length=100, fill_char=click.style('█', 'bright_blue')) as bar:
        for i in range(100):
            time.sleep(0.02)  # Simulate progress
            bar.update(1)

# --- CLI Commands ---
@click.group()
@click.version_option(version=__version__, prog_name="tellabot", 
                      message=click.style('%(prog)s %(version)s', fg='bright_green', bold=True))
def cli():
    """TellaBot CLI - Build Telegram Bots with Ease"""
    pass

@cli.command()
@click.argument('project_name')
def init(project_name):
    """✨ Scaffold a new bot project"""
    target = Path.cwd() / project_name if project_name != "." else Path.cwd()
    
    echo_header("🚀 Initializing New Bot Project")
    
    if target.exists() and any(target.iterdir()):
        if project_name == ".":
            echo_warning(f"Directory '{target}' is not empty")
            click.echo()
            
            choice = click.prompt(
                click.style("Delete existing files? (yes/no/cancel)", fg='bright_yellow'),
                default="cancel",
                show_choices=True,
                type=click.Choice(['yes', 'no', 'cancel'], case_sensitive=False)
            ).lower()

            if choice == "yes":
                echo_info("Clearing directory contents...")
                for item in target.iterdir():
                    try:
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                    except Exception as e:
                        echo_error(f"Failed to delete {item}: {e}")
                echo_success("Directory cleared successfully")
            elif choice == "no":
                echo_info("Keeping existing files")
            else:
                echo_error("Operation cancelled")
                return
        else:
            echo_error(f"Directory '{project_name}' already exists and is not empty")
            return

    src = Path(__file__).parent / "templates" / "main_template"
    copy_template(src, target)
    
    echo_success(f"Project '{project_name}' created at {target}")
    echo_header("Next Steps:")
    if project_name != ".":
        echo_step(f"cd {project_name}")
    echo_step("tellabot install")
    echo_step("tellabot run")
    click.echo()


@cli.command()
def install():
    """📦 Install project dependencies"""
    echo_header("Installing Dependencies")
    req_file = Path("requirements.txt")
    
    if not req_file.exists():
        echo_error("requirements.txt not found")
        return
        
    echo_progress("Installing packages")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Show installation summary
        installed = [line for line in result.stdout.split('\n') if 'Successfully installed' in line]
        if installed:
            echo_success(installed[0])
        else:
            echo_success("All dependencies are already installed")
            
    except subprocess.CalledProcessError as e:
        echo_error(f"Installation failed: {e.stderr.splitlines()[-1] if e.stderr else e}")


@cli.command()
def run():
    """🚀 Run bot and admin panel"""
    echo_header("Starting TellaBot Services")
    bot_script = Path.cwd() / "run.py"

    if not bot_script.exists():
        echo_error(f"Run script not found at {bot_script}")
        return

    echo_info("Starting bot and admin server...")
    echo_step("Press CTRL+C to stop")

    # Start run.py as subprocess
    proc = subprocess.Popen([sys.executable, str(bot_script)])

    # Give some time for the server to start
    time.sleep(2)

    url = "http://localhost:5000"
    echo_success(f"Admin panel ready at {click.style(url, underline=True)}")
    webbrowser.open(url)

    try:
        proc.wait()
    except KeyboardInterrupt:
        echo_info("\nStopping services...")
        proc.terminate()
        echo_success("All services stopped")


@cli.command()
def update():
    """🔄 Update core framework files and upgrade tellabot package"""
    echo_header("Updating Framework")
    project_root = Path.cwd()
    template_root = Path(__file__).parent / "templates" / "main_template"

    # Upgrade tellabot package itself
    echo_info("Upgrading tellabot package to the latest version...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "--no-cache-dir", "tellabot"],
            check=True,
            capture_output=True,
            text=True
        )

        upgraded = [line for line in result.stdout.split('\n') if 'Successfully installed' in line or 'Requirement already satisfied' in line]
        if upgraded:
            echo_success(upgraded[0])
        else:
            echo_success("tellabot is already up to date")
    except subprocess.CalledProcessError as e:
        echo_error(f"Failed to upgrade tellabot: {e.stderr.splitlines()[-1] if e.stderr else e}")

    core_files = [
        "app/__init__.py",
        "app/bot.py",
        "run.py"
    ]

    updated_count = 0
    backup_count = 0
    
    for file in core_files:
        src = template_root / file
        dst = project_root / file

        if not src.exists():
            echo_warning(f"Template missing: {file}")
            continue

        # Backup existing file
        if dst.exists():
            backup_path = dst.with_suffix(dst.suffix + ".bak")
            shutil.copy2(dst, backup_path)
            echo_info(f"Backed up: {backup_path.name}")
            backup_count += 1

        # Ensure directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Update file
        shutil.copy2(src, dst)
        echo_success(f"Updated: {file}")
        updated_count += 1

    echo_header("Update Summary")
    echo_step(f"Files updated: {click.style(str(updated_count), fg='bright_green', bold=True)}")
    echo_step(f"Backups created: {click.style(str(backup_count), fg='bright_blue', bold=True)}")
    echo_success("Framework update completed")


if __name__ == "__main__":
    cli()