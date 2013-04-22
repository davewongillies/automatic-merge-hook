#!/usr/bin/python
import os
import sys
import subprocess
import logging as log
from itertools import dropwhile
from pprint import pformat

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def get_output(command):
    return subprocess.Popen(command.split(),stdout=subprocess.PIPE, stderr=open(os.devnull, 'w')).communicate()

def call(command):
    return subprocess.call(command, shell=True)

def get_branch(refname):
    return refname.split('/')[2]

def latest_branches_commits(branches):
    latest = {}
    for branch in branches:
        latest[branch] = get_output('git rev-parse %s' % branch)[0][:-1]
    return latest

def start_from(branch, branches):
    return list(dropwhile(lambda x: x != branch, branches))

def next(item, lst):
    try:
        return lst[lst.index(item) + 1]
    except IndexError:
        return None

def parse_arguments():
    try:
        import argparse
        parser = argparse.ArgumentParser(description='auto merge post update hook')
        parser.add_argument('refname', metavar='refname', help='refname')
        parser.add_argument('oldrev', metavar='oldrev', help='old revision')
        parser.add_argument('newrev', metavar='newrev', help='new revision')
        return parser.parse_args()
    except ImportError:
        return Bunch(refname = sys.argv[1], oldrev = sys.argv[2], newrev = sys.argv[3])

def automatic_merge(head_before_start, latest, branches_flow):
    log.debug('Auto-merging through: %s' % branches_flow)
    reset = False
    for branch in branches_flow:
        onto = next(branch, branches_flow)
        if onto:
            exitcode = call('git checkout %s && git merge refs/heads/%s' % (onto, branch))
            if exitcode:
                log.debug('Merge of %s onto %s failed, must reset to original state' % (branch, onto))
                call('git reset --hard %s' % (latest[onto]))
                reset = True
                break

    if reset:
        for to_reset in branches_flow:
            call('git checkout %s && git reset --hard %s && git checkout %s' % (
                to_reset, latest[to_reset], head_before_start))
        sys.exit('Automated merges failed, reset to original state')

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    os.environ["GIT_WORK_TREE"] = os.path.abspath(os.curdir)
    
    branches_flow = ['2.1','2.2','2.3', 'master']
    head_before_start = get_output('git rev-parse --abbrev-ref HEAD')[0][:-1]
    log.debug('Before we start we are at: %s' % head_before_start)

    options = parse_arguments()
    log.debug('Parsed input parameters: %s %s %s' % (options.refname, options.oldrev, options.newrev))

    latest = latest_branches_commits(branches_flow)
    log.debug('Storing current heads of branches before we start: %s', pformat(latest))

    branches_flow = start_from(get_branch(options.refname), branches_flow)
    automatic_merge(head_before_start, latest, branches_flow)
