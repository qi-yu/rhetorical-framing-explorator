import os, re, logging
from src.annotation.config import Config
from src.annotation.utils import parse_xml_tree, get_sentence_as_lexeme_list, get_sentence_as_text

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

logging.info("Annotating concessive connectors...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)
                lexemeList_toString = get_sentence_as_text(s)

                index = 0
                for lexeme in lexemeList:
                    currentLemma = lexeme.get("lemma")
                    currentPos = lexeme.get("pos")

                    # ----- 1. dennoch -----
                    if currentLemma == "dennoch":
                        lexeme.set("concessive", "dennoch")

                    # ----- 2. obwohl -----
                    if currentLemma == "obwohl":
                        lexeme.set("concessive", "obwohl")

                        # Exclude "obwohl" used for correcting the preceding proposition (i.e. followed by ,/./- + V2 sentences):
                        # if index < len(lexemeList) - 1 and re.fullmatch("[,.-]", lexemeList[index+1].text):
                        #     lexeme.attrib.pop("concessive", None)

                    # ----- 3. wobei -----
                    if currentLemma == "wobei" and index < len(lexemeList)-1 and re.fullmatch("[,.-]", lexemeList[index+1].text):
                        lexeme.set("concessive", "wobei")

                    # ----- 4. trotzdem -----
                    if currentLemma == "trotzdem":
                        lexeme.set("concessive", "trotzdem")

                    # ----- 5. trotz -----
                    if currentLemma == "trotz":
                        lexeme.set("concessive", "trotz")

                    # ----- 6. ungeachtet / ungeachtet dessen / dessen ungeachtet -----
                    if currentLemma == "ungeachtet":
                        lexeme.set("concessive", "ungeachtet")

                        # if index < len(lexemeList)-1 and lexemeList[index+1].text == "dessen":
                        #     lexemeList[index+1].set("concessive", "ungeachtet")
                        #
                        # if index > 0 and re.fullmatch("[Dd]essen", lexemeList[index-1].text):
                        #     lexemeList[index-1].set("concessive", "ungeachtet")


                    # ----- 7. zwar -----
                    # Exclude "zwar" in "und zwar":
                    if currentLemma == "zwar" and index > 0 and lexemeList[index-1].get("lemma") != "und":
                        lexeme.set("concessive", "zwar")

                    # ----- 8. gleichwohl -----
                    if currentLemma == "gleichwohl":
                        lexeme.set("concessive", "gleichwohl")

                    # ----- 9. wenngleich -----
                    if currentLemma == "wenngleich":
                        lexeme.set("concessive", "wenngleich")

                    # ----- 10. obschon -----
                    if currentLemma == "obschon":
                        lexeme.set("concessive", "obschon")

                    # ----- 11. nichtsdestotrotz -----
                    if currentLemma == "nichtsdestotrotz":
                        lexeme.set("concessive", "nichtsdestotrotz")

                    # ----- 12. nichtsdestoweniger -----
                    if currentLemma == "nichtsdestoweniger":
                        lexeme.set("concessive", "nichtsdestoweniger")

                    # ----- 13. unbeschadet dessen -----
                    if currentLemma == "unbeschadet" and index < len(lexemeList)-1 and lexemeList[index+1].text == "dessen":
                        lexeme.set("concessive", "unbeschadet_dessen")
                        lexemeList[index+1].set("concessive_2", "dessen")

                    index += 1

            tree.write(os.path.join(r, filename), encoding="utf-8")

logging.info("Done with annotating concessive connectors.")