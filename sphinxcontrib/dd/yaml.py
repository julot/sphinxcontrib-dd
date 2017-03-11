import io
import os
import collections
import jsonschema
import tempfile

import yaml.resolver

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
                return resolved
        elif isinstance(node, collections.Mapping):
            for k, v in node.items():
                node[k] = _do_resolve(v)
        elif isinstance(node, (list, tuple)):
            for i in range(len(node)):
                node[i] = _do_resolve(node[i])
        return node

    return _do_resolve(spec)


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
    spec = resolve_refs('file://{0}'.format(f.name), spec)

    os.unlink(f.name)

    return spec
