#!/usr/bin/env python
import os
import subprocess
import datetime
from os.path import expanduser
import argparse

def read_repos(path):
    repos = []
    with open(path, 'r') as f:
        for line in f:
            path = line.strip()
            repos.append(os.path.abspath(path))
    return repos

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get last weeks commits and report them in .md format")
    parser.add_argument('-r', '--repos', type=str, default=expanduser("~"), help="repositories file: one file path per line")
    args = parser.parse_args()
    repos = read_repos(args.repos)
    today = datetime.date.today()
    days_since_last_monday = today.weekday()
    if days_since_last_monday == 0:
        days_since_last_monday = 7
    last_monday = today - datetime.timedelta(days=days_since_last_monday)
    author = subprocess.getoutput('git config --get user.name')
    commits = []
    for repo in repos:
        os.chdir(repo)
        repo_name = os.path.basename(repo)
        print("##", repo_name)
        remotes = subprocess.getoutput('git remote -v')
        _remote = remotes.splitlines()[0].split('\t')[1].split(' ')[0]
        if _remote.startswith('git@'):
            _remote = _remote.replace(':', '/').replace('git@', 'https://')
        remote = _remote.replace('.git', '')
        call = 'git log --author="{}" --since="{}" --pretty=format:"%ad %h %s" --date=short'.format(author, last_monday)
        git_log = subprocess.getoutput(call)
        for line in git_log.splitlines():
            tokens = line.split(' ')
            date = '``{}``'.format(tokens[0])
            commit_hash = tokens[1]
            commit_msg = '``{}``'.format(' '.join(tokens[2:]))
            commit_link = "{}/commit/{}".format(remote, commit_hash)
            print("*", "[`{}`]({})".format(commit_hash, commit_link), commit_msg)
        print()
