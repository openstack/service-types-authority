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

import sys

import jsonschema


def validate_schema(schema, data, registry):
    """Validate mapping against schema using the given registry.

    :return: An iterator over messages for any errors encountered.
    """
    validator = jsonschema.Draft202012Validator(schema, registry=registry)
    for error in validator.iter_errors(data):
        yield error.message


def validate_unique_tokens(data):
    """Ensure service types, aliases and primary projects are all unique.

    :return: An iterator over messages for any errors encountered.
    """
    service_types = []
    aliases = []
    projects = []
    for service in data['services']:
        service_types.append(service['service_type'])
        if 'aliases' in service:
            for alias in service['aliases']:
                if alias in aliases:
                    yield f"Alias '{alias}' appears twice"
                aliases.append(alias)
        if service.get('secondary', False):
            continue
        if service['project'] in projects:
            yield (
                f"'{service['service_type']}' duplicates service from "
                f"'{service['project']}'"
            )
        projects.append(service['project'])
    for alias in aliases:
        if alias in service_types:
            yield f"Alias '{alias}' conflicts with a service_type"


def validate_api_reference(data):
    """Ensure api_reference matches the retired state of each service.

    Retired services must have a null api_reference, while all other
    services must have a published API reference document.

    :return: An iterator over messages for any errors encountered.
    """
    for service in data['services']:
        service_type = service['service_type']
        if service.get('retired'):
            if service.get('api_reference'):
                yield (
                    f"'{service_type}' is retired but has an api_reference"
                )
        elif not service.get('api_reference'):
            yield f"'{service_type}' is not retired and needs an api_reference"


def validate_all(schema, data, registry):
    """Runs all validators, printing any errors to stderr.

    :return: True if all checks passed; False if any checks failed.
    """
    ret = True
    for msg in validate_schema(schema, data, registry):
        print(msg, file=sys.stderr)
        ret = False
    for msg in validate_unique_tokens(data):
        print(msg, file=sys.stderr)
        ret = False
    for msg in validate_api_reference(data):
        print(msg, file=sys.stderr)
        ret = False
    return ret
