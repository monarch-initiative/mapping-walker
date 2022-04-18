import logging
from dataclasses import dataclass, field
from typing import Dict, List, Union

from oaklib.datamodels.vocabulary import IS_A
from oaklib.implementations.ols.ols_implementation import OlsImplementation
from sssom.sssom_datamodel import Mapping, MappingSet, MatchTypeEnum
from sssom.sssom_document import MappingSetDocument

from mapping_walker.ext_schemas.oxo import OntologyIdentifier, ScopeEnum
from mapping_walker.pipeline.pipeline_config import EndpointConfiguration
from mapping_walker.utils.sssom_utils import curie_to_uri_map


@dataclass
class Endpoint:
    """
    Abstract class for any mapping endpoint
    """
    prefix_map: Dict[str, str] = field(default_factory=lambda: {})
    configuration: EndpointConfiguration = None

    def get_parents(self, term_id: str) -> List[str]:
        raise NotImplementedError(f'Not implemented for {self}')

    def get_ancestors(self, term_id: str) -> List[str]:
        raise NotImplementedError(f'Not implemented for {self}')

    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSetDocument:
        raise NotImplementedError(f'Not implemented for {self}')

    def fill_gaps(self, msdoc: MappingSetDocument, confidence: float = 1.0):
        raise NotImplementedError(f'Not implemented for {self}')

    def add_prefix(self, curie: str, uri: str):
        [pfx, local] = curie.split(':', 2)
        if pfx not in self.prefix_map:
            self.prefix_map[pfx] = uri.replace(local, '')


@dataclass
class OxoEndpoint(Endpoint):

    def __post_init__(self):
        self.ols = OlsImplementation()
    
    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSetDocument:
        mappings = list(self.ols.get_sssom_mappings_by_curie(curie))
        ms = MappingSet(mapping_set_id=OlsImplementation.base_url,
                          license='http://example.org/mixed',
                          mappings=mappings)
        return MappingSetDocument(mapping_set=ms,
                prefix_map=self.ols.get_prefix_map())

    def get_ancestors(self, term_id: str, ontology: str = None) -> List[str]:
        self.ols.focus_ontology = ontology
        ancs = self.ols.ancestors(term_id, predicates=[IS_A])
        return ancs

    def fill_gaps(self, msdoc: MappingSetDocument, confidence: float = 1.0) -> int:
        curie_map = curie_to_uri_map(msdoc)
        inv_map = {v: k for k, v in curie_map.items()}
        n = 0
        for curie, uri in curie_map.items():
            pfx, _ = curie.split(':', 2)
            ancs = self.get_ancestors(uri, ontology=pfx.lower())
            logging.debug(f'{curie} ANCS = {ancs}')
            for anc in ancs:
                if anc in curie_map:
                    m = Mapping(subject_id=curie,
                                object_id=anc,
                                predicate_id='rdfs:subClassOf',
                                confidence=confidence,
                                match_type=MatchTypeEnum.HumanCurated
                                )
                    logging.info(f'Gap filled link: {m}')
                    msdoc.mapping_set.mappings.append(m)
                    n += 1
        return n









@dataclass
class BioportalEndpoint(Endpoint):
    pass ## TODO


@dataclass
class UbergraphEndpoint(Endpoint):
    pass ## TODO
