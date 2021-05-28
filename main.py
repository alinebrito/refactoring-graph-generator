import sys
import subprocess
import os
import json
import pandas as pd
from modules.gitservice import GitService
from modules.refdiff import RefDiff
from modules.filter import RefactoringFilter
from modules.refgraph import RefactoringGraph

def main():
    print('\n\n----------------------------------------------')
    print('Refactoring Graph Generator (v.0.1)')
    print('----------------------------------------------\n')
    if(len(sys.argv) < 3) or (sys.argv[2] != 'java' and sys.argv[2] != 'js'):
        print("Usage: {} owner/project language\n".format(sys.argv[0]))
        return
    
    project = sys.argv[1]
    language = sys.argv[2]

    git = GitService()
    git.clone(project)
    git.first_parent(project)

    refdiff = RefDiff()
    refdiff.detect_refactorings(project, language)

    filter = RefactoringFilter()
    filter.core_operations(project, language)
    
    rg = RefactoringGraph()
    subgraphs = rg.find_disconnected_subgraphs(project, language)

    pass

if __name__ == "__main__":
    main()