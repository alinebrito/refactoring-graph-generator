import sys
import subprocess
import os
import json

def git_clone(project):
    print('Cloning {}...'.format(project))
    subprocess.call('git clone https://github.com/{}.git dataset/{}/code'.format(project,project), shell = True)
    pass

def git_first_parent(project):
    print('Finding commits...')
    proc = subprocess.Popen(['git', '-C', 'dataset/{}/code'.format(project), 'log', '--first-parent', '--pretty=%H;%h;%an;%ae;%ad;%at'], stdout=subprocess.PIPE).communicate()
    path = 'dataset/{}/results'.format(project)
    os.mkdir(path)
    with open('{}/commits.csv'.format(path), 'w') as file:
        file.write('sha1;abbreviated_sha1;author_name;author_email;author_date;author_date_unix_timestamp\n')
        [file.write(data.decode('utf-8')) for data in proc if data]
    pass

def refdiff(project, language, commits):
    path = 'dataset/{}/results'.format(project)
    with open('{}/refactorings.csv'.format(path), 'a+') as file:
        file.write('name\n')
        for commit in commits:
            proc = subprocess.Popen(['java', '-cp', '"bin/refdiff_lib/*"', '-jar', 'bin/refdiff.jar', project, language, commit, '-Xmx6144m'], stdout=subprocess.PIPE).communicate()
            for data in proc:
                if data:
                    refactorings = json.loads(data.decode('utf-8'))
                    for ref in refactorings:
                        line = ''
                        for key in ref.keys():
                            line = line + '{};'.format(ref.get(key))
                            file.write('{}\n'.format(line[:-1]))
    pass

def main():
    print('\n\n----------------------------------------------')
    print('Refactoring Graph Generator (v.0.1)')
    print('----------------------------------------------\n')
    if(len(sys.argv) < 3) or (sys.argv[2] != 'java' and sys.argv[2] != 'js'):
        print("Usage: {} owner/project language\n".format(sys.argv[0]))
        return
    
    project = sys.argv[1]
    language = sys.argv[2]
    git_clone(project)
    git_first_parent(project)
    refdiff(project, language, ['aa'])
    pass

if __name__ == "__main__":
    main()