import logging, os, datetime
import pandas as pd
from src.config import Config
from src.app.disambiguation import Disambiguation
from src.app.utils import parse_xml_tree, get_sentence_as_lexeme_list, update_progress

logging.basicConfig(level=logging.INFO)

class Annotation:
    inputRoot = Config.PREPROCESSED_FILE_PATH
    progressOutputRoot = Config.PROGRESS_PATH
    statisticsOutputRoot = Config.PREPROCESSED_FILE_PATH
    disambiguation = Disambiguation()
    selected_features = []


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

    
    def generate_statistics(self):
        all_filenames = []
        all_total_token_counts = []
        feature_stats = {feature: [] for feature in self.selected_features}

        for r, d, f in os.walk(self.inputRoot):
            total_steps = len([filename for filename in f if filename.endswith(".xml")])
            step_count = 0

            for filename in f:
                if filename.endswith(".xml"):
                    tree, root = parse_xml_tree(os.path.join(r, filename))
                    all_filenames.append(filename)
                    current_total_token_count = 0

                    for lexeme in root.iter("lexeme"):
                        current_total_token_count += 1
                    
                    all_total_token_counts.append(current_total_token_count)

                    for feature in feature_stats.keys():
                        current_feature_count = 0

                        for s in root.iter("sentence"):
                            lexeme_list = get_sentence_as_lexeme_list(s)
                        
                            for lexeme in lexeme_list:
                                if lexeme.get(feature):
                                    current_feature_count += 1
                                    
                        feature_stats[feature].append(current_feature_count)

                    step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "statistics.txt"))

        df = pd.DataFrame(feature_stats)
        df.insert(0, "id", all_filenames)
        df.insert(1, "total_token_count", all_total_token_counts)
        csv_data = df.to_csv(sep="\t", encoding="utf-8", index=False)
        
        return csv_data

                            

                        