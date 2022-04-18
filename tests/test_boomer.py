import json
from pathlib import Path
import unittest

from linkml_runtime.loaders import json_loader, yaml_loader
from mapping_walker.pipeline.pipeline import Pipeline
from sssom import MappingSet
from sssom.sssom_document import MappingSetDocument

from tests import INPUT_DIR, OUTPUT_DIR

class TestBoomer(unittest.TestCase):

    def test_outputs(self):
        infile = str(Path(INPUT_DIR) / 'oxo-walk.yaml')
        mapping_set = yaml_loader.load(infile, target_class=MappingSet)
        doc = MappingSetDocument(mapping_set=mapping_set, prefix_map={})
        boomer = Pipeline()
        with open(str(Path(OUTPUT_DIR) / 'oxo-walk.ptable.tsv'), 'w', encoding='utf-8') as stream:
            boomer.write_ptable(doc, output=stream)
        boomer.write_ontology(doc, str(Path(OUTPUT_DIR) / 'oxo-walk.ontology.ttl'))
        with open(str(Path(OUTPUT_DIR) / 'oxo-walk.prefixes.yaml'), 'w', encoding='utf-8') as stream:
            boomer.write_prefixmap(doc, output=stream)


