from setuptools import setup, find_packages

setup(
    name="rag-mongo-logger",
    version="0.1.1",
    description="Async buffered logger with MongoDB and PostgreSQL support for your rag application",
    author="Siddhesh Dosi",
    author_email="siddheshdosi106@google.com",
    packages=find_packages(),
    install_requires=[
        "pymongo",
        # add more dependencies as needed
    ],
    python_requires=">=3.10",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
