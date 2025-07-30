from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tellabot',
    version='0.1.0',
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
    description='Framework to scaffold Telegram bots with Flask, Supabase, Admin panel, and CLI tools.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://mechatemesgenportfolio.vercel.app/', 
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
