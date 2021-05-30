import re
import os.path
import hashlib
import sys
import pandas as pd

from modules.catalog import Catalog

class RefactoringFilter:

    def valid_level(self, level, language):
        return ((level.lower() == 'methoddeclaration') and (language.lower() == 'java')) or ((level.lower() == 'function') and (language.lower() == 'js'))

    def valid_type(self, refactoring, language):
        return (refactoring.get('refactoringType') in Catalog.operations(language)) 
    
    def contains_test_package(self, path):
        path = path.split("#")[0]
        test_package = re.findall(r'(test.+?|test)\.', path, re.IGNORECASE)
        contains_test_package = bool(re.search(r'(test.+?|test)\.', path, re.IGNORECASE))
        return contains_test_package

    def contains_sample_package(self, path):
        path = path.split("#")[0]
        sample_package = re.findall(r'(sample.+?|sample)\.', path, re.IGNORECASE)
        contains_sample_package = bool(re.search(r'(sample.+?|sample)\.', path, re.IGNORECASE))
        return contains_sample_package

    def contains_example_package(self, path):
        path = path.split("#")[0]
        example_package = re.findall(r'(example.+?|example)\.', path, re.IGNORECASE)
        contains_example_package = bool(re.search(r'(example.+?|example)\.', path, re.IGNORECASE))
        return contains_example_package

    def exports_keyword(self, entity):
        return bool(re.search(r'(^exports.|^exports#|\.exports\.|\.exports#|#exports$)', entity, re.IGNORECASE))

    def contains_exports_keyword(self, refactoring):
        return self.exports_keyword(refactoring.get('entityBeforeFullName')) or self.exports_keyword(refactoring.get('entityAfterFullName'))

    def entity_contains_package(self, entity, package):
        return bool(re.search(r'(^' + package + '.|\.' + package + '\.|\.' + package + '#)', entity, re.IGNORECASE))

    def contains_package(self, refactoring, package):
        return self.entity_contains_package(refactoring.get('entityBeforeFullName'), package) or self.entity_contains_package(refactoring.get('entityAfterFullName'), package)

    def valid_package(self, path):
        return ((not self.contains_test_package(path)) and (not self.contains_sample_package(path)) and (not self.contains_example_package(path)))

    def equals_entities(self, refactoring):
        entity_before = refactoring.get('entityBeforeFullName')
        entity_after = refactoring.get('entityAfterFullName')   
        return (entity_before == entity_after)

    def contains_constructor(self, refactoring):
        entity_before = refactoring.get('entityBeforeFullName')
        entity_after = refactoring.get('entityAfterFullName')
        return ("#new(" in entity_before) or ("#new(" in entity_after)

    def valid_refactoring(self, refactoring, list_duplicated_edges, language):
        return (not self.equals_entities(refactoring)) and (not self.contains_duplicated_edge(refactoring, list_duplicated_edges)) and (self.valid_type(refactoring, language))

    def find_duplicated_operations(self, refactorings):
        operations = []
        [operations.append('{}|{}'.format(ref.get('entityBeforeFullName'), ref.get('entityAfterFullName'))) for index, ref in refactorings.iterrows()]
        return list(set([op for op in operations if operations.count(op) > 1]))

    def contains_duplicated_edge(self, refactoring, list_duplicated_edges):
        edge1 = '{}|{}'.format(refactoring.get('entityBeforeFullName'), refactoring.get('entityAfterFullName'))
        edge2 = '{}|{}'.format(refactoring.get('entityAfterFullName'), refactoring.get('entityBeforeFullName'))
        return (edge1 in list_duplicated_edges) or (edge2 in list_duplicated_edges)

    def default_core_operation(self, refactoring, list_duplicated_edges, language):
        return self.valid_level(refactoring.get('refactoringLevel'), language) and self.valid_package(refactoring.get('entityBeforeFullName')) and self.valid_package(refactoring.get('entityAfterFullName')) and self.valid_refactoring(refactoring, list_duplicated_edges, language)

    def core_operation_js(self, refactoring, list_duplicated_edges, language):
        return self.default_core_operation(refactoring, list_duplicated_edges, language) and (not self.contains_exports_keyword(refactoring)) and (not self.contains_package(refactoring, 'dist')) and (not self.contains_package(refactoring, 'doc')) and (not self.contains_package(refactoring, 'docs')) and (not self.contains_package(refactoring, 'benchmark')) and (not self.contains_package(refactoring, 'benchmarks'))

    def core_operation_java(self, refactoring, list_duplicated_edges, language):
        return self.default_core_operation(refactoring, list_duplicated_edges, language) and     (not self.contains_constructor(refactoring))

    def core_operation(self, refactoring, list_duplicated_edges, language):
        return self.core_operation_java(refactoring, list_duplicated_edges, language) if language.lower() == 'java' else self.core_operation_js(refactoring, list_duplicated_edges, language)

    def filter_core_operations(self, project, language):
      
        refactorings = pd.read_csv('dataset/{}/results/refactorings.csv'.format(project), sep=';', keep_default_na=False)

        core_refactorings = []
        list_duplicated_edges = self.find_duplicated_operations(refactorings)

        with open('dataset/{}/results/selected_refactorings.csv'.format(project), 'a+') as file:
            head = 'entityBeforeFullName;entityBeforeSimpleName;entityBeforeLocation;entityBeforeParameters;entityBeforeLine;entityBeforeParents;entityAfterFullName;entityAfterSimpleName;entityAfterLocation;entityAfterParameters;entityAfterLine;entityAfterParents;refactoringLevel;refactoringType;commitHash;abbreviatedCommitHash;authorName;authorEmail;authorDate;authorDateUnixTimestamp;committerName;committerEmail;committerDate;committerDateUnixTimestamp'
            file.write(head)
            for index, ref in refactorings.iterrows():
                if self.core_operation(ref, list_duplicated_edges, language):
                    line = ''
                    for key in ref.keys():
                        line = line + '{};'.format(ref.get(key))
                    file.write('{}\n'.format(line[:-1]))
        pass

