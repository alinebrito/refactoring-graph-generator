# Refactoring Graph Generator

Scripts to generate refactoring subgraphs in Java and JavaScript.

## Usage

> python3 main.py owner/project language

## Examples:

JavaScript:

> python main.py request/request js

Java:

> python main.py bumptech/glide java


## Output:

Commits: 

> output/owner/project/results/commits.csv

Refactorings:

> output/owner/project/results/refactorings.csv

Selected refactorings:

> output/owner/project/results/selected_refactorings.csv

Refactorings subgraphs (JSON):

> output/owner/project/results/atomic_subgraphs.json

> output/owner/project/results/overtime_subgraphs.json

Refactorings subgraphs (HTML):

> output/owner/project/results/view