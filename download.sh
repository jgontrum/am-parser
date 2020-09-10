#!/bin/bash

am_tools_url="http://www.coli.uni-saarland.de/projects/amparser/am-tools.jar"
model_url="http://www.coli.uni-saarland.de/projects/amparser/raw_text_model.tar.gz"
ner_url="https://nlp.stanford.edu/software/stanford-ner-2018-10-16.zip"
pos_url="https://nlp.stanford.edu/software/stanford-postagger-2018-10-16.zip"
wordnet_url="http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz"
lookup15_url="http://www.coli.uni-saarland.de/projects/amparser/lookupdata15.zip"

if [ ! -f am-tools.jar ]; then
	curl -OL $am_tools_url
fi

if [ ! -f raw_text_model.tar.gz ]; then
	curl -OL $model_url
fi

mkdir -p stanford
if [ ! -f stanford/english.conll.4class.distsim.crf.ser.gz ]; then
	curl -OL $ner_url
	mkdir -p tmp
	unzip stanford-ner-2018-10-16.zip -d tmp/
	mv tmp/stanford-ner-2018-10-16/classifiers/english.conll.4class.distsim.crf.ser.gz stanford/english.conll.4class.distsim.crf.ser.gz
	rm -rf tmp stanford-ner-2018-10-16.zip
fi

if [ ! -f stanford/english-bidirectional-distsim.tagger ]; then
	curl -OL $pos_url
	mkdir -p tmp
	unzip stanford-postagger-2018-10-16.zip -d tmp/
	mv tmp/stanford-postagger-2018-10-16/models/english-bidirectional-distsim.tagger stanford/english-bidirectional-distsim.tagger
	rm -rf tmp stanford-postagger-2018-10-16.zip
fi

if [ ! -d wordnet3.0 ]; then
	curl -OL $wordnet_url
	mkdir -p tmp
	tar -xzvf WordNet-3.0.tar.gz -C tmp
	mkdir -p wordnet3.0
	mv tmp/WordNet-3.0/dict wordnet3.0/
	rm -rf tmp WordNet-3.0.tar.gz
fi

if [ ! -d lookup/lookupdata17 ]; then
	curl -OL $lookup17_url
	unzip lookupdata17.zip -d lookup/
	rm lookupdata17.zip
fi
