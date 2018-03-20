#!/usr/bin/env python3
import sys
import os
import subprocess
import datetime
from os.path import expanduser
import argparse
import tempfile

def read_repos(path):
    repos = []
    with open(path, 'r') as f:
        for line in f:
            path = line.strip()
            repos.append(os.path.abspath(path))
    return repos

def get_remote():
    remotes = subprocess.getoutput('git remote -v')
    if remotes == '':
        return None
    remote = remotes.splitlines()[0].split('\t')[1].split(' ')[0]
    if remote.startswith('git@'):
        remote = remote.replace(':', '/').replace('git@', 'https://')
    return remote.replace('.git', '')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get last weeks commits and report them in .md format")
    parser.add_argument('repos', type=str, help="repositories file: one file path per line")
    parser.add_argument('out', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('--today', type=str, default=None, help="date of 'today', day/month/year e.g. 03/06/18")
    parser.add_argument('--weeks', type=int, default=1, help="how many weeks to include in the report.")
    parser.add_argument('--html', dest='html', action='store_true', help="convert file to html using pandoc")
    parser.add_argument('--markdown', dest='html', action='store_false', help="output in markdown format")
    parser.set_defaults(html=True)
    args = parser.parse_args()
    repos = read_repos(args.repos)
    today = datetime.datetime.strptime(args.today, '%d/%m/%y') if args.today is not None else datetime.date.today()
    days_since_last_monday = today.weekday()
    if days_since_last_monday == 0:
        days_since_last_monday = 7
    last_monday = today - datetime.timedelta(days=days_since_last_monday, weeks=max(0, args.weeks - 1))
    author = subprocess.getoutput('git config --get user.name')
    commits = []
    tmp = tempfile.mktemp()
    with open(tmp, 'w') as f:
        print("# Commits", last_monday, "-", today, file=f)
        for repo in repos:
            os.chdir(repo)
            repo_name = os.path.basename(repo)
            remote = get_remote()
            call = 'git log --author="{}" --since="{}" --pretty=format:"%ad %h %s" --date=short'.format(author, last_monday)
            git_log = subprocess.getoutput(call)
            git_log_lines = git_log.splitlines()
            if len(git_log_lines) > 0:
                print("##", repo_name, file=f)
            for line in git_log_lines:
                tokens = line.split(' ')
                date = '``{}``'.format(tokens[0])
                commit_hash = tokens[1]
                commit_msg = '``{}``'.format(' '.join(tokens[2:]))
                commit_link = "{}/commit/{}".format(remote, commit_hash) if remote is not None else ""
                print("*", "[`{}`]({})".format(commit_hash, commit_link), commit_msg, file=f)
    if args.html:
        import subprocess
        print(subprocess.check_output(['pandoc', '--from', 'markdown', '--to', 'html', tmp]).decode('utf-8'), file=args.out)
    else:
        with open(tmp, 'r') as f:
            for line in f:
                print(line.strip(), file=args.out)
