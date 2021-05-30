import sys
import subprocess
import os
import json
import pandas as pd
from scripts.gitservice import GitService
from scripts.refdiff import RefDiff
from scripts.filter import RefactoringFilter
from scripts.refgraph import RefactoringGraph

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
    filter.filter_core_operations(project, language)
    
    rg = RefactoringGraph()
    rg.find_disconnected_subgraphs(project, language)
    rg.plot_atomic_subgraphs(project)
    rg.plot_overtime_subgraphs(project)

    pass

if __name__ == "__main__":
    main()