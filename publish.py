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

import glob
import json
import operator
import os
import shutil
import sys

import requests

HTTP_LOCATION = 'https://service-types.openstack.org/service-types.json'
OUTDIR = 'publish'
HEADER = '''<div class="section" id="service-types-authority">
<h1>OpenStack Service Types Authority Data</h1>
<p>For more information on the files, see:
    <a href='http://specs.openstack.org/openstack/service-types-authority/'>
    http://specs.openstack.org/openstack/service-types-authority/</a></p>
<p>For more information on using the information, see:
    <a href='http://specs.openstack.org/openstack/api-wg/'>
    http://specs.openstack.org/openstack/api-wg/</a></p>
<p>The canonical source data is kept in git at:
    <a href='https://git.openstack.org/cgit/openstack/service-types-authority'>
    https://git.openstack.org/cgit/openstack/service-types-authority</a></p>
</div>
'''


def is_data_equal(old, new):
    # Check specific data - largely because services is a list where order
    # does not matter, and version/sha are always going to be different.
    # Order DOES matter in alias lists and mappings though, so just do
    # normal equality on the service dicts and reverse and forward mappings.
    if old.keys() != new.keys():
        return False
    if (sorted(old['services'], key=operator.itemgetter('service_type')) !=
            sorted(new['services'], key=operator.itemgetter('service_type'))):
        return False
    if old['reverse'] != new['reverse']:
        return False
    if old['forward'] != new['forward']:
        return False
    return True


def should_publish_data():
    current_contents = json.load(open('service-types.json', 'r'))

    try:
        response = requests.get(HTTP_LOCATION)
        response.raise_for_status()
        existing_contents = response.json()
    except (requests.HTTPError, requests.ConnectionError) as e:
        print("Failed to fetch current service-types.json. Assuming data"
              " needs to be published. Error: {error}".format(error=str(e)))
        return (True, current_contents['version'])

    # If our contents are not the same as published, we need to publish
    should_publish = not is_data_equal(existing_contents, current_contents)
    if should_publish:
        return (True, current_contents['version'])
    else:
        return (False, existing_contents['version'])


def main():
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
    elif not os.path.isdir(OUTDIR):
        print(
            "{outdir} exists but is not a directory. Aborting!".format(
                outdir=OUTDIR))
        return 1

    # It's fine to always copy json schema and yaml source
    # The source yaml file can change in ways that don't affect the json output
    # The schema can update - descriptions can be cleaned up, format regexes
    # can get fixed.
    # schema updates that don't work with the existing file won't land (we
    # gate on them).
    to_copy = glob.glob('*schema.json') + glob.glob('*.yaml')
    should_publish, latest_version = should_publish_data()
    if should_publish:
        to_copy += glob.glob('service-types.json*')
    else:
        print("Data in existing file matches {version} data."
              " Not publishing".format(version=latest_version))

    for filename in to_copy:
        shutil.copyfile(filename, os.path.join(OUTDIR, filename))

    latest_file = 'service-types.json.{version}'.format(version=latest_version)
    with open('publish/HEADER.html', 'w') as header:
        header.write(HEADER)
        header.write(
            '<h2>Latest file is <a href="./{fn}">{fn}</a></h2>\n'.format(
                fn=latest_file))
    return 0


if __name__ == '__main__':
    sys.exit(main())
