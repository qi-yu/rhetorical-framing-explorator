import sys, logging, os
from src.config import Config
from src.annotation.features import Disambiguation
from src.annotation.utils import parse_xml_tree, get_sentence_as_lexeme_list, update_progress

logging.basicConfig(level=logging.INFO)

class Annotation:
    inputRoot = Config.PREPROCESSED_FILE_PATH
    progressOutputRoot = Config.PROGRESS_PATH
    disambiguation = Disambiguation()


    def annotate_feature(self, feature):
        logging.info("Annotating " + feature + "...")

        for r, d, f in os.walk(self.inputRoot):
            total_steps = len([filename for filename in f if filename.endswith(".xml")])
            step_count = 0

            for filename in f:
                if filename.endswith(".xml"):
                    tree, root = parse_xml_tree(os.path.join(r, filename))

                    for s in root.iter("sentence"):
                        lexeme_list = get_sentence_as_lexeme_list(s)

                        if hasattr(Disambiguation, feature) and callable(getattr(self.disambiguation, feature)):
                            method_to_call = getattr(self.disambiguation, feature)
                            method_to_call(lexeme_list)  
                        else:
                            logging.info(f"Method '{feature}' does not exist or is not callable.")

                    tree.write(os.path.join(r, filename), encoding="utf-8")
                    step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, feature + ".txt"))


        logging.info("Done with annotating " + feature + ".")