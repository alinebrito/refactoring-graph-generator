# Refactoring Graph Generator

Scripts to generate refactoring subgraphs in Java and JavaScript.

## Dependencies

* Git 2.17.1+

* Java 8

* Python 3+

* Python libraries: `pip3 install --no-cache-dir -r requirements.txt`

* [Graphviz](https://graphviz.org/download/) 2.40.1 

## Usage

> python3 main.py owner/project language

## Examples:

JavaScript:

> python main.py request/request js

Java:

> python main.py bumptech/glide java


## Output:

Commits: 

> dataset/owner/project/results/commits.csv

Refactorings:

> dataset/owner/project/results/refactorings.csv

Selected refactorings:

> dataset/owner/project/results/selected_refactorings.csv

Refactorings subgraphs (JSON):

> dataset/owner/project/results/atomic_subgraphs.json

> dataset/owner/project/results/overtime_subgraphs.json

Refactorings subgraphs (HTML):

> dataset/owner/project/results/view
