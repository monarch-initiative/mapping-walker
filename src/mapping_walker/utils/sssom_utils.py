from typing import List, Dict

import yaml
from linkml_runtime.dumpers import yaml_dumper, json_dumper
from linkml_runtime.loaders import json_loader
from rdflib import URIRef
from sssom import MappingSet
from sssom.sssom_document import MappingSetDocument
import bioregistry

priority = ["obofoundry", "default", "miriam", "ols", "n2t", "bioportal"]

def guess_prefix_expansion(pfx) -> str:
    """
    Guess a prefix expansion using bioregistry
    :param pfx:
    :return:
    """
    return bioregistry.get_iri(pfx, "", priority=priority)

def merge_mapping_set_docs(tgt: MappingSetDocument, src: MappingSetDocument):
    """
    Merges source into target

    :param tgt:
    :param src:
    :return:
    """
    tgt.mapping_set.mappings += src.mapping_set.mappings
    tgt.prefix_map = {**tgt.prefix_map, **src.prefix_map}

def save_mapping_set_doc(msdoc: MappingSetDocument, destination: str):
    """
    Saves document to a yaml file

    :param msdoc:
    :param destination:
    :return:
    """
    ms_obj = json_dumper.to_dict(msdoc.mapping_set)
    with open(destination, 'w', encoding='utf-8') as stream:
        yaml.dump({"mapping_set": ms_obj, "prefix_map": msdoc.prefix_map}, stream)

def load_mapping_set_doc(path: str) -> MappingSetDocument:
    """
    Loads document from a yaml file

    :param path:
    :return:
    """
    with open(path) as stream:
        obj = yaml.safe_load(stream)
        mapping_set = json_loader.load(obj['mapping_set'], target_class=MappingSet)
        return MappingSetDocument(mapping_set=mapping_set, prefix_map=obj['prefix_map'])

def all_curies_in_doc(msdoc: MappingSetDocument) -> List[str]:
    """
    all referenced CURIEs

    :param msdoc:
    :return:
    """
    curies = set()
    for m in msdoc.mapping_set.mappings:
        curies.add(m.subject_id)
        curies.add(m.object_id)
    return list(curies)


def all_uris_in_doc(msdoc: MappingSetDocument) -> List[URIRef]:
    """
    all referenced CURIEs

    :param msdoc:
    :return:
    """
    uris = set()
    for m in msdoc.mapping_set.mappings:
        uris.add(get_iri_from_curie(m.subject_id, msdoc))
        uris.add(get_iri_from_curie(m.object_id, msdoc))
    return list(uris)


def curie_to_uri_map(msdoc: MappingSetDocument) -> Dict[str, URIRef]:
    """
    all referenced CURIEs

    :param msdoc:
    :return:
    """
    d = {}
    for m in msdoc.mapping_set.mappings:
        d[m.subject_id] = get_iri_from_curie(m.subject_id, msdoc)
        d[m.object_id] = get_iri_from_curie(m.object_id, msdoc)
    return d


def fix_prefixes(msdoc: MappingSetDocument):
    """
    Repairs prefixmap in place

    :param msdoc:
    :return:
    """
    for m in msdoc.mapping_set.mappings:
        get_iri_from_curie(m.subject_id, msdoc)
        get_iri_from_curie(m.object_id, msdoc)

def get_iri_from_curie(curie: str, msdoc: MappingSetDocument) -> URIRef:
    """
    Expand a CURIE

    :param curie:
    :param msdoc:
    :return:
    """
    if ':' not in curie:
        raise ValueError(f'BASE: {curie}')
    pfx, local = curie.split(':', 2)
    if pfx in msdoc.prefix_map and msdoc.prefix_map[pfx] != '':
        uri_base = msdoc.prefix_map[pfx]
    else:
        uri_base = guess_prefix_expansion(pfx)
        if uri_base is None:
            uri_base = f'http://purl.obolibrary.org/obo/{pfx}_'
        msdoc.prefix_map[pfx] = uri_base
    return URIRef(f'{uri_base}{local}')
