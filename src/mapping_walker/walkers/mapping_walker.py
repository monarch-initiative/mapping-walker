import logging
from copy import copy
from dataclasses import dataclass, field
from typing import List, Union, Tuple

from mapping_walker.walkers.endpoints import Endpoint
from sssom import MappingSet
from sssom.sssom_document import MappingSetDocument, PrefixMap
from sssom.typehints import PrefixMap
from mapping_walker.pipeline.pipeline_config import PipelineConfiguration, EndpointConfiguration

@dataclass
class MappingWalker:
    endpoints: List[Endpoint] = field(default_factory= lambda: [])

    def walk(self, curies: Union[str, List[str]], config: PipelineConfiguration = None) -> MappingSetDocument:
        """
        Iterate from a starting point of a list of curies and build out mappings

        :param curies: single curie or list of curies
        :param max_clique_size:
        :return:
        """
        if config is None:
            config = PipelineConfiguration()
        max_clique_size: int = config.max_clique_size if config.max_clique_size is not None else 100
        max_hops: int = config.max_hops if config.max_hops is not None else 3
        if not isinstance(curies, list):
            curies = [curies]
        seeds: List[Tuple[str, int]] = [(curie, 0) for curie in curies]
        visited = copy(curies)
        mapping_set = MappingSet(mapping_set_id='TODO',
                                 license='http://example.org')
        max_dist_reached = (0, None)
        while len(seeds) > 0 and len(visited) < max_clique_size:
            logging.debug(f'ITER: {len(visited)} // {seeds}')
            next_seed, dist = seeds.pop()
            if dist > max_dist_reached[0]:
                max_dist_reached = (dist, next_seed)
            if dist > max_hops:
                continue
            for endpoint in self.endpoints:
                mappings = endpoint.get_direct_mappings(next_seed).mappings
                mapping_set.mappings += mappings
                for m in mappings:
                    obj_id = m.object_id
                    if obj_id == next_seed:
                        obj_id = m.subject_id
                    logging.debug(f' CHECKING {obj_id} from {m.subject_id} <-> {m.object_id}')
                    if obj_id not in visited:
                        logging.debug(f'  ** ADDING TO SEED')
                        seeds.append((obj_id, dist+1))
                        visited.append(obj_id)
        complete = len(seeds) == 0
        mapping_set.description = f'Complete: {complete} Visited: {len(visited)} Seed: {curies} Max Distance Reached: {max_dist_reached}'
        return MappingSetDocument(mapping_set=mapping_set, prefix_map={})
