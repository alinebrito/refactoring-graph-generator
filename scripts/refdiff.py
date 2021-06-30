import sys
import subprocess
import os
import json
import pandas as pd

class RefDiff:
    
    def detect_refactorings(self, project, language):

        print('Running RefDiff...')

        commits = pd.read_csv('dataset/{}/results/commits.csv'.format(project), sep=";", keep_default_na=False)
        path = 'dataset/{}/results'.format(project)
        head = 'entityBeforeFullName;entityBeforeSimpleName;entityBeforeLocation;entityBeforeParameters;entityBeforeLine;entityBeforeParents;entityAfterFullName;entityAfterSimpleName;entityAfterLocation;entityAfterParameters;entityAfterLine;entityAfterParents;refactoringLevel;refactoringType;commitHash;abbreviatedCommitHash;authorName;authorEmail;authorDate;authorDateUnixTimestamp;committerName;committerEmail;committerDate;committerDateUnixTimestamp'

        with open('{}/refactorings.csv'.format(path), 'a+') as file:
            file.flush()
            os.fsync(file.fileno())
            file.write('{}\n'.format(head))
            for index, commit in commits.iterrows():

                print('Processing commit {}...'.format(commit.get('commitHash')))
        
                proc = subprocess.Popen(['java', '-cp', '"bin/refdiff_lib/*"', '-jar', 'bin/refdiff.jar', 'dataset', '{}/code'.format(project), language, commit.get('commitHash'), '-Xmx6144m'], stdout=subprocess.PIPE).communicate()
                for data in proc:
                    if data:
                        refactorings = json.loads(data.decode('utf-8'))
                        for ref in refactorings:
                            line = ''
                            for key in ref.keys():#refactoring
                                line = line + '{};'.format(ref.get(key))
                            for key in commit.keys():#commit
                                line = line + '{};'.format(commit.get(key))
                            file.flush()
                            os.fsync(file.fileno())
                            file.write('{}\n'.format(line[:-1]))
                            
        pass