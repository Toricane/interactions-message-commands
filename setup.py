from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="interactions-message-commands",
    version="0.1.1",
    description="Message commands extension for discord-py-interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Toricane/interactions-message-commands",
    author="Toricane",
    author_email="prjwl028@gmail.com",
    license="MIT",
    packages=["interactions.ext.message_commands"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires="discord-py-interactions>=4.0.1",
)
