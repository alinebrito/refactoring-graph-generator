import subprocess
import os

class GitService:
    
    def clone(self, project):
        print('Cloning {}...'.format(project))
        subprocess.call('git clone https://github.com/{}.git --bare dataset/{}/code'.format(project,project), shell = True)
    pass

    def first_parent(self, project):
        print('Finding commits from default branch...')
        proc = subprocess.Popen(['git', '-C', 'dataset/{}/code'.format(project), 'log', '--first-parent', '--pretty=%H;%h;%an;%ae;%ad;%at;%cn;%ce;%cd;%ct'], stdout=subprocess.PIPE).communicate()
        file_name = 'dataset/{}/results/commits.csv'.format(project)
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w') as file:
            file.write('commitHash;abbreviatedCommitHash;authorName;authorEmail;authorDate;authorDateUnixTimestamp;committerName;committerEmail;committerDate;committerDateUnixTimestamp\n')
            [file.write(data.decode('utf-8')) for data in proc if data]
    pass