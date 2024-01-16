import logging, os
import pandas as pd
from src.config import Config
from src.app.disambiguation import Disambiguation
from src.app.utils import parse_xml_tree, get_sentence_as_lexeme_list, update_progress

logging.basicConfig(level=logging.INFO)

class Annotation:
    inputRoot = Config.PREPROCESSED_FILE_PATH
    progressOutputRoot = Config.PROGRESS_PATH
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
        all_ids = []
        all_labels = []
        all_total_token_counts = []
        feature_stats = {feature: [] for feature in self.selected_features}

        for r, d, f in os.walk(self.inputRoot):
            for filename in f:
                if filename.endswith(".xml"):
                    tree, root = parse_xml_tree(os.path.join(r, filename))
                    all_ids.append(root.get("id"))
                    all_labels.append(root.get("label"))
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


        df = pd.DataFrame(feature_stats)
        df.insert(0, "id", all_ids)
        df.insert(1, "label", all_labels)
        df.insert(2, "total_token_count", all_total_token_counts)
        count = df.to_csv(sep="\t", encoding="utf-8", index=False)

        return df, count


    def generate_by_label_statistics(self):
        df_count, csv_count = self.generate_statistics()
        df_sums_by_label = df_count.drop("id", axis=1).groupby("label").sum()
        
        for col in df_sums_by_label.columns:
            if col != "label" and col != "total_token_count": 
                df_sums_by_label[col] = df_sums_by_label[col] / df_sums_by_label["total_token_count"]

        df_sums_by_label = df_sums_by_label.drop(["total_token_count"], axis=1) 
        by_label_freq = df_sums_by_label.to_csv(sep="\t", encoding="utf-8")   

        return by_label_freq            

                        