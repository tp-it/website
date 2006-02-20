#!/usr/bin/env python2.4
# -*- coding: UTF-8 -*-
#
# Ordina le voci del Glossario dei traduttori di programmi liberi,
# disponibile presso: http://www.linux.it/tp/glossario.html
#
# Copyright © 2006 Danilo Piazzalunga <danilopiazza@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the BSD license.
#

import sys
import re

from xml.dom import minidom

default_encoding = "UTF-8"

# Regole predefinite per costruire la chiave di ordinamento
default_sorting_rules = \
    (
        # Elimina parole tra parentesi, barre e trattini.
        ("(/|-|\(.*?\))\s*", ""),
        # Posiziona i verbi prima dei sostantivi, mantenendo l'ordinamento delle
        # altre parole (es. "route" < "router" e "name server" < "named pipe").
        ("\s+", "0"),
        (",[0 ]to$", " 000"),
        ("$", " zzz")
    )

def parse_document(docfile):
    """Carica il documento e ne analizza la struttura"""
    doc = minidom.parse(docfile)

    sanity_checks(doc)

    return doc

def sanity_checks(doc):
    """Esegue controlli sulla struttura del documento"""
    dtelems = [e for e in doc.getElementsByTagName("dt")
        if e.attributes["xml:lang"].value == "en"]

    # Gli elementi <dt> sono tutti e soli i termini del glossario.
    alldtelems = doc.getElementsByTagName("dt")
    assert dtelems == alldtelems

    # C'è una sola lista <ul> che contiene un elemento per definizione.
    ulelems = doc.getElementsByTagName("ul")
    lielems = get_li_elements(doc, ulelems[0])
    assert len(ulelems) == 1
    assert len(lielems) == len(dtelems)

def get_ul_element(doc):
    return doc.getElementsByTagName("ul")[0]

def get_li_elements(doc, ul):
    return [e for e in ul.childNodes
        if e.nodeType == e.ELEMENT_NODE and e.tagName == "li"]

def sorting_key(li):
    """Costruisce la chiave di ordinamento applicando regole opportune"""
    k = li.getElementsByTagName("dt")[0].firstChild.data.lower()

    for rule in default_sorting_rules:
        k = re.sub(rule[0], rule[1], k)

    return k

def sort_definitions(docfile):
    """Ordina le definizioni del glossario secondo la chiave specificata"""
    doc = parse_document(docfile)
    ul = get_ul_element(doc)
    lielems = get_li_elements(doc,ul)

    # Rimuove tutti gli elementi dalla lista...
    while ul.childNodes: ul.removeChild(ul.firstChild)
    assert not ul.hasChildNodes()
    # ... e li riaggiunge una volta ordinati.
    for child in sorted(lielems, key=sorting_key):
        ul.appendChild(child)
    assert len(ul.childNodes) == len(lielems)

    return doc

def main():
    if len(sys.argv) < 2:
        print >> sys.stderr, \
            "uso: %s [opzioni] glossario.html" % sys.argv[0]
        sys.exit(2)

    if sys.argv[1] == "-": docfile = sys.stdin
    else: docfile = sys.argv[1]

    print sort_definitions(docfile).toxml(encoding=default_encoding)

if __name__ == "__main__":
    main()
