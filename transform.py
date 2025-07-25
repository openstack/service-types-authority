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

"""Validate and optionally generate the services-types documents."""

import argparse
import datetime
import json
import subprocess
import sys

import referencing
import yaml

import validate

API_REF_FMT = 'https://docs.openstack.org/api-ref/{service}/'


def create_local_registry():
    """Create a referencing registry that uses local spec files.

    This registry contains the spec, and the specs are used against data in
    gating jobs to validate consistency. However, the specs use URIs to
    refer to each other for external consumption, which makes gating
    changes tricky. Instead of fetching from the already published spec,
    use the local one so that changes can be self-gating.
    """

    def local_retrieve(uri: str):
        if uri.startswith('https://specs.openstack.org'):
            # The URI arrives with fragment removed. We assume no querystring.
            filename = uri.split('/')[-1]
            with open(filename) as fh:
                return referencing.Resource.from_contents(json.load(fh))
        # We shouldn't have any external URIs. Scream bloody murder if someone
        # tries.
        raise referencing.exceptions.NoSuchResource(ref=uri)

    return referencing.Registry(retrieve=local_retrieve)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            'Validate service-types.yaml; optionally generating '
            'service-types.json from it.'
        ),
        epilog=(
            'If -n is not specified, two identical files will be created in '
            'pwd:\n'
            '\n'
            '  service-types.json\n'
            '  service-types.json.<version_timestamp>\n'
            '\n'
            'These represent the data in service-types.yaml according to the '
            'schema file\n'
            'published-schema.json.'
        ),
    )
    parser.add_argument(
        '-n',
        action='store_false',
        dest='enable_generation',
        default=True,
        help='only perform validation - do not generate service-types.json',
    )
    args = parser.parse_args()

    with open('service-types.yaml') as fh:
        mapping = yaml.safe_load(fh)

    # we are using a TZ-naive timestamp for legacy reasons, but we should
    # probably revisit this as TZ-naive timestamps are a menace
    #
    # https://nerderati.com/a-python-epoch-timestamp-timezone-trap/
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

    mapping['version'] = now.isoformat()
    mapping['sha'] = (
        subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        .decode('utf-8')
        .strip()
    )
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
                    name, []
                )
                if service_type not in project_types:
                    project_types.append(service_type)
                mapping['service_types_by_project'][name] = project_types
        # Generate api_reference if not specified
        if not service.get('api_reference'):
            service['api_reference'] = API_REF_FMT.format(service=service_type)

    with open('published-schema.json') as fh:
        schema = json.load(fh)

    registry = create_local_registry()

    valid = validate.validate_all(schema, mapping, registry=registry)

    if valid and args.enable_generation:
        output = json.dumps(mapping, indent=2, sort_keys=True)
        output.replace(' \n', '\n')
        unversioned_filename = 'service-types.json'
        versioned_filename = f'service-types.json.{mapping["version"]}'
        for filename in (unversioned_filename, versioned_filename):
            with open(filename, 'w') as fh:
                fh.write(output)

    return int(not valid)


if __name__ == '__main__':
    sys.exit(main())
