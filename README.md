# Mapping Walker

This application will:

 - crawl a mapping endpoint weaving a set of SSSOM mappings
 - input these into boomer
 - visualize the results with obographviz

__THIS IS ALPHA SOFTWARE__

## Requirements

You need the following on your path:

 - boomer
 - og2dot

## Running

```bash
mapcrawl OMIM:603467
```

you can enter as many CURIEs as you like

The output looks like:

![img](./docs/images/omim-example.png)

Note the visualization doesn't show the mappings that were rejected - see the full boomer report file. It shows things like:

- [Fanconi anemia](http://purl.obolibrary.org/obo/Orphanet_84) SiblingOf [](http://purl.obolibrary.org/obo/OMIM_614087)         0.09999999999999998
- [Fanconi anemia](http://purl.obolibrary.org/obo/Orphanet_84) ProperSuperClassOf [](http://purl.obolibrary.org/obo/OMIM_603467)        (most probable) 0.8
- [aplastic anemia](http://purl.obolibrary.org/obo/MONDO_0015909) EquivalentTo [Anemia, Aplastic](http://purl.obolibrary.org/obo/MeSH_D000741)  (most probable) 0.8
- [Fanconi anemia](http://purl.obolibrary.org/obo/DOID_13636) EquivalentTo [Fanconi Anemia](http://purl.obolibrary.org/obo/MeSH_D005199)        (most probable) 0.8


## Gallery


### Anatomy

* FMA:24879

![FMA:24879](./docs/images/fma-example.png)


### Disease

MONDO:0019249 ! mucopolysaccharidosis


![mucopolysaccharidosis](./docs/images/muco-example.png)

## How it works

It currently queries OxO - it will do a breadth first search until either saturated or either max depth or max queries is reached

All configuration is specified in LinkML yaml - docs will be up soon

Currently it applies the standard SSSOM-py mappings for all predicates obtained from OxO (most mappings in OxO are RELATED but there are some narrow/broad)

Default confidence is 0.8 (currently no mappings in OxO have confidence)

We don't yet allow plugin in of rules - e.g. boost confidence if mapping comes from a more trusted source, or is HumanCurated

## TODO

- add bioportal endpoint (currently uses oxo)
- add ubergraph endpoint



