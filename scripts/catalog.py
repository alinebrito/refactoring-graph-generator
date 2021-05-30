import sys
import subprocess
import os
import json
import pandas as pd

class Catalog:

    @staticmethod
    def java_operations():
        dictionary = {}
        dictionary["RENAME"] = 101
        dictionary["PULL_UP"] = 102
        dictionary["PUSH_DOWN"] = 103
        dictionary["MOVE"] = 104
        dictionary["MOVE_RENAME"] = 105
        dictionary["EXTRACT"] = 106
        dictionary["EXTRACT_MOVE"] = 107
        dictionary["INLINE"] = 108
        #dictionary["INTERNAL_MOVE"] = 109
        #dictionary["INTERNAL_MOVE_RENAME"] = 110
        #dictionary["CHANGE_SIGNATURE"] = 111
        return dictionary

    @staticmethod   
    def js_operations():
        dictionary = {}
        dictionary["RENAME"] = 101
        #dictionary["PULL_UP"] = 102
        #dictionary["PUSH_DOWN"] = 103
        dictionary["MOVE"] = 104
        dictionary["MOVE_RENAME"] = 105
        dictionary["EXTRACT"] = 106
        dictionary["EXTRACT_MOVE"] = 107
        dictionary["INLINE"] = 108
        dictionary["INTERNAL_MOVE"] = 109
        dictionary["INTERNAL_MOVE_RENAME"] = 110
        #dictionary["CHANGE_SIGNATURE"] = 111
        return dictionary
    
    @staticmethod
    def operations(language):
        return Catalog.java_operations() if language.lower() == 'java' else Catalog.js_operations()


    