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

import argparse
import glob
import json
import operator
import os
import shutil
import sys

import requests

HTTP_LOCATION = 'https://service-types.openstack.org/service-types.json'
SPECS_BASE = 'http://specs.openstack.org/openstack'
OUTDIR = 'doc/build/html'
HEADER = """<div class="section" id="service-types-authority">
<h1>OpenStack Service Types Authority Data</h1>
<p>For more information on the files, see:
    <a href='{specs_base}/service-types-authority'>
    {specs_base}/service-types-authority</a></p>
<p>For more information on using the information, see:
    <a href='{specs_base}/api-wg/'>
    {specs_base}/api-wg/</a></p>
<p>The canonical source data is kept in git at:
    <a href='https://opendev.org/openstack/service-types-authority'>
    https://opendev.org/openstack/service-types-authority</a></p>
<p>The canonical YAML source can be found at:
    <a href='{specs_base}/service-types-authority/#service-data'>
    {specs_base}/service-types-authority/#service-data
    </a></p>
</div>
<h2>Latest file is <a href="./{latest_file}">{latest_file}</a></h2>
"""


def is_data_equal(old, new):
    # Check specific data - largely because services is a list where order
    # does not matter, and version/sha are always going to be different.
    # Order DOES matter in alias lists and mappings though, so just do
    # normal equality on the service dicts and reverse and forward mappings.
    if old.keys() != new.keys():
        return False
    if sorted(
        old['services'], key=operator.itemgetter('service_type')
    ) != sorted(new['services'], key=operator.itemgetter('service_type')):
        return False
    if old['reverse'] != new['reverse']:
        return False
    if old['forward'] != new['forward']:
        return False
    return True


def should_publish_data():
    with open('service-types.json') as fh:
        current_contents = json.load(fh)

    try:
        response = requests.get(HTTP_LOCATION)
        response.raise_for_status()
        existing_contents = response.json()
    except (requests.HTTPError, requests.ConnectionError) as e:
        print(
            f'Failed to fetch current service-types.json. Assuming data '
            f'needs to be published. Error: {str(e)}',
            file=sys.stderr,
        )
        return (True, current_contents['version'])

    # If our contents are not the same as published, we need to publish
    should_publish = not is_data_equal(existing_contents, current_contents)
    if should_publish:
        return (True, current_contents['version'])
    else:
        return (False, existing_contents['version'])


def main():
    parser = argparse.ArgumentParser(
        description='Generate HTML documents for publication'
    )
    parser.parse_args()

    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
    elif not os.path.isdir(OUTDIR):
        print(
            f'{OUTDIR} exists but is not a directory. Aborting!',
            file=sys.stderr,
        )
        return 1

    # It's fine to always copy the json schema
    # The schema can update - descriptions can be cleaned up, format regexes
    # can get fixed.
    # schema updates that don't work with the existing file won't land (we
    # gate on them).
    to_copy = glob.glob('*schema.json')
    should_publish, latest_version = should_publish_data()
    if should_publish:
        to_copy += glob.glob('service-types.json*')
    else:
        print(
            f'Data in existing file matches {latest_version} data. '
            f'Not publishing',
            file=sys.stderr,
        )

    for filename in to_copy:
        shutil.copyfile(filename, os.path.join(OUTDIR, filename))

    latest_file = f'service-types.json.{latest_version}'
    with open(f'{OUTDIR}/HEADER.html', 'w') as header:
        header.write(
            HEADER.format(latest_file=latest_file, specs_base=SPECS_BASE)
        )
    return 0


if __name__ == '__main__':
    sys.exit(main())
