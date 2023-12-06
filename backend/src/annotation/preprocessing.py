import os, spacy, logging, subprocess
import xml.etree.ElementTree as ET
from src.config import Config
from src.annotation.utils import parse_xml_tree, update_progress, convert_to_xml, prettify


logging.basicConfig(level=logging.INFO)

inputRoot = Config.RAW_FILE_PATH
outputRoot = Config.PREPROCESSED_FILE_PATH
progressOutputRoot = Config.PROGRESS_PATH

step_count = 0

# ----- File format conversion -----
convert_to_xml(inputRoot, inputRoot)
total_steps = len([filename for r, d, f in os.walk(inputRoot) for filename in f if filename.endswith(".xml") and filename.startswith(".") is False]) + 2 # +2: count the step for converting file format and loading stanza
step_count = update_progress(step_count, total_steps, progressOutputRoot)

# -----Start processsing -----
package_name = "de_core_news_sm"
if not spacy.util.is_package(package_name):
    command = f"python -m spacy download {package_name}"
    subprocess.run(command, shell=True)

nlp = spacy.load("de_core_news_sm")
step_count = update_progress(step_count, total_steps, progressOutputRoot)

logging.info("Making XML structures...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml") and filename.startswith(".") is False:
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for utr in root.iter('utterance'):
                currentUtr = nlp(utr.text)

                for s in currentUtr.sents:
                    sentenceLabel = ET.SubElement(utr, "sentence")
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

                utr.text = None

            output = prettify(root)
            with open(os.path.join(outputRoot, filename.split('.')[0] + "_DUS.xml"), mode="w", encoding="utf-8") as outputfile:
                outputfile.write(output)

            step_count = update_progress(step_count, total_steps, progressOutputRoot)

logging.info("Done with preprocessing.")