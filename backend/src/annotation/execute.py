import sys, logging, os
from src.config import Config
from src.annotation.annotation import Annotation
from src.annotation.utils import parse_xml_tree, get_sentence_as_lexeme_list, get_sentence_as_text, update_progress


logging.basicConfig(level=logging.INFO)
inputRoot = Config.PREPROCESSED_FILE_PATH

method_name = sys.argv[1].split(".")[0]
anotation = Annotation()

logging.info("Annotating " + method_name + "...")
for r, d, f in os.walk(inputRoot):
    total_steps = len([filename for filename in f if filename.endswith(".xml")])
    step_count = 0

    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexeme_list = get_sentence_as_lexeme_list(s)

                if hasattr(Annotation, method_name) and callable(getattr(anotation, method_name)):
                    method_to_call = getattr(anotation, method_name)
                    method_to_call(lexeme_list)  
                else:
                    logging.info(f"Method '{method_name}' does not exist or is not callable.")

            tree.write(os.path.join(r, filename), encoding="utf-8")
            step_count = update_progress(step_count, total_steps)

logging.info("Done with annotating " + method_name + ".")