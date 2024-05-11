"""mkenvyaml.py

by Wesley R. Elsberry with assist from ChatGPT 4 and Codebooga 34b.

Program to scan a folder for Python files, find 'import'-like
statements, collect the set of package names, and attempt to generate
a Conda-compatible YAML requirements text.

This is intended to help get started with making a suitable
'requirements.yml' file if what you have is a Python project of code
files, but not a specific environment or virtual environment for that
project. This will likely only be a starting point, and will need
adjustment to fit your project. Given that one will usually want to
restrict a Docker container to just the necessary packages, this
should help in keeping the generated environment to the minimal set
actually needed by your project. This does not take into account that
a project may include dead code that could specify import packages
that are not used elsewhere in the project; you should make an effort
to prune unneeded code before running this.

You should test the creation of an environment by:

  conda env create -f requirements.yml

or

  mamba env create -f requirements.yml

After that, it should be ready for inclusion in your workflow.

Use redirection to send the output to file.

python mkenvyaml.py --help
Usage: mkenvyaml.py [OPTIONS] DIRECTORY > requirements.yml

  Generates a Conda-compatible 'requirements.yml' file based on Python
  files in the specified directory.

Options:
  --env-name TEXT        Name of the Conda environment
  --python-version TEXT  Desired Python version (e.g., 3.8)
  --help                 Show this message and exit.

"""

import os
import re
import click
from typing import List
import ast
import pprint
import traceback


@click.command()
@click.option("--env-name", prompt="Enter the environment name", help="Name of the Conda environment")
@click.option("--python-version", prompt="Enter the Python version", default="3.8", help="Desired Python version (e.g., 3.8)")
@click.argument("directory", type=click.Path(exists=True))
def main(env_name: str, python_version: str, directory: str) -> None:
    """
    Generates a Conda-compatible 'requirements.yml' file based on Python files in the specified directory.

    Args:
        env_name (str): Name of the Conda environment.
        python_version (str): Desired Python version.
        directory (str): Directory to search for Python files.
    """
    requirements_content = generate_requirements_file(env_name, python_version, directory)
    print(requirements_content)

def analyze(myfile):
    # print("analyze() start...", myfile)
    with open(myfile, "r") as source:
        tree = ast.parse(source.read())

    analyzer = Analyzer()
    analyzer.visit(tree)
    # analyzer.report()

    packages = set()
    for pi in analyzer.stats['from']:
        packages.add(pi)
    for pi in analyzer.stats['import']:
        packages.add(pi)
        
    analyzer.stats['packages'] = sorted(list(packages))
    # print(analyzer.stats['packages'])
    
    return analyzer


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"import": [], "from": []}

    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["from"].append(alias.name)
        self.generic_visit(node)

    def report(self):
        pprint.pprint(self.stats)


def imports_by_analysis(myfile):

    analyzer = analyze(myfile)

    return analyzer
        
def getpackagenames(file_name: str) -> List[str]:
    """
    Examines the given file and returns a list of package names imported in any import statement.

    Args:
        file_name (str): The name of the file to examine.

    Returns:
        List[str]: A list of unique package names imported by the script.

    Raises:
        FileNotFoundError: If the specified file does not exist or is not accessible.
    """
    try:
        analyzer = imports_by_analysis(file_name)
        return analyzer.stats['packages']

    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_name}' not found or inaccessible.")

'''
# Example usage:
if __name__ == "__main__":
    filename_to_examine = "your_python_file.py"
    try:
        packages = getpackagenames(filename_to_examine)
        print("Imported packages:")
        for package in packages:
            print(package)
    except FileNotFoundError as e:
        print(e)
'''

def find_python_files(directory: str) -> List[str]:
    """
    Recursively finds all Python files in the specified directory.

    Args:
        directory (str): The directory to search.

    Returns:
        List[str]: A list of Python file paths.
    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def generate_requirements_file(env_name: str, python_version: str, directory: str) -> str:
    """
    Generates a Conda-compatible 'requirements.yml' file.

    Args:
        env_name (str): Name of the Conda environment.
        python_version (str): Desired Python version (e.g., "3.8").
        directory (str): Directory to search for Python files.

    Returns:
        str: Contents of the 'requirements.yml' file.
    """

    """
    Some packages are named differently from how they are imported,
    some packages are part of the base system, etc.

    The pkg_map is incomplete, so be prepared to extend it for your
    project.

    """
    pkg_map = {
        "os": "",
        "sys": "",
        "traceback": "",
        "json": "",
        "re": "",
        "glob": "",
        "datetime": "",
        "platform": "",
        "_pickle": "",
        "pickle": "",
        "ast": "",
        "auc": "",
        "expit": "",
        "list": "",
        "pprint": "",
        "recall_score": "",
        "roc_curve": "",
        "sgdclassifier": "",
        "train_test_split": "",
        "smote": "imbalanced-learn",
        "imblearn": "imbalanced-learn",
        "beautiful_soup": "bs4",
        "beautifulsoup": "bs4",
        "sklearn": "sckikit-learn",
        "sqlite3": "sqlite",
        "jupyter_lab": "jupyterlab",
        "pysimplegui": "PySimpleGui",
        "pysimpleguiweb": "PySimpleGuiWeb",
        }
    
    python_files = find_python_files(directory)
    imports = set()
    for file in python_files:
        # print(file)
        imports.update(getpackagenames(file))
        
    requirements_content = f"""name: {env_name}
channels:
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
  - pip
"""

    for impi in sorted(imports):
        # Most modules are imported just as they are named, but not all of them
        pkgname = pkg_map.get(impi.lower(), impi)
        if pkgname in [None, ""]:
            continue
        # If the package has a dot dereference...
        pkgname = pkgname.split('.')[0]
        requirements_content += f"  - {pkgname}\n"

    """
    Packages handled by pip rather than Conda are not automatically
    recognized. So you may need to edit in a section that specifies
    pip as the installer and then the package names pip needs to
    install.
    
    - pip:
      - package1
      - package2
    """

    return requirements_content


if __name__ == "__main__":

    main()



    
    
