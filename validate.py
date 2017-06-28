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

import json
import sys

import jsonschema
import yaml


def validate_schema(schema, data, resolver=None):
    """Validate mapping against schema using the given resolver.

    :return: An iterator over messages for any errors encountered.
    """
    validator = jsonschema.Draft4Validator(schema, resolver=resolver)
    for error in validator.iter_errors(data):
        yield error.message


def validate_unique_tokens(data):
    """Ensure service types and aliases are all unique tokens.

    :return: An iterator over messages for any errors encountered.
    """
    service_types = []
    aliases = []
    for service in data['services']:
        service_types.append(service['service_type'])
        if "aliases" in service:
            for alias in service['aliases']:
                if alias in aliases:
                    yield "Alias '{alias}' appears twice".format(alias=alias)
                aliases.append(alias)
    for alias in aliases:
        if alias in service_types:
            yield "Alias '{alias}' conflicts with a service_type".format(
                alias=alias)


def validate_all(schema, data, resolver=None):
    """Runs all validators, printing any errors to stdout.

    :return: True if all checks passed; False if any checks failed.
    """
    ret = True
    for msg in validate_schema(schema, data, resolver=resolver):
        print(msg)
        ret = False
    for msg in validate_unique_tokens(data):
        print(msg)
        ret = False
    return ret


def main():
    schema = json.load(open('schema.json', 'r'))
    data = yaml.load(open('service-types.yaml', 'r'))
    return int(not validate_all(schema, data))

if __name__ == '__main__':
    sys.exit(main())
