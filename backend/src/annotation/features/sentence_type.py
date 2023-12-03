import os, logging
from utils import parse_xml_tree, get_input_root, get_sentence_as_lexeme_list, get_sentence_as_text

logging.basicConfig(level=logging.INFO)

inputRoot = "./output"

logging.info("Annotating sentence type...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)

                for lexeme in lexemeList:
                    if lexeme.text == "?":
                        lexeme.set("question", "y")

                    if lexeme.text == "!":
                        lexeme.set("exclamation", "y")

            tree.write(os.path.join(r, filename), encoding="utf-8")

logging.info("Done with annotating sentence type.")