# Copyright (c) 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
import subprocess
import sys

import jsonschema
import yaml


class LocalResolver(jsonschema.RefResolver):
    """Local Resolver class that uses the spec from this repo.

    This repo contains the spec, and the specs are used against data in
    gating jobs to validate consistency. However, the specs use URIs to
    refer to each other for external consumption, which makes gating
    changes tricky. Instead of fetching from the already published spec,
    use the local one so that changes can be self-gating.
    """

    def resolve_remote(self, uri):
        if uri.startswith('https://specs.openstack.org'):
            filename = os.path.split(uri)[-1]
            return json.load(open(filename, 'r'))
        return super(LocalResolver, self).resolve_remote(uri)


def main():
    ret = 0
    mapping = yaml.load(open('service-types.yaml', 'r'))

    mapping['version'] = datetime.datetime.utcnow().isoformat()
    mapping['sha'] = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']).strip()
    mapping['forward'] = {}
    mapping['reverse'] = {}

    for service in mapping['services']:
        service_type = service['service_type']
        if 'aliases' in service:
            aliases = service['aliases']
            mapping['forward'][service_type] = aliases
            for alias in aliases:
                mapping['reverse'][alias] = service_type

    schema = json.load(open('published-schema.json', 'r'))
    resolver = LocalResolver.from_schema(schema)
    validator = jsonschema.Draft4Validator(schema, resolver=resolver)
    for error in validator.iter_errors(mapping):
        print(error.message)
        ret = 1

    if '-n' not in sys.argv:
        json.dump(mapping, open('service-types.json', 'w'), indent=2)
        versioned_file_name = 'service-types.json.{version}'.format(
            version=mapping['version'])
        json.dump(mapping, open(versioned_file_name, 'w'), indent=2)

    return ret


if __name__ == '__main__':
    sys.exit(main())
