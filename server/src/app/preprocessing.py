import os, spacy, logging, subprocess
import xml.etree.ElementTree as ET
from src.config import Config
from src.app.utils import parse_xml_tree, update_progress, convert_to_xml, prettify


logging.basicConfig(level=logging.INFO)

class Preprocessing:
    inputRoot = Config.RAW_FILE_PATH
    tempRoot = Config.TEMP_FILE_PATH
    outputRoot = Config.PREPROCESSED_FILE_PATH
    progressOutputRoot = Config.PROGRESS_PATH


    def preprocess(self):
        step_count = 0

        # ----- File format conversion -----
        convert_to_xml(self.inputRoot, self.tempRoot)
        total_steps = len([filename for r, d, f in os.walk(self.tempRoot) for filename in f if filename.endswith(".xml") and filename.startswith(".") is False]) + 2 # +2: count the step for converting file format and loading stanza
        step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "preprocessing.txt"))

        # -----Start processsing -----
        package_name = "de_core_news_sm"
        if not spacy.util.is_package(package_name):
            command = f"python -m spacy download {package_name}"
            subprocess.run(command, shell=True)

        nlp = spacy.load("de_core_news_sm")
        step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "preprocessing.txt"))

        logging.info("Making XML structures...")
        for r, d, f in os.walk(self.tempRoot):
            for filename in f:
                if filename.endswith(".xml") and filename.startswith(".") is False:
                    tree, root = parse_xml_tree(os.path.join(r, filename))

                    for document in root.iter('document'):
                        currentDoc = nlp(document.text)

                        for s in currentDoc.sents:
                            sentenceLabel = ET.SubElement(document, "sentence")
                            for w in s:
                                lexemeLabel = ET.SubElement(sentenceLabel, "lexeme")
                                lexemeLabel.text = w.text
                                lexemeLabel.set("index", str(w.i))
                                lexemeLabel.set("lemma", w.lemma_)
                                lexemeLabel.set("pos", w.tag_)
                                lexemeLabel.set("feats", w.morph)
                                lexemeLabel.set("governor", str(w.head.i))
                                lexemeLabel.set("dependency_relation", w.dep_)

                                if w.ent_type_ != "":
                                    lexemeLabel.set("ner", w.ent_type_)

                        document.text = None

                    output = prettify(root)
                    with open(os.path.join(self.outputRoot, filename), mode="w", encoding="utf-8") as outputfile:
                        outputfile.write(output)

                    step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "preprocessing.txt"))

        logging.info("Done with preprocessing.")