from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mtabe",
    version="1.8.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
    "click>=8.1.8,<9.0",
    "colorama>=0.4.6,<0.5",
    "rich>=14.0.0,<15.0",
    "pandas>=2.2.3,<3.0",
    "openpyxl>=3.1.5,<4.0",
    "xlrd>=2.0.1,<3.0",
    "python-docx>=1.1.2,<2.0",
    "PyPDF2>=3.0.1,<4.0",
    "python-pptx>=1.0.2,<2.0",
    "requests>=2.32.3,<3.0",
    "beautifulsoup4>=4.13.4,<5.0",
    "pyfiglet>=1.0.2,<2.0",
    "python-dotenv>=1.1.0,<2.0",
    "groq>=0.23.1,<1.0",          # or whatever the expected major version is
    "yt-dlp>=2025.5.22,<2026.0"  # yt-dlp uses year.month.date, so next year may break things
],
    entry_points={
        'console_scripts': [
            'mtabe=mtabe.main:mycommands',
        ],
    },
    author="Henrylee",
    author_email="henrydionizi@gmail.com",
    description="An AI-powered CLI for adding notes and generating flashcards, tests, and chat summaries.",
    keywords='cli ai notes flashcards',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Henryle-hd/mtabe",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)