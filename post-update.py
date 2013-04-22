#!/bin/env python
import os
import sys
import subprocess
import logging as log
import argparse
from pprint import pformat

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

if __name__ == '__main__':
    branches_flow = ['2.1','2.2','2.3', 'master']
    parser = argparse.ArgumentParser(description='auto merge post update hook')
    parser.add_argument('refname', metavar='refname', help='refname')
    parser.add_argument('oldrev', metavar='oldrev', help='old revision')
    parser.add_argument('newrev', metavar='newrev', help='new revision')
    options = parser.parse_args()

    log.basicConfig(level=log.DEBUG)
    log.debug('Parsed input parameters: %s %s %s' % (get_branch(options.refname), 
        options.oldrev, options.newrev))
    latest = latest_branches_commits(branches_flow)
    log.debug('Storing HEADS for branches before we start: %s', pformat(latest))

    #exit_code = call('git checkout 2.2 && git merge %s' % (options.refname))
    #print exit_code

