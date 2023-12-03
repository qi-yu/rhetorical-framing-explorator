
import os, re, logging
from src.annotation.config import Config
from utils import parse_xml_tree, get_input_root, get_sentence_as_lexeme_list, get_sentence_as_text, get_wordlist_from_txt

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

booster_list = get_wordlist_from_txt("./src/annotation/wordlists/boosters.txt")


logging.info("Annotating boosters...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)

                rechtGovernor = None
                verbIndex = None
                verbLemma = None

                for idx, lexeme in enumerate(lexemeList):
                    currentLemma = lexeme.get("lemma")
                    currentPos = lexeme.get("pos")
                    currentGovenor = lexeme.get("governor")

                    # ----- 1. Monograms that do not need disambiguation: -----
                    if currentLemma in booster_list:
                        lexeme.set("booster", currentLemma)

                    # ----- 2. N-grams -----
                    ## 2.1 erst recht:
                    if idx < len(lexemeList) - 1 and lexeme.get("lemma") == "erst" and lexemeList[idx + 1].get("lemma") == "recht":
                        lexeme.set("booster", "erst_recht")
                        lexemeList[idx+1].set("booster_2", "recht")

                    ## 2.2 bei weitem:
                    if idx < len(lexemeList) - 1 and lexeme.get("lemma") == "bei" and lexemeList[idx + 1].text == "weitem":
                        lexeme.set("booster", "bei_weitem")
                        lexemeList[idx+1].set("booster_2", "weitem")

                    ## 2.3 ganz und gar:
                    if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "ganz" and lexemeList[idx + 1].text == "und" and lexemeList[idx + 2].text == "gar":
                        lexeme.set("booster", "ganz_und_gar")
                        lexemeList[idx + 1].set("booster_2", "und")
                        lexemeList[idx + 1].set("booster_3", "gar")

                    # ----- 3. Items that need disambiguation:
                    # 3.1 Items that should only be annotated as booster when bearing the POS "ADJD":
                    if currentLemma in ["ausgesprochen", "entschieden", "komplett", "wesentlich"] and currentPos == "ADJD":
                        lexeme.set("booster", currentLemma)

                    ## 3.2 Items that should only be annotated as booster when bearing the POS "ADV":
                    if currentLemma in ["tatsächlich", "viel", "weit"] and currentPos == "ADV":
                        lexeme.set("booster", currentLemma)

                    ## 3.3 Items that should only be annotated as booster only when modifying adjectives/adverbs:
                    if currentLemma in ["denkbar", "echt", "richtig", "wirklich"]:
                        for l in lexemeList:
                            if l.get("index") == currentGovenor and l.get("pos").startswith("AD"):
                                lexeme.set("booster", currentLemma)

                    ## 3.4 absolut: exclude usages in "absolute [Zz]ahl$"
                    if currentLemma == "absolut" and re.search("[Zz]ahl$", lexemeList[idx+1].get("lemma")) is None:
                        lexeme.set("booster", currentLemma)

                    ## 3.5. total:
                    if currentLemma == "total" and currentPos in ["ADJD", "ADJA"]:
                        lexeme.set("booster", currentLemma)

                    ## 3.6. ganz:
                    if currentLemma == "ganz" and currentPos in ["ADJD", "ADV"] and lexeme.get("booster") != "ganz_und_gar": # not already annotated as "ganz und gar"
                        lexeme.set("booster", currentLemma)

                    ## 3.7 höchst:
                    if lexeme.text == "höchst":
                        lexeme.set("booster", currentLemma)

                    ## 3.8 recht:
                    if currentLemma == "recht" and currentPos == "ADV" and lexeme.get("booster") != "erst_recht": # not already annotated as "erst_recht"
                        for l in lexemeList:
                            if  l.get("index") == currentGovenor and l.get("lemma") not in ["haben", "behalten", "geben", "kommen", "bekommen"]:
                                lexeme.set("booster", currentLemma)

            tree.write(os.path.join(r, filename), encoding="utf-8")

logging.info("Done with annotating boosters.")