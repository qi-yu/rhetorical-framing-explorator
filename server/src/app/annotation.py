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
                    all_lexemes = []                

                    for s in root.iter("sentence"):
                        lexeme_list = get_sentence_as_lexeme_list(s)
                        all_lexemes += lexeme_list

                        if feature != "direct_speech":
                            try:
                                if hasattr(Disambiguation, feature) and callable(getattr(self.disambiguation, feature)):
                                    method_to_call = getattr(self.disambiguation, feature)
                                    method_to_call(lexeme_list)  

                            except Exception as e:
                                logging.info(e)

                    try:
                        self.disambiguation.direct_speech(all_lexemes)
                    except Exception as e:
                        logging.info(e)


                    tree.write(os.path.join(r, filename), encoding="utf-8")
                    step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, feature + ".txt"))


        logging.info("Done with annotating " + feature + ".")

    
    def generate_statistics(self):
        all_ids = []
        all_labels = []
        all_texts = []
        all_preprocessed_texts = []
        all_total_token_counts = []
        feature_stats = {feature['annotation_method']: [] for feature in self.selected_features if feature["is_auxiliary"] == False}
        selected_auxiliary_features = [feature['annotation_method'] for feature in self.selected_features if feature["is_auxiliary"] == True]

        for r, d, f in os.walk(self.inputRoot):
            for filename in f:
                if filename.endswith(".xml"):
                    tree, root = parse_xml_tree(os.path.join(r, filename))
                    all_ids.append(root.get("id"))
                    all_labels.append(root.get("label"))
                    current_total_token_count = 0

                    tree_raw, root_raw = parse_xml_tree(os.path.join(Config.TEMP_FILE_PATH, filename))
                    current_text = root_raw.text
                    all_texts.append(current_text)

                    current_preprocessed_text = ""
                    for lexeme in root.iter("lexeme"):
                        current_total_token_count += 1
                        if lexeme.get("pos").startswith("$"):
                            current_preprocessed_text += lexeme.text + " "
                        else:
                            current_preprocessed_text += lexeme.get("lemma") + " "
                    
                    all_total_token_counts.append(current_total_token_count)
                    all_preprocessed_texts.append(current_preprocessed_text)

                    for feature in feature_stats.keys():
                        current_feature_count = 0

                        for s in root.iter("sentence"):
                            lexeme_list = get_sentence_as_lexeme_list(s)
                        
                            if selected_auxiliary_features:
                                for lexeme in lexeme_list:
                                    found_auxiliary_feature = False
                        
                                    for aux_feature in selected_auxiliary_features:
                                        if lexeme.get(aux_feature):
                                            found_auxiliary_feature = True
                                            break
                                             
                                    if not found_auxiliary_feature and lexeme.get(feature):
                                        logging.info(filename + " " + lexeme.get("lemma"))
                                        current_feature_count += 1
                                        
                            else:
                                for lexeme in lexeme_list:
                                    if lexeme.get(feature):
                                        current_feature_count += 1
                                    
                        feature_stats[feature].append(current_feature_count)


        df = pd.DataFrame(feature_stats)
        df.insert(0, "id", all_ids)
        df.insert(1, "label", all_labels)
        df.insert(2, "text", all_texts)
        df.insert(3, "text_preprocessed", all_preprocessed_texts)
        df.insert(4, "total_token_count", all_total_token_counts)
        count = df.to_csv(sep="\t", encoding="utf-8", index=False)

        return df, count


    def generate_by_label_statistics(self):
        df_count, csv_count = self.generate_statistics()
        df_sums_by_label = df_count.drop("id", axis=1).groupby("label").sum()
        
        for col in df_sums_by_label.columns:
            if col not in ["label", "text",  "text_preprocessed", "total_token_count"]: 
                df_sums_by_label[col] = df_sums_by_label[col] / df_sums_by_label["total_token_count"]

        by_label_freq = df_sums_by_label.to_csv(sep="\t", encoding="utf-8")   

        return by_label_freq            

                        