RUN = poetry run

STYLE := ./conf/style.json

DMS = src/mapping_walker/ext_schemas/oxo.py


%.py: %.yaml
	$(RUN) gen-python $< > $@

JSONS=$(wildcard output/*.json)
PNGS=$(patsubst %.json, %.png, $(JSONS))

%.dot: %.json
	og2dot.js -s $(STYLE) $< >$@

%.png: %.dot
	dot $< -Tpng -Grankdir=BT >$@

pngs: $(PNGS)

%.html: %.md
	pandoc $< -o $@
