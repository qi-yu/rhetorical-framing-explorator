# Author of the script: Marina Janka-Ramm
# The implementation by Janka-Ramm is based on the architecture designed by Qi Yu
# Adapted by: Qi Yu, Date of adaption: 12.12.2022

import os, logging
from src.annotation.config import Config
from backend.src.annotation.utils import parse_xml_tree, get_sentence_as_lexeme_list, get_sentence_as_text

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

# ---List of conditional connectors that don't need disambiguation ---- #
conditionalConnectorsList = ["wenn", "falls", "sofern", ] # Qi: "ob" is excluded from this list. It is not always a conditional connector.

logging.info("Annotating conditional connectors...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)
                lexemeList_toString = get_sentence_as_text(s)

                # ----- Start annotation -----
                index = 0
                for lexeme in lexemeList:
                    currentLemma = lexeme.get("lemma")
                    currentPos = lexeme.get("pos")
                    currentWord = lexeme.text
                    depRelation = lexeme.get("dependency_relation")

                    ### ----- Conditional connectors ----- ###
                    # ----- 1. condConnectors without disambiguation rules -----
                    if currentLemma in conditionalConnectorsList:
                        lexeme.set("conditional", currentLemma)


                # ---- Start annotation where disambiguation is needed ----#
                    # --- 2. "gesetzt" ---#
                    if currentWord == "Gesetzt" or currentWord == "gesetzt" and index == 0:
                        # --- "gesetzt den Fall"
                        if len(lexemeList) > 2 and lexemeList[index+1].get("lemma") == "der" and lexemeList[index+2].get("lemma") == "Fall":
                            lexemeList[index].set("conditional", "gesetzt_den_Fall")
                            lexemeList[index+1].set("conditional_2", "den")
                            lexemeList[index+2].set("conditional_3", "Fall")
                        # ---- "gesetzt" ---'
                        if depRelation == "conj":
                            lexeme.set("conditional", "gesetzt")

                    index += 1

            tree.write(os.path.join(r, filename), encoding="utf-8")

logging.info("Done with annotating conditional connectors.")