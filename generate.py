#!/usr/bin/env python3
from typing import Dict, Any
import os
import yaml


# load the list of bug-fixing commits
commits_fn = os.path.join(os.path.dirname(__file__), 'fix-commits.txt')
with open(commits_fn, 'r') as f:
    REVS = [rev.strip() for rev in f]


def build(fix_revision: str, manifest: Dict[str, Any]) -> None:
    name_bug = "ardubugs:{}".format(fix_revision)
    name_image = 'squareslab/ardubugs:{}'.format(fix_revision)
    manifest["bugs"].append({
        'name': name_bug,
        'image': name_image,
        'program': 'ardurover',
        'dataset': 'ardubugs',
        'languages': ['cpp'],
        'source-location': '/opt/ardupilot',
        'compiler': {
            'type': 'simple',
            'context': '/opt/ardupilot',
            'command': './builder',
            'command_with_instrumentation': './configure --instrumentation && ./builder',
            'command_clean': 'exit 0',
            'time-limit': 120
        },
        'coverage': {
            'files-to-instrument': [
                'APMrover2/APMrover2.cpp',
                'ArduCopter/ArduCopter.cpp',
                'ArduPlane/ArduPlane.cpp'
            ]
        },
        'test-harness': {
            'type': 'empty'
        }
    })
    manifest["blueprints"].append({
        'type': 'docker',
        'tag': name_image,
        'depends-on': 'squareslab/ardubugs:base',
        'file': 'Dockerfile.bug',
        'arguments': {'rev_fix': fix_revision}
    })


def main():
    manifest = {
        'version': '1.1',
        'blueprints': [
            {'type': 'docker',
             'file': 'Dockerfile',
             'tag': 'squareslab/ardubugs:base',
             'context': '.'}
        ],
        'bugs': []
    }

    for fix_revision in REVS:
        build(fix_revision, manifest)

    with open('ardu.bugzoo.yml', 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False)


if __name__ == '__main__':
    main()
