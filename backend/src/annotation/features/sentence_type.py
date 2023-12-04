import os, logging
from src.annotation.config import Config
from utils import parse_xml_tree, get_sentence_as_lexeme_list, update_progress

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

total_files = len([filename for r, d, f in os.walk(inputRoot) for filename in f if filename.endswith(".xml")])
processed_files = 0

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

            processed_files += 1
            progress = processed_files / total_files * 100
            update_progress(progress)

logging.info("Done with annotating sentence type.")