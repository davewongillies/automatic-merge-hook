#!/bin/env python
import os
import sys
import subprocess
import logging as log
import argparse
from itertools import dropwhile
from pprint import pformat

def get_output(command):
    return subprocess.Popen(command.split(),stdout=subprocess.PIPE, stderr=open(os.devnull, 'w')).communicate()

def call(command):
#    log.debug(command)
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
    parser = argparse.ArgumentParser(description='auto merge post update hook')
    parser.add_argument('refname', metavar='refname', help='refname')
    parser.add_argument('oldrev', metavar='oldrev', help='old revision')
    parser.add_argument('newrev', metavar='newrev', help='new revision')
    return parser.parse_args()

if __name__ == '__main__':
    os.environ["GIT_WORK_TREE"] = os.path.abspath(os.curdir)
    
    branches_flow = ['2.1','2.2','2.3', 'master']
    log.basicConfig(level=log.DEBUG)
    head_before_start = get_output('git rev-parse --abbrev-ref HEAD')[0][:-1]
    options = parse_arguments()

    log.debug('before we start we are at: %s' % head_before_start)
    log.debug('Parsed input parameters: %s %s %s' % (options.refname, 
        options.oldrev, options.newrev))
    latest = latest_branches_commits(branches_flow)
    log.debug('Storing current HEADS of branches before we start: %s', pformat(latest))

    curr_refname = options.refname
    branches_flow = start_from(get_branch(options.refname), branches_flow)
    log.debug('auto-merging through: %s' % branches_flow)
    reset = False
    for branch in branches_flow:
        onto = next(branch, branches_flow)
        if onto:
            exitcode = call('git checkout %s && git merge refs/heads/%s' % (onto, branch))
            if exitcode:
                log.debug('merge of %s onto %s failed, must reset to original state' % (branch, onto))
                call('git reset --hard %s' % (latest[onto]))
                reset = True
                break

    if reset:
        for to_reset in branches_flow:
            call('git checkout %s && git reset --hard %s && git checkout %s' % (
                to_reset, latest[to_reset], head_before_start))
        sys.exit('Automated merges failed, reset to original state')
