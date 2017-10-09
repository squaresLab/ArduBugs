#!/usr/bin/env python3
from typing import List
from enum import Enum
from collections import Counter
from pprint import pprint as pp
import re
import git
import os
import operator


# buckets:
# { copter, rover, plane, sub, gcs, libraries, sitl, tools }


CATEGORY_MAPPING = {
    'apmrover2': 'rover',
    'apmrover': 'rover',
    'copte': 'copter',
    'rangefilnder': 'rangefinder',
    'ardcucopter': 'copter',
    'doc': 'docs',
    'documentation': 'docs',
    'simulator': 'sitl',
    'baro': 'barometer'
}

# a list of categories that we're not interested in
DROP_CATEGORIES = [
    'waf',
    'cli',
    'github',
    'web',
    'docs',
    'travis',
    'ci',
    'build',
    'readme',
    'autotest',
    'desktop',
    'pysim',
    'codestyle',
    'rpm',
    'vagrant',
    'hello'
]

REGEX_HIL = re.compile('\\bhil\\b')
REGEX_BUG = re.compile('\\bbug\\b')
REGEX_FIX = re.compile('\\bfix\\b')
REGEX_CATEGORY = re.compile("^\w+(?=:)")


class Package(Enum):
    copter = 'copter'
    rover = 'rover'
    plane = 'plane'
    sub = 'sub'
    gcs = 'gcs'
    sitl = 'sitl'
    tools = 'tools'
    library = 'library'


    @staticmethod
    def determine(commit: git.Commit, category: str) -> 'Package':
        """
        Determines the package to which a provided commit (belonging to a given
        category) belongs.
        """
        if category == 'copter':
            return Package.copter
        if category == 'plane':
            return Package.plane
        if category == 'rover':
            return Package.rover
        if category == 'sub':
            return Package.sub
        if category == 'sitl':
            return Package.sitl
        if category in ['gcs', 'gcs_mavlink']:
            return Package.gcs
        if category in ['tools', 'replay', 'logs', 'loganalyzer', 'menu', 'hil', 'scripts']:
            return Package.tools

        return Package.library


class BugFix(object):
    def __init__(self, commit: git.Commit, category: str) -> None:
        self.__commit = commit
        self.__category = category
        self.__description = commit.message.partition(':')[2].strip()
        self.__package = Package.determine(commit, category)

    
    @property
    def hex8(self) -> str:
        return self.id[:8]


    @property
    def id(self) -> str:
        return str(self.commit)


    @property
    def commit(self) -> git.Commit:
        return self.__commit


    @property
    def category(self) -> str:
        return self.__category


    @property
    def package(self) -> Package:
        return self.__package


    @property
    def description(self) -> str:
        return self.__description


    @property
    def files(self) -> List[str]:
        return list(self.commit.stats.files.keys())
    

    @property
    def summary(self) -> str:
        return self.description.partition('\n')[0]


    def __str__(self) -> str:
        return "{}: {}".format(self.hex8, self.summary)


    def to_csv_row(self) -> List[str]:
        """
        Returns a description of this row in the form of a list, ready to
        be written as a CSV row.
        """
        return []


def contains_any(string: str, substrings: List[str]) -> bool:
    for substring in substrings:
        if substring in string:
            return True
    return False


def get_bugs() -> List[BugFix]:
    if not os.path.exists('ardu'):
        print('cloning repo...')
        git.Repo.clone_from('https://github.com/ArduPilot/ArduPilot.git', 'ardu')

    if os.path.exists('non-bugs.txt'):
        with open('non-bugs.txt', 'r') as f:
            non_bugs = set(rev.partition(',')[0] for rev in f)
    else:
        non_bugs = set()

    repo = git.Repo('ardu')
    commits = list(repo.iter_commits())
    print("# commits: {}".format(len(commits)))

    bugs = []
    categories = {}
    for c in commits:
        msg = c.message.lower()

        # 0. must not belong to the set of non-bugs
        if str(c) in non_bugs:
            continue

        # 1. must contain the term "bug" or "fix"
        if not (REGEX_BUG.search(msg) or REGEX_FIX.search(msg)):
            continue

        # 2. must not contain any of the terms:
        #       "build", "compile", "hil"
        if REGEX_HIL.search(msg):
            continue
        if contains_any(msg, ['build', 'compile', 'comment', 'indent-tabs-mode', 'fix example',
                              'spelling', 'minor fix', 'line ending', 'documentation',
                              'coding style', 'indentation', 'whitespace', 'docs', 'formatting']):
            continue

        # determine the category name
        category = REGEX_CATEGORY.match(c.message)
        if not category: # ill-formed description; discard
            continue

        # normalise the category name
        category = category.group(0).lower()
        category = category.replace('ardu', '')
        category = category.replace('ap_', '')
        category = CATEGORY_MAPPING.get(category, category)

        # drop board-specific bugs
        if 'px4' in category:
            continue

        # discard categories that we're not interested in
        if category in DROP_CATEGORIES:
            continue

        # 3. must modify at least one source code file
        # (NOTE: this is quite expensive, so we leave it till the end)
        # files = c.stats.files.keys()
        # if not any(fn.endswith('.cpp') or fn.endswith('.h') or fn.endswith('.pde') for fn in files):
        #     continue
        
        # keep track of the number of commits belonging to each category
        if category not in categories:
            categories[category] = 1
        else:
            categories[category] += 1

        # construct a bug fix object
        fix = BugFix(c, category)

        # record the commit as a bug fix
        bugs.append(fix)

    return bugs


if __name__ == '__main__':
    bugs = get_bugs()
    copter_bugs = [b for b in bugs if b.package == Package.copter]
    for b in copter_bugs:
        print("{}: {}".format(b.hex8, b.summary))
    print("# bugs: {}".format(len(bugs)))
