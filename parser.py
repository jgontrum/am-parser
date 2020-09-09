import os
from uuid import uuid4

from allennlp.models.archival import load_archive
from allennlp.common.util import prepare_environment
from allennlp.data.dataset_readers.dataset_reader import DatasetReader

from graph_dependency_parser.components.dataset_readers.amconll_tools import from_raw_text
from graph_dependency_parser.components.evaluation.predictors import AMconllPredictor
from graph_dependency_parser.components.spacy_interface import spacy_tokenize
from graph_dependency_parser.graph_dependency_parser import GraphDependencyParser
import graph_dependency_parser.graph_dependency_parser
import graph_dependency_parser.important_imports

from tempfile import TemporaryDirectory


# Define output graph functions

import jnius_config

class AMRInterface:
    def __init__(self, lookupdata: str, wordnet_path: str):
        from jnius import autoclass
        self.lookupdata = lookupdata
        self.wordnet_path = wordnet_path
        self.main = autoclass("de.saar.coli.amrtagging.formalisms.amr.tools.EvaluateCorpus")

    def evaluate(self, input_file: str, output_path: str) -> str:
        self.main.main(
            ["-c", input_file, "-o", output_path, "--relabel", "--wn", self.wordnet_path, "--lookup", self.lookupdata,
             "--th", "10"])
        return output_path + "/parserOut.txt"


class Parser:
    def __init__(self, archive_path, cuda_device, overrides, weights_file, lookup_path, wordnet_path, am_tools_path):
        jnius_config.set_classpath(".", am_tools_path)

        # Load model
        archive = load_archive(archive_path, cuda_device, overrides, weights_file)
        config = archive.config
        config.formalism = "DUMMY"
        prepare_environment(config)
        model = archive.model
        model.eval()
        dataset_reader = DatasetReader.from_params(config.pop('dataset_reader'))

        self.predictor = AMconllPredictor(
            dataset_reader,
            k=6,
            give_up=0,
            threads=1,
            model=model
        )

        self.formalism = AMRInterface(lookup_path, wordnet_path)


    def parse(self, sentence):
        print("")
        words = spacy_tokenize(sentence)
        am_sentence = from_raw_text(
            rawstr=sentence,
            words=words,
            add_art_root=False,
            attributes=dict(),
            contract_ne=True
        )

        with TemporaryDirectory() as direc:
            temp_path = direc + f"/sentences.amconll"
            output_filename = direc + "/parsed.amconll"

            with open(temp_path, "w") as f:
                f.write(str(am_sentence))
                f.write("\n\n")

            self.predictor.parse_and_save(
                formalism="AMR-2017",
                input_file=temp_path,
                output_file=output_filename
            )

            interpreted_output = self.formalism.evaluate(output_filename, direc)

            with open(interpreted_output) as f:
                return str(f.read()).rstrip()
