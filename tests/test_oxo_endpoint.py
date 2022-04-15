import json
from pathlib import Path
import unittest

from mapping_walker.utils.sssom_utils import save_mapping_set_doc, get_iri_from_curie

from tests import INPUT_DIR, OUTPUT_DIR

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.loaders import json_loader
from mapping_walker.utils.oxo_utils import load_oxo_payload
from mapping_walker.walkers.endpoints import OxoEndpoint
from mapping_walker.walkers.mapping_walker import MappingWalker

from mapping_walker import __version__
from mapping_walker.ext_schemas.oxo import Container

OUT_FILE = Path(OUTPUT_DIR) / 'uberon-oxo-result.yaml'

class TestOxOEndpoint(unittest.TestCase):

    def test_oxo_endpoint(self):
        endpoint = OxoEndpoint()
        msdoc = endpoint.get_direct_mappings('UBERON:0013141')
        #print(yaml_dumper.dumps(msdoc.mapping_set))
        save_mapping_set_doc(msdoc, OUT_FILE)
        for m in msdoc.mapping_set.mappings:
            uri = get_iri_from_curie(m.object_id, msdoc)
            print(f'{m.object_id} = {uri}')
        
        assert any(mapping for mapping in msdoc.mapping_set.mappings if mapping.object_id == 'FMA:45632')
        assert msdoc.prefix_map['FMA']

