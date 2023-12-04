import os, logging
from src.config import Config
from src.annotation.utils import parse_xml_tree, get_sentence_as_lexeme_list, update_progress

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH


logging.info("Annotating sentence type...")
for r, d, f in os.walk(inputRoot):
    total_steps = len([filename for filename in f if filename.endswith(".xml")])
    step_count = 0

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
            step_count = update_progress(step_count, total_steps)

logging.info("Done with annotating sentence type.")