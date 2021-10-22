#!/usr/bin/env python3
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import json
import re
import sys
import textwrap

import requests


def to_underscores(item):
    words = re.findall(r'[A-Z](?:[a-z0-9]+|[A-Z0-9]*(?=[A-Z]|$))', item)
    return '_'.join(w.upper() for w in words)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL of a DMTF definition")
    parser.add_argument("name", help="name of the enumeration")
    parser.add_argument("--compat", help="generate old-style constants",
                        action="store_true")
    args = parser.parse_args()

    if args.url.startswith("https://") or args.url.startswith("http://"):
        resp = requests.get(args.url)
        resp.raise_for_status()
        content = resp.json()
    else:
        with open(args.url, "t") as fp:
            content = json.load(fp)

    try:
        definition = content["definitions"][args.name]
    except KeyError as exc:
        sys.exit(f"Key {exc} was not found in definition at {args.url}")

    try:
        items = definition["enum"]
        descriptions = definition.get("enumDescriptions", {})
    except (TypeError, KeyError):
        sys.exit(f"Definition {args.name} is malformed or not en enumeration")

    items = [(to_underscores(item), item) for item in items]

    print(f"class {args.name}(enum.Enum):")
    for varname, item in items:
        print(f"    {varname} = '{item}'")

        try:
            description = descriptions[item]
        except KeyError:
            pass
        else:
            # 79 (expected) - 4 (indentation) - 2 * 3 (quotes) = 69
            lines = textwrap.wrap(description, 69)
            lines[0] = '"""' + lines[0]
            lines[-1] += '"""'
            for line in lines:
                print(f'    {line}')
        print()

    if args.compat:
        print()
        print("# Backward compatibility")
        for varname, item in items:
            print(f"{to_underscores(args.name)}_{varname} = "
                  f"{args.name}.{varname}")


if __name__ == '__main__':
    sys.exit(main())
