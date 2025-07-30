from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import os

# ASCII Art for Visual Appeal
TELLABOT_ASCII = r"""
████████╗███████╗██╗     ██╗      █████╗     ██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██║     ██╔══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     ██║     ███████║    ██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██║     ██╔══██║    ██╔══██╗██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗██║  ██║    ██████╔╝╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
"""

# Color codes for terminal output
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m"
}

def colorize(text, color):
    """Apply color to text if running in terminal"""
    if sys.stdout.isatty() and os.name != 'nt':
        return f"{COLORS[color]}{text}{COLORS['ENDC']}"
    return text

# Custom install command to display welcome message
class PostInstallCommand(install):
    """Custom installation command to display welcome message"""
    def run(self):
        install.run(self)
        print(colorize(TELLABOT_ASCII, "BLUE"))
        print(colorize("🚀 Installation Successful!", "GREEN"))
        print(colorize("=" * 50, "CYAN"))
        print(colorize("Get started with these commands:", "BOLD"))
        print(colorize("  tellabot --help          ", "YELLOW") + colorize("- Show help information", "CYAN"))
        print(colorize("  tellabot init my_bot     ", "YELLOW") + colorize("- Scaffold a new bot project", "CYAN"))
        print(colorize("  tellabot run             ", "YELLOW") + colorize("- Launch your bot and admin panel", "CYAN"))
        print(colorize("=" * 50, "CYAN"))
        # print(colorize("📚 Documentation: ", "BOLD") + colorize("https://mechatemesgenportfolio.vercel.app/", "UNDERLINE"))
        # print(colorize("💖 Support: ", "BOLD") + colorize("ililnaafbarihe94@proton.me", "UNDERLINE"))
        print("\n")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tellabot',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        # Add other dependencies your framework needs here
    ],
    entry_points={
        'console_scripts': [
            'tellabot=tellabot.cli:cli',
        ],
    },
    author='Mecha Temesgen',
    author_email='ililnaafbarihe94@proton.me',
    description=colorize('⚡ Framework to scaffold Telegram bots with Flask, Supabase, and Admin panel', 'BOLD'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://mechatemesgenportfolio.vercel.app/', 
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Environment :: Console',
    ],
    python_requires='>=3.7',
    cmdclass={
        'install': PostInstallCommand,
    },
    project_urls={
        'Documentation': 'https://mechatemesgenportfolio.vercel.app/',
        'Source': 'https://github.com/yourusername/tellabot',
        'Tracker': 'https://github.com/yourusername/tellabot/issues',
    },
)