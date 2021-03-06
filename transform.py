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
"""Validate service-types.yaml; optionally generate service-types.json from it.

Usage: python transform.py [-n]

Flags:
    -n    Only perform validation - do not generate service-types.json*

If -n is not specified, two identical files will be created in pwd:
  service-types.json
  service-types.json.<version_timestamp>

These represent the data in service-types.yaml according to the schema file
published-schema.json.
"""

import datetime
import json
import subprocess
import sys

import jsonschema
import yaml

import validate


API_REF_FMT = 'https://docs.openstack.org/api-ref/{service}/'


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
            # The uri arrives with fragment removed. We assume no querystring.
            filename = uri.split('/')[-1]
            return json.load(open(filename, 'r'))
        return super(LocalResolver, self).resolve_remote(uri)


def main():
    mapping = yaml.safe_load(open('service-types.yaml', 'r'))

    mapping['version'] = datetime.datetime.utcnow().isoformat()
    mapping['sha'] = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    mapping['forward'] = {}
    mapping['reverse'] = {}
    mapping['primary_service_by_project'] = {}
    mapping['all_types_by_service_type'] = {}
    mapping['service_types_by_project'] = {}

    for service in mapping['services']:
        service_type = service['service_type']
        mapping['all_types_by_service_type'][service_type] = [service_type]
        if 'aliases' in service:
            aliases = service['aliases']
            mapping['forward'][service_type] = aliases
            mapping['all_types_by_service_type'][service_type].extend(aliases)
            for alias in aliases:
                mapping['reverse'][alias] = service_type
        for key in ('project', 'api_reference_project'):
            name = service.get(key)
            if name:
                if not service.get('secondary', False):
                    mapping['primary_service_by_project'][name] = service
                project_types = mapping['service_types_by_project'].get(
                    name, [])
                if service_type not in project_types:
                    project_types.append(service_type)
                mapping['service_types_by_project'][name] = project_types
        # Generate api_reference if not specified
        if not service.get('api_reference'):
            service['api_reference'] = API_REF_FMT.format(service=service_type)

    schema = json.load(open('published-schema.json', 'r'))
    resolver = LocalResolver.from_schema(schema)

    valid = validate.validate_all(schema, mapping, resolver=resolver)

    if valid and '-n' not in sys.argv:
        output = json.dumps(mapping, indent=2, sort_keys=True)
        output.replace(' \n', '\n')
        unversioned_filename = 'service-types.json'
        versioned_filename = 'service-types.json.{version}'.format(
            version=mapping['version'])
        for filename in (unversioned_filename, versioned_filename):
            open(filename, 'w').write(output)

    return int(not valid)


if __name__ == '__main__':
    sys.exit(main())
