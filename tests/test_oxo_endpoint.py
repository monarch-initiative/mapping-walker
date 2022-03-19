import json
from pathlib import Path

from tests import INPUT_DIR, OUTPUT_DIR

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.loaders import json_loader
from mapping_walker.utils.oxo_utils import load_oxo_payload
from mapping_walker.walkers.endpoints import OxoEndpoint
from mapping_walker.walkers.mapping_walker import MappingWalker

from mapping_walker import __version__
from mapping_walker.ext_schemas.oxo import Container


def test_oxo_endpoint():
    endpoint = OxoEndpoint()
    mapping_set = endpoint.get_direct_mappings('UBERON:0013141')
    print(yaml_dumper.dumps(mapping_set))

