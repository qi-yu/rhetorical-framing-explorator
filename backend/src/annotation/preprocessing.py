import os, stanza, logging
import xml.etree.ElementTree as ET
from xml.dom import minidom
from src.config import Config
from src.annotation.utils import parse_xml_tree, update_progress, df_to_xml, prettify


logging.basicConfig(level=logging.INFO)

inputRoot = Config.RAW_FILE_PATH
outputRoot = Config.PREPROCESSED_FILE_PATH
progressOutputRoot = Config.PROGRESS_PATH

step_count = 0

# ----- File format conversion -----
df_to_xml(inputRoot, inputRoot)
total_steps = len([filename for r, d, f in os.walk(inputRoot) for filename in f if filename.endswith(".xml")]) + 2 # +2: count the step for converting file format and loading stanza
step_count = update_progress(step_count, total_steps, progressOutputRoot)

# -----Start processsing -----
# Please uncomment this line to install the German model when running this programm for the first time.
# stanza.download("de")

nlp = stanza.Pipeline(lang="de")
step_count = update_progress(step_count, total_steps, progressOutputRoot)

logging.info("Making XML structures...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith('.xml'):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for utr in root.iter('utterance'):
                currentUtr = nlp(utr.text)

                for s in currentUtr.sentences:
                    sentenceLabel = ET.SubElement(utr, "sentence")
                    for w in s.words:
                        lexemeLabel = ET.SubElement(sentenceLabel, "lexeme")
                        lexemeLabel.text = w.text
                        lexemeLabel.set("index", str(w.id))
                        lexemeLabel.set("lemma", str(w.lemma))
                        lexemeLabel.set("pos", str(w.xpos))
                        lexemeLabel.set("feats", str(w.feats))
                        lexemeLabel.set("governor", str(w.head))
                        lexemeLabel.set("dependency_relation", str(w.deprel))

                        if w.parent.ner != "O":
                            lexemeLabel.set("ner", w.parent.ner)

                utr.text = None

            output = prettify(root)
            with open(os.path.join(outputRoot, filename.split('.')[0] + "_DUS.xml"), mode="w", encoding="utf-8") as outputfile:
                outputfile.write(output)

            step_count = update_progress(step_count, total_steps, progressOutputRoot)

logging.info("Done with preprocessing.")