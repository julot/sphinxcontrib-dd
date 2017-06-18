import io
import os
import collections
import jsonschema
import tempfile

import yaml.resolver

from copy import deepcopy
from yaml import load as load_yaml


# This is taken from sphinxcontrib-openapi

# Dictionaries do not guarantee to preserve the keys order so when we load
# JSON or YAML - we may loose the order. In most cases it's not important
# because we're interested in data. However, in case of OpenAPI spec it'd
# be really nice to preserve them since, for example, endpoints may be
# grouped logically and that improved readability.


class Loader(yaml.SafeLoader):
    pass


Loader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: collections.OrderedDict(loader.construct_pairs(node))
)


def resolve_refs(uri, spec):
    """Resolve JSON references in a given dictionary.

    OpenAPI spec may contain JSON references to its nodes or external
    sources, so any attempt to rely that there's some expected attribute
    in the spec may fail. So we need to resolve JSON references before
    we use it (i.e. replace with referenced object). For details see:

        https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-02

    The input spec is modified in-place despite being returned from
    the function.
    """
    resolver = jsonschema.RefResolver(uri, spec)

    def _do_resolve(node):
        if isinstance(node, collections.Mapping) and '$ref' in node:
            with resolver.resolving(node['$ref']) as resolved:
                result = deepcopy(resolved)
                for key in resolved:
                    if key in node:
                        merge(result[key], node[key])
                return result
        elif isinstance(node, collections.Mapping):
            for k, v in node.items():
                node[k] = _do_resolve(v)
        elif isinstance(node, (list, tuple)):
            for i in range(len(node)):
                node[i] = _do_resolve(node[i])
        return node

    return _do_resolve(spec)


def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key].extend(b[key])
            else:
                msg = (
                    'Conflict at {0}. '
                    'Unexpected data type {1} and {2}.'
                )
                pos = '.'.join(path + [str(key)])
                raise Exception(msg.format(pos, type(a[key]), type(b[key])))

        else:
            a[key] = b[key]
    return a


def resolve_all_of(spec):
    result = collections.OrderedDict()

    for key, value in spec.items():
        if type(value) == collections.OrderedDict:
            result[key] = resolve_all_of(value)
        else:
            result[key] = value

        if key == 'allOf':
            for index, each in enumerate(value):
                if index == 0:
                    result = each
                else:
                    result = merge(result, each)

    return result


def load(path, definition_path=None):
    f = tempfile.NamedTemporaryFile(mode='w', encoding='UTF-8', delete=False)

    with open(path, encoding='utf-8') as i:
        f.write(i.read())

    if definition_path:
        f.write('\n')
        with open(definition_path, encoding='utf-8') as i:
            f.write(i.read())

    f.close()

    with io.open(f.name, 'rt', encoding='utf-8') as stream:
        spec = load_yaml(stream, Loader)

    # FIXME: Change this to function that check whether $ref key still exists
    # The problem is sometimes the key exists in dict inside list
    spec = resolve_refs('file://{0}'.format(f.name), spec)
    spec = resolve_refs('file://{0}'.format(f.name), spec)
    spec = resolve_refs('file://{0}'.format(f.name), spec)
    spec = resolve_all_of(spec)

    os.unlink(f.name)

    return spec
