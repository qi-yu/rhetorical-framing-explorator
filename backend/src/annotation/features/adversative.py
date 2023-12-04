import os, re, logging
from src.annotation.config import Config
from src.annotation.utils import parse_xml_tree, get_sentence_as_lexeme_list, get_sentence_as_text

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

logging.info("Annotating adversative connectors...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)
                lexemeList_toString = get_sentence_as_text(s)

                # ----- variables used for disambiguing "sondern" -----
                findNichtNur = False

                index = 0
                for lexeme in lexemeList:
                    currentLemma = lexeme.get("lemma")
                    currentPos = lexeme.get("pos")

                    # # ----- 1. wiederum -----
                    # ### TODO: How to disambiguate "wiederum" as adversative connector for opposition and "wiederum" with the meaning "again"?
                    # if currentLemma == "wiederum":
                    #     lexeme.set("adversative", "wiederum")


                    # ----- 2. allerdings -----
                    ### TODO: How to disambiguate "allerdings" as adversative connector for opposition and "allerdings" as adverb for affirmation?
                    if currentLemma == "allerdings":
                        lexeme.set("adversative", "allerdings")


                    # ----- 3. sondern -----
                    # Exclude "sondern" in "nicht nur..., sondern (auch)...":
                    if currentLemma == "nicht" and index < len(lexemeList)-1 and lexemeList[index+1].get("lemma") == "nur":
                        findNichtNur = True

                    if currentLemma == "sondern":
                        if findNichtNur != True:
                            lexeme.set("adversative", "sondern")

                        if index < len(lexemeList)-1 and lexemeList[index+1].get("lemma") == "auch":
                            lexeme.attrib.pop("adversative", None)


                    # ----- 4. jedoch -----
                    if currentLemma == "jedoch":
                        lexeme.set("adversative", "jedoch")


                    # ----- 5. einerseits -----
                    if currentLemma == "einerseits":
                       lexeme.set("adversative", "einerseits")


                    # ----- 6. andererseits -----
                    if currentLemma == "andererseits":
                        lexeme.set("adversative_2", "andererseits")


                    # ----- 7. zum einen -----
                    if re.fullmatch("[Zz]u", lexeme.text) and index < len(lexemeList)-2 and re.fullmatch("dem", lexemeList[index+1].text) and re.fullmatch("einen", lexemeList[index+2].text):
                       lexeme.set("adversative", "zum_einen")
                       lexemeList[index+1].set("adversative_2", "dem")
                       lexemeList[index+2].set("adversative_3", "einen")


                    # ----- 8. zum anderen -----
                    if re.fullmatch("[Zz]u", lexeme.text) and index < len(lexemeList)-2 and re.fullmatch("dem", lexemeList[index+1].text) and re.fullmatch("anderen", lexemeList[index+2].text):
                        lexeme.set("adversative_4", "zu")
                        lexemeList[index + 1].set("adversative_5", "dem")
                        lexemeList[index + 2].set("adversative_6", "anderen")


                    # ----- 9. statt -----
                    if currentLemma == "statt" and currentPos != "PTKVZ":
                        lexeme.set("adversative", "statt")

                        # # Exclude cases like "Einen Tag zuvor gab es einen Kompromiss statt Krawall", because they don't express opposition relation on discourse level:
                        # if index == 0:
                        #     lexeme.set("adversative", "statt")
                        #
                        # if index > 0 and re.fullmatch("(\$,|KON)", lexemeList[index-1].get("pos")):
                        #     lexeme.set("adversative", "statt")


                    # ----- 10. anstatt -----
                    if currentLemma == "anstatt":
                        lexeme.set("adversative", "anstatt")

                        # # Exclude cases like "Zudem beginnen immer mehr junge Menschen ein Studium anstatt einer Ausbildung", because they don't express opposition relation on discourse level:
                        # if index == 0:
                        #     lexeme.set("adversative", "anstatt")
                        #
                        # if index > 0 and re.fullmatch("(\$,|KON)", lexemeList[index-1].get("pos")):
                        #     lexeme.set("adversative", "anstatt")


                    # ----- 11. vielmehr -----
                    if currentLemma == "vielmehr":
                        lexeme.set("adversative", "vielmehr")


                    # ----- 12. andernfalls / anderenfalls -----
                    if currentLemma == "andernfalls" or currentLemma == "anderenfalls":
                        lexeme.set("adversative", "andernfalls")

                    index += 1

            tree.write(os.path.join(r, filename), encoding="utf-8")

logging.info("Done with annotating adversative connectors.")
