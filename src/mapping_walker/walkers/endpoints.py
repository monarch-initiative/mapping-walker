import logging
from dataclasses import dataclass, field
from typing import Union, Dict, List

import requests
import urllib
from mapping_walker.ext_schemas.oxo import Container, OntologyIdentifier, ScopeEnum
from mapping_walker.utils.oxo_utils import load_oxo_payload
from mapping_walker.utils.sssom_utils import all_curies_in_doc, get_iri_from_curie, curie_to_uri_map
from sssom.sssom_datamodel import MappingSet, Mapping, MatchTypeEnum

from mapping_walker.pipeline.pipeline_config import PipelineConfiguration, EndpointConfiguration
from sssom.sssom_document import MappingSetDocument

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
    base_url = "https://www.ebi.ac.uk/spot/oxo/api/mappings"
    ols_base_url = "https://www.ebi.ac.uk/ols/api/ontologies/"

    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSetDocument:
        result = requests.get(self.base_url, params=dict(fromId=curie))
        obj = result.json()
        container = load_oxo_payload(obj)
        return self.convert_payload(container)

    def convert_payload(self, container: Container) -> MappingSetDocument:
        oxo_mappings = container._embedded.mappings
        mappings: Mapping = []
        for oxo_mapping in oxo_mappings:
            oxo_s = oxo_mapping.fromTerm
            oxo_o = oxo_mapping.toTerm
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
        ms = MappingSet(mapping_set_id=container._links.link_to_self.href,
                          license='http://example.org/mixed',
                          mappings=mappings)
        return MappingSetDocument(mapping_set=ms,
                                  prefix_map=self.prefix_map)

    def get_ancestors(self, term_id: str, ontology: str = None) -> List[str]:
        # must be double encoded https://www.ebi.ac.uk/ols/docs/api
        term_id_quoted = urllib.parse.quote(term_id, safe='')
        term_id_quoted = urllib.parse.quote(term_id_quoted, safe='')
        url = f'{self.ols_base_url}{ontology}/terms/{term_id_quoted}/ancestors'
        logging.debug(f'URL={url}')
        result = requests.get(url)
        obj = result.json()
        if result.status_code == 200 and '_embedded' in obj:
            ancs = [x['obo_id'] for x in obj['_embedded']['terms']]
        else:
            logging.debug(f'No ancestors for {url} (maybe ontology not indexed in OLS?)')
            ancs = []
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
