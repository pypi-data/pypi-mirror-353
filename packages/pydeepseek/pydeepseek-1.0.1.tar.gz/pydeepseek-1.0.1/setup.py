from setuptools import setup, find_packages

setup(
    name="pydeepseek",
    version="1.0.1",
    packages=find_packages(),
    install_requires=["requests"],
    author="LongTime",
    author_email="noreply@long-time.ru",
    description="Python wrapper for DeepSeek V3 model",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deepseek-v3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
)
