#!/usr/bin/env python3
import os
import yaml


# load the list of bug-fixing commits
commits_fn = os.path.join(os.path.dirname(__file__), 'fix-commits.txt')
with open(commits_fn, 'r') as f:
    REVS = [rev.strip() for rev in f]


def build(fix_revision: str) -> dict:
    manifest = {
        'version': '1.0',
        'bug': fix_revision,
        'program': 'ardurover',
        'dataset': 'ardubugs',
        'languages': ['cpp'],
        'source-location': '/experiment/source',
        'build': {
            'type': 'docker',
            'tag': 'squareslab/ardubugs:{}'.format(fix_revision),
            'depends-on': 'squareslab/ardubugs:base',
            'file': 'Dockerfile.bug',
            'arguments': {
                'rev_fix': fix_revision
            }
        },
        'compiler': {
            'type': 'waf',
            'time-limit': 120
        },
        'test-harness': {
            'type': 'empty'
        }
    }

    # write to file
    fn = "bugs/{}.bug.yml".format(fix_revision)
    with open(fn, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False)


def main():
    for fix_revision in REVS:
        build(fix_revision)


if __name__ == '__main__':
    main()
