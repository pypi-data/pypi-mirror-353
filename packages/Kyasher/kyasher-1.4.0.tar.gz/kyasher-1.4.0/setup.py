from setuptools import setup, find_packages
def load_readme() -> str:
    with open("README.md",encoding="utf-8_sig") as fin:
        return fin.read()
setup(
    name='Kyasher',
    version='1.4.0',
    keywords = "kyash",
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    author='taka4602',
    author_email='takaka4602@gmail.com',
    url='https://github.com/taka-4602/Kyasher',
    description='An API wrapper for the KyashAPI',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "requests",
        "bs4",
    ],
    python_requires='>=3.6',
)