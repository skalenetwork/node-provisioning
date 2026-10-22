#   -*- coding: utf-8 -*-
#
#   This file is part of node-provisioning
#
#   Copyright (C) 2026-Present SKALE Labs
#
#   node-provisioning is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   node-provisioning is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with node-provisioning.  If not, see <https://www.gnu.org/licenses/>.

"""Print a skale-node compose file changed to build the SKALE containers from source.

Only the services below get a build section (the repo synced to <base path>/<repo>) and a
local image name. Everything else stays as in skale-node, comments and formatting included.

Usage: compose_from_source.py <compose file> <base path>
"""

import sys

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml.util import load_yaml_guess_indent

# Image built from each repo
IMAGES = {
    'skale-admin': 'skale-admin:${TAG:-latest}',
    'transaction-manager': 'skalenetwork/transaction-manager:${TAG:-latest}',
    'bounty-agent': 'bounty-agent:${TAG:-latest}',
    'skale-watchdog': 'skale-watchdog:${TAG:-latest}',
}

# Repo each service is built from. Add new skale-node services here.
SERVICES = {
    'transaction-manager': 'transaction-manager',
    'admin': 'skale-admin',
    'boot-admin': 'skale-admin',
    'api': 'skale-admin',
    'boot-api': 'skale-admin',
    'celery': 'skale-admin',
    'bounty': 'bounty-agent',
    'watchdog': 'skale-watchdog',
}


def build_from_source(compose: CommentedMap, base_path: str) -> list[str]:
    built = []
    for name, service in compose['services'].items():
        repo = SERVICES.get(name)
        if repo is None:
            continue
        image = DoubleQuotedScalarString(IMAGES[repo])
        build = CommentedMap(
            context=DoubleQuotedScalarString(f'{base_path}/{repo}'),
            dockerfile='Dockerfile',
            network='host',
        )
        service.pop('build', None)
        # Not the keys a service gets from a merge (<<: *sk_base)
        own_keys = [key for key, _ in service.non_merged_items()]
        service['image'] = image
        service['build'] = build
        if 'image' in own_keys:
            # Keep build right after image
            for key in own_keys[own_keys.index('image') + 1:]:
                service.move_to_end(key)
        built.append(name)
    return built


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    path, base_path = sys.argv[1], sys.argv[2].rstrip('/')
    try:
        with open(path) as compose_file:
            text = compose_file.read()
    except FileNotFoundError:
        sys.exit(f'{path} not found')

    # Write it back the way skale-node formats it
    _, indent, block_seq_indent = load_yaml_guess_indent(text)
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    if block_seq_indent is None:
        yaml.indent(mapping=indent, sequence=indent, offset=0)
    else:
        yaml.indent(mapping=2, sequence=indent, offset=block_seq_indent)
    compose = yaml.load(text)

    built = build_from_source(compose, base_path)
    if not built:
        sys.exit(f'{path} has none of the services built from source: {", ".join(SERVICES)}')
    print(f'Building from source: {", ".join(built)}', file=sys.stderr)
    yaml.dump(compose, sys.stdout)


if __name__ == '__main__':
    main()
