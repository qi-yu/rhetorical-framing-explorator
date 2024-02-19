import logging, os
import pandas as pd
from src.config import Config
from src.app.disambiguation import Disambiguation
from src.app.utils import parse_xml_tree, get_document_as_text, get_document_as_lemmatized_text, \
    get_sentence_as_lexeme_list, get_sentence_as_text, get_sentence_as_lemmatized_text, update_progress

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

    
    def aggregate_statistics(self):
        selected_auxiliary_features = [feature['annotation_method'] for feature in self.selected_features if feature["is_auxiliary"] == True]

        for r, d, f in os.walk(self.inputRoot):
            for filename in f:
                if filename.endswith(".xml"):
                    tree, root = parse_xml_tree(os.path.join(r, filename))
                    doc_feature_stats = {**{"total_token_count": 0}, **{feature['annotation_method']: 0 for feature in self.selected_features if feature["is_auxiliary"] == False}}

                    
                    for s in root.iter("sentence"):
                        lexeme_list = get_sentence_as_lexeme_list(s)
                        sent_feature_stats = {**{"total_token_count": 0}, **{feature['annotation_method']: 0 for feature in self.selected_features if feature["is_auxiliary"] == False}}
                            
                        if selected_auxiliary_features:
                            for lexeme in lexeme_list:
                                sent_feature_stats["total_token_count"] += 1
                                found_auxiliary_feature = False

                                for aux_feature in selected_auxiliary_features:
                                    if lexeme.get(aux_feature):
                                        found_auxiliary_feature = True
                                        break

                                if not found_auxiliary_feature:
                                     for feature in sent_feature_stats.keys():
                                        if lexeme.get(feature):
                                            sent_feature_stats[feature] += 1
                        else:
                            for lexeme in lexeme_list:
                                sent_feature_stats["total_token_count"] += 1
                                for feature in sent_feature_stats.keys():
                                    if lexeme.get(feature):
                                        sent_feature_stats[feature] += 1

                        for k, v in sent_feature_stats.items():
                            s.set(k, str(v))
                            doc_feature_stats[k] += v

                    for k, v in doc_feature_stats.items():
                        root.set(k, str(v))

                    tree.write(os.path.join(r, filename), encoding="utf-8")
                    

    def generate_statistics_table(self, level):
        all_ids = []
        all_labels = []
        all_sentence_indices = []
        all_texts = []
        all_preprocessed_texts = []
        all_stats = {**{"total_token_count": []}, **{feature['annotation_method']: [] for feature in self.selected_features if feature["is_auxiliary"] == False}}

        for r, d, f in os.walk(self.inputRoot):
            for filename in f:
                if filename.endswith(".xml"):
                    tree, root = parse_xml_tree(os.path.join(r, filename))

                    if level == "document":
                        all_ids.append(root.get("id"))
                        all_labels.append(root.get("label"))
                        all_texts.append(get_document_as_text(root))
                        all_preprocessed_texts.append(get_document_as_lemmatized_text(root))
                        
                        for key in all_stats.keys():
                            all_stats[key].append(int(root.get(key)))

                    if level == "sentence":
                        for s in root.iter("sentence"):
                            all_ids.append(root.get("id"))
                            all_labels.append(root.get("label"))
                            all_sentence_indices.append(s.get("index"))
                            all_texts.append(get_sentence_as_text(s))
                            all_preprocessed_texts.append(get_sentence_as_lemmatized_text(s))

                            for key in all_stats.keys():
                                all_stats[key].append(int(s.get(key)))

        df = pd.DataFrame(all_stats)
        df.insert(0, "id", all_ids)
        df.insert(1, "label", all_labels)
        df.insert(2, "text", all_texts)
        df.insert(3, "text_preprocessed", all_preprocessed_texts)

        if level == "sentence":
            df.insert(1, "sentence_index", all_sentence_indices)

        return df
    

    def generate_by_label_statistics(self):
        df_count = self.generate_statistics_table("document")
        df_sums_by_label = df_count.drop(["id", "text", "text_preprocessed"], axis=1).groupby("label").sum()
        
        for col in df_sums_by_label.columns:
            if col not in ["label", "total_token_count"]: 
                df_sums_by_label[col] = df_sums_by_label[col] / df_sums_by_label["total_token_count"]

        by_label_freq = df_sums_by_label

        return by_label_freq            


    def get_statistics(self):
        step_count = 0
        total_steps = 4

        self.aggregate_statistics()
        step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "statistics.txt"))

        self.generate_statistics_table("document").to_csv(Config.STATISTICS_DOCUMENT_LEVEL_PATH, sep="\t", encoding="utf-8", index=False) 
        step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "statistics.txt"))

        self.generate_statistics_table("sentence").to_csv(Config.STATISTICS_SENTENCE_LEVEL_PATH, sep="\t", encoding="utf-8", index=False) 
        step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "statistics.txt"))

        self.generate_by_label_statistics().to_csv(Config.STATISTICS_BY_LABEL_PATH, sep="\t", encoding="utf-8")                      
        step_count = update_progress(step_count, total_steps, os.path.join(self.progressOutputRoot, "statistics.txt"))