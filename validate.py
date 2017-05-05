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


def main():
    ret = 0
    schema = json.load(open('schema.json', 'r'))
    validator = jsonschema.Draft4Validator(schema)
    data = yaml.load(open('service-types.yaml', 'r'))
    for error in validator.iter_errors(data):
        print(error.message)
        ret = 1
    service_types = []
    aliases = []
    for service in data['services']:
        service_types.append(service['service_type'])
        if "aliases" in service:
            for alias in service['aliases']:
                if alias in aliases:
                    print("Alias {alias} appears twice".format(alias=alias))
                    ret = 1
                aliases.append(alias)
    for alias in aliases:
        if alias in service_types:
            print("Alias {alias} conflicts with a service_type".format(
                alias=alias))
            ret = 1
    return ret


if __name__ == '__main__':
    sys.exit(main())
