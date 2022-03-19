import logging
from dataclasses import dataclass, field
from typing import Union, Dict

import requests
from mapping_walker.ext_schemas.oxo import Container, OntologyIdentifier, ScopeEnum
from mapping_walker.utils.oxo_utils import load_oxo_payload
from sssom.sssom_datamodel import MappingSet, Mapping, MatchTypeEnum

from mapping_walker.pipeline.pipeline_config import PipelineConfiguration, EndpointConfiguration

oxo_pred_mappings = {
    ScopeEnum.EXACT.text: 'skos:exactMatch',
    ScopeEnum.BROADER.text: 'skos:broadMatch',
    ScopeEnum.NARROWER.text: 'skos:narrowMatch',
    ScopeEnum.RELATED.text: 'skos:closeMatch',
}

@dataclass
class Endpoint:
    """
    Abstract class for any mapping endpoint
    """
    prefix_map: Dict[str, str] = field(default_factory=lambda: {})
    configuration: EndpointConfiguration = None

    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSet:
        raise NotImplementedError(f'Not implemented for {self}')


@dataclass
class OxoEndpoint(Endpoint):
    base_url = "https://www.ebi.ac.uk/spot/oxo/api/mappings"

    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSet:
        result = requests.get(self.base_url, params=dict(fromId=curie))
        obj = result.json()
        container = load_oxo_payload(obj)
        return self.convert_payload(container)

    def convert_payload(self, container: Container) -> MappingSet:
        oxo_mappings = container._embedded.mappings
        mappings: Mapping = []
        for oxo_mapping in oxo_mappings:
            oxo_s = oxo_mapping.fromTerm
            oxo_o = oxo_mapping.toTerm
            logging.debug(f' xx SCOPE={oxo_mapping.scope}')
            mapping = Mapping(subject_id=oxo_s.curie,
                              subject_label=oxo_s.label,
                              subject_source=oxo_s.datasource.prefix if oxo_s.datasource else None,
                              predicate_id=oxo_pred_mappings[str(oxo_mapping.scope)],
                              match_type=MatchTypeEnum.Unspecified,
                              object_id=oxo_o.curie,
                              object_label=oxo_o.label,
                              object_source=oxo_o.datasource.prefix if oxo_o.datasource else None,
                              mapping_provider=oxo_mapping.datasource.prefix)
            self.add_prefix(oxo_s.curie, oxo_s.uri)
            self.add_prefix(oxo_o.curie, oxo_o.uri)
            mappings.append(mapping)
        return MappingSet(mapping_set_id=container._links.link_to_self.href,
                          license='http://example.org/mixed',
                          mappings=mappings)


    def add_prefix(self, curie: str, uri: str):
        [pfx, local] = curie.split(':', 2)
        if pfx not in self.prefix_map:
            self.prefix_map[pfx] = uri.replace(local, '')



@dataclass
class BioportalEndpoint(Endpoint):
    pass ## TODO


@dataclass
class UbergraphEndpoint(Endpoint):
    pass ## TODO
