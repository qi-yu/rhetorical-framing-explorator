import os, stanza, logging, shutil
import xml.etree.ElementTree as ET
from xml.dom import minidom
# from src.annotation.utils.annotation_utils import parse_xml_tree


def prettify(elem):
    """Return a pretty-printed XML string for the Element.

    Args:
        elem: The XML element to be prettified.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

logging.basicConfig(level=logging.INFO)

# Please uncomment this line to install the German model when running this programm for the first time.
# stanza.download("de")

nlp = stanza.Pipeline(lang="de")

# ----- Define the paths of input and output files -----
inputRoot = "./upload"
outputRoot = "./output"


# -----Start processsing -----
logging.info("Making XML structures...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith('.xml'):
            tree = ET.parse(os.path.join(r, filename))
            root = tree.getroot()

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

logging.info("Done with preprocessing.")