from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Direct requirements (no external file needed)
requirements = [
    "telethon~=1.40.0",
    "python-dotenv~=1.1.0",
    "PyYAML~=6.0.2",
    "aiofiles~=24.1.0",
]

setup(
    name="tgloader",
    version="0.0.1",
    author="TgLoader",
    author_email="ip387525@gmail.com",
    description="Telegram media downloader library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1SKcode/tgloader",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
   install_requires=[
    "telethon~=1.40.0",
    "python-dotenv~=1.1.0",
    "PyYAML~=6.0.2", 
    "aiofiles~=24.1.0",
    ],
) 