import unittest
from pathlib import Path

from mapping_walker.utils.sssom_utils import (get_iri_from_curie,
                                              save_mapping_set_doc)
from mapping_walker.walkers.endpoints import BioportalEndpoint

from linkml_runtime.dumpers import yaml_dumper

from tests import OUTPUT_DIR

OUT_FILE = Path(OUTPUT_DIR) / 'uberon-bioportal-result.yaml'

class TestBioPortalEndpoint(unittest.TestCase):

    def test_oxo_endpoint(self):
        endpoint = BioportalEndpoint()
        msdoc = endpoint.get_direct_mappings('UBERON:0013141')
        # print(yaml_dumper.dumps(msdoc.mapping_set))
        save_mapping_set_doc(msdoc, OUT_FILE)
        for m in msdoc.mapping_set.mappings:
            uri = get_iri_from_curie(m.object_id, msdoc)
            print(f'{m.object_id} = {uri}')
        
        assert any(mapping for mapping in msdoc.mapping_set.mappings if mapping.object_id == 'http://purl.org/obo/owlapi/fma#FMA_45632')

