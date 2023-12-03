import os, re, logging
from src.annotation.config import Config
from utils import parse_xml_tree, get_input_root, get_sentence_as_lexeme_list, get_sentence_as_text, get_wordlist_from_txt

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

hedges_list = get_wordlist_from_txt("./src/annotation/wordlists/hedges.txt")

print("Annotating hedges...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)

                # ----- Variables used for particle verbs with stems and particles separated -----
                stemIndex = None
                stemListIndex = None
                particleGov = None
                particleListIndex = None

                for idx, lexeme in enumerate(lexemeList):
                    currentLemma = lexeme.get("lemma")
                    currentPos = lexeme.get("pos")

                    # ----- 1. Monograms that do not need disambiguation -----
                    if currentLemma in hedges_list:
                        lexeme.set("hedge", currentLemma)

                    # ----- 2. N-grams: -----
                    ## 2.1 im Prinzip, im Wesentlichen, in der Regel:
                    if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "in" \
                            and lexemeList[idx + 1].get("lemma") == "der" \
                            and lexemeList[idx + 2].text in ["Prinzip", "Wesentlichen", "Regel"]:
                        lexeme.set("hedge", "in_der_" + lexemeList[idx + 2].text)
                        lexemeList[idx+1].set("hedge_2", "der")
                        lexemeList[idx+2].set("hedge_3", lexemeList[idx + 2].get("lemma"))

                    ## 2.2 in gewissem Maße:
                    if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "in" \
                            and lexemeList[idx + 1].text == "gewissem" \
                            and lexemeList[idx + 2].text == "Maße":
                        lexeme.set("hedge", "in_gewissem_Maße" + lexemeList[idx + 2].text)
                        lexemeList[idx + 1].set("hedge_2", "gewissem")
                        lexemeList[idx + 2].set("hedge_3", "Maße")

                    ## 2.3 im Grunde genommen:
                    if idx < len(lexemeList) - 3 and lexeme.get("lemma") == "in" \
                            and lexemeList[idx + 1].get("lemma") == "der" \
                            and lexemeList[idx + 2].text == "Grunde" \
                            and lexemeList[idx + 3].text == "genommen":
                        lexeme.set("hedge", "im_Grunde_genommen" + lexemeList[idx + 2].text)
                        lexemeList[idx + 1].set("hedge_2", "der")
                        lexemeList[idx + 2].set("hedge_3", "Grunde")
                        lexemeList[idx + 3].set("hedge_4", "genommen")

                    # ## 2.4 in den meisten Fällen
                    # if idx <= len(lexemeList)-4 and lexeme.text == "in" \
                    #         and lexemeList[idx+1].text == "den" and lexemeList[idx+2].text == "meisten" and lexemeList[idx+3].text == "Fällen":
                    #     lexeme.set("hedge", "in_den_meisten_Faellen")
                    #     lexemeList[idx+1].set("hedge_2", "den")
                    #     lexemeList[idx+2].set("hedge_3", "meisten")
                    #     lexemeList[idx+3].set("hedge_4", "Faellen")

                    ## 2.5 zu großen Teilen
                    # if idx <= len(lexemeList)-3 and lexeme.text == "zu" and lexemeList[idx+1].text == "großen" and lexemeList[idx+2].text == "Teilen":
                    #     lexeme.set("hedge", "zu_grossen_Teilen")
                    #     lexemeList[idx + 1].set("hedge_2", "grossen")
                    #     lexemeList[idx + 2].set("hedge_3", "Teilen")

                    # 2.6 Pi mal Daumen
                    if idx <= len(lexemeList)-3 and lexeme.text == "Pi" and lexemeList[idx+1].text == "mal" and lexemeList[idx+2].text == "Daumen":
                        lexeme.set("hedge", "Pi_mal_Daumen")
                        lexemeList[idx + 1].set("hedge_2", "mal")
                        lexemeList[idx + 2].set("hedge_3", "Daumen")

                    ## 2.7 im Großen und Ganzen
                    if idx < len(lexemeList) - 4 and lexeme.get("lemma") == "in" \
                            and lexemeList[idx + 1].get("lemma") == "der" \
                            and lexemeList[idx + 2].text == "Großen" \
                            and lexemeList[idx + 3].text == "und" \
                            and lexemeList[idx + 4].text == "Ganzen":
                        lexeme.set("hedge", "im_Großen_und_Ganzen")
                        lexemeList[idx + 1].set("hedge_2", "der")
                        lexemeList[idx + 2].set("hedge_3", "Großen")
                        lexemeList[idx + 3].set("hedge_4", "und")
                        lexemeList[idx + 4].set("hedge_4", "Ganzen")

                    ## 2.8 streng genommen
                    if idx < len(lexemeList) - 1 and lexeme.get("lemma") == "streng" and lexemeList[idx + 1].text == "genommen":
                        lexeme.set("hedge", "streng_genommen")
                        lexemeList[idx+1].set("hedge_2", "genommen")

                    ## 2.9 unter bestimmten Umständen
                    # if idx <= len(lexemeList)-3 and lexeme.get("lemma") == "unter" \
                    #         and lexemeList[idx+1].text == "bestimmten" \
                    #         and lexemeList[idx+2].text == "Umständen":
                    #     lexeme.set("hedge", "unter_bestimmten_Umstaenden")
                    #     lexemeList[idx + 1].set("hedge_2", "bestimmten")
                    #     lexemeList[idx + 2].set("hedge_3", "Umstaenden")

                    # ----- 3. Items that need disambiguation: -----
                    ## 3.1 Verbs:
                    if currentLemma in  ["scheinen", "vermuten", "spekulieren"] and re.fullmatch("(VVFIN|VVPP)", currentPos):
                        lexeme.set("hedge", currentLemma)

                    ## 3.2 Modal verbs:
                    # TODO: CHECK IF THE RULES ARE CORRECT!
                    if currentLemma in ["können", "müssen", "sollen", "werden"] and re.match("(könnt|müsst|sollt|würd)", lexeme.text):
                        lexeme.set("hedge", currentLemma)

                    ## 3.3 Items that should only be annotated as hedge when bearing the POS "ADV":
                    if currentLemma in ["etwas", "grob"] and currentPos == "ADV":
                        lexeme.set("hedge", currentLemma)

                    ## 3.4 annähernd:
                    if lexeme.get("lemma") == "annähernd":
                        lexeme.set("hedge", currentLemma)

                    ## 3.5 wohl: annotated by the script "modal_particles.py"

            tree.write(os.path.join(r, filename), encoding="utf-8")

print("Done with annotating hedges.")