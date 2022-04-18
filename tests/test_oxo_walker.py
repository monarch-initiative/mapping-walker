import json
from pathlib import Path
import unittest

from mapping_walker.pipeline.pipeline_config import PipelineConfiguration
from mapping_walker.utils.sssom_utils import load_mapping_set_doc, save_mapping_set_doc

from tests import INPUT_DIR, OUTPUT_DIR

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.loaders import json_loader
from mapping_walker.utils.oxo_utils import load_oxo_payload
from mapping_walker.walkers.endpoints import OxoEndpoint
from mapping_walker.walkers.mapping_walker import MappingWalker

from mapping_walker import __version__
from mapping_walker.ext_schemas.oxo import Container

#CURIE = 'MONDO:0019391'
CURIE = 'UBERON:0013141'


class TestOxOWalker(unittest.TestCase):
    def test_oxo_walker(self):
        """
        Tests iterative walking over OxO endpoint
        """
        endpoint = OxoEndpoint()
        walker = MappingWalker(endpoints=[endpoint])
        config = PipelineConfiguration(max_clique_size=100, max_hops=3)
        msdoc = walker.walk(CURIE, config=config)
        assert len(msdoc.mapping_set.mappings) > 4
        with open(str(Path(OUTPUT_DIR) / 'oxo-walk.yaml'), 'w', encoding='utf-8') as stream:
            stream.write(yaml_dumper.dumps(msdoc.mapping_set))

    def test_oxo_fill_gaps(self):
        """
        uses a predefined mapping file to test gap-filling using OLS
        :return:
        """
        msdoc = load_mapping_set_doc(str(Path(INPUT_DIR) / 'neoplasm.sssom.yaml'))
        endpoint = OxoEndpoint()
        n = endpoint.fill_gaps(msdoc)
        print(n)
        save_mapping_set_doc(msdoc, str(Path(OUTPUT_DIR) / 'neoplasm-gap-filled.sssom.yaml'))
        for m in msdoc.mapping_set.mappings:
            if m.predicate_id == 'rdfs:subClassOf':
                print(yaml_dumper.dumps(m))
        assert n > 0
