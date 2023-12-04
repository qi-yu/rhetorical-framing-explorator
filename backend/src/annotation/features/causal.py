import os, re, logging
from src.annotation.config import Config
from utils import parse_xml_tree, get_sentence_as_lexeme_list, get_sentence_as_text, update_progress

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

total_files = len([filename for r, d, f in os.walk(inputRoot) for filename in f if filename.endswith(".xml")])
processed_files = 0

logging.info("Annotating causal connectors...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)
                lexemeList_toString = get_sentence_as_text(s)

                # ----- variables used for disambiguing "Grund" -----
                negGovList = []

                # ----- variables used for disambiguing "daher" -----
                finVerbStemIndex = None
                finVerbStemLemma = None
                finVerbStemListIndex = None
                koennenIndex = None
                koennenListIndex = None


                # ----- Start disambiguation -----
                index = 0
                for lexeme in lexemeList:
                    currentLemma = lexeme.get("lemma")
                    currentPos = lexeme.get("pos")

                    ### ----- Part 1: Causal connectors ----- ###
                    # ----- 1. weil -----
                    if currentLemma == "weil":
                        lexeme.set("causal", "weil")

                    # ----- 2. da -----
                    if currentLemma == "da" and currentPos == "KOUS" and lexeme.get("dependency_relation") == "mark":
                        lexeme.set("causal", "da")

                        # Exclude "da" that are not at the beginning of a sentence or a part-sentence:
                        if index > 0 and re.fullmatch("(KON|\$[,.(])", lexemeList[index-1].get("pos")) is None:
                            lexeme.attrib.pop("causal", None)

                        # Exclude "da" directly followed by comma, e.g. "Da , wo die Häuser stehen, ...":
                        if index < len(lexemeList)-1 and lexemeList[index+1].text == ",":
                            lexeme.attrib.pop("causal", None)

                        # Exclude "da" in cases like "Da wo wir große Gefährdungen haben":
                        if index < len(lexemeList)-1 and lexemeList[index+1].get("lemma") == "wo":
                            lexeme.attrib.pop("causal", None)

                        # Exclude "da" directly followed by a finite verb:
                        if index < len(lexemeList)-1 and re.fullmatch("V[AMV]FIN", lexemeList[index+1].get("pos")):
                            lexeme.attrib.pop("causal", None)

                        # Exclude "da" in "hier und da":
                        if index > 1 and lexemeList[index-2].get("lemma") == "hier" and lexemeList[index-1].get("lemma") == "und":
                            lexeme.attrib.pop("causal", None)


                    # ----- 3. denn -----
                    if currentLemma == "denn":

                        # Exclude cases like "mehr denn je"
                        if currentPos == "KON" and index+1 < len(lexemeList) and lexemeList[index+1].get("lemma") != "je":
                            lexeme.set("causal", "denn")

                        if index+1 < len(lexemeList) and lexemeList[index+1].get("lemma") == ":":
                            lexeme.set("causal", "denn")

                        # Exclude "denn" in "Es sei denn, ..."
                        if index-1 >= 0 and lexemeList[index-1].text == "sei":
                            lexeme.attrib.pop("causal", None)


                    # ----- 4. Grund -----
                    # if lexeme.get("negation") is not None:
                    #     negGovList.append(lexeme.get("governor"))
                    #
                    # if currentLemma == "Grund":
                    #     grundIndex = lexeme.get("index")
                    #     lexeme.set("causal", "Grund")
                    #
                    #     # Exclude "Grund" with negation, such as "Es gibt keinen Grund, ...": They are not reasoning.
                    #     if grundIndex in negGovList:
                    #         lexeme.attrib.pop("causal", None)



                    ### ----- Part 2: Consecutive connectors ----- ###
                    # ----- 5. also -----
                    ### TODO: Check if these rules are accurate enough!
                    if currentLemma == "also" and currentPos == "ADV" and lexemeList[-1].text != "?" and lexemeList[-2].text != "?":
                        lexeme.set("causal", "also")

                        # Exclude "also" at the beginning of a sentence or a part-sentence which is not followed by a finite verb:
                        if index == 0 and len(lexemeList) > 1 and re.fullmatch("V[AMV]FIN", lexemeList[1].get("pos")) is None:
                            lexeme.attrib.pop("causal", None)

                        if index > 0 and index < len(lexemeList)-1 and re.match("\$[,.(]", lexemeList[index-1].get("pos")) and re.fullmatch("V[AMV]FIN", lexemeList[index+1].get("pos")) is None:
                            lexeme.attrib.pop("causal", None)


                    # ----- 6. daher -----
                    if re.fullmatch("(kommen|rühren|rennen|laufen|fliegen|reiten|bringen|reden|stapfen)", currentLemma):
                        finVerbStemIndex = lexeme.get("index")
                        finVerbStemLemma = currentLemma
                        finVerbStemListIndex = index

                    if currentLemma == "können":
                        koennenIndex = lexeme.get("index")
                        koennenListIndex = index

                    if currentLemma == "daher":
                        if lexeme.get("governor") != finVerbStemIndex:
                            lexeme.set("causal", "daher")

                        if lexeme.get("governor") == finVerbStemIndex and finVerbStemLemma and re.fullmatch("(kommen|rühren)", finVerbStemLemma) :
                            # Annotate "daher" in cases like "Das kommt/rührt (aber auch) daher, ..." as "causal":
                            if finVerbStemListIndex < index:
                                lexeme.set("causal", "daher")
                                for w in lexemeList[finVerbStemListIndex+1:index]:
                                    if re.fullmatch("(ADV|APPR|PIS)", w.get("pos")) is None:
                                        lexeme.attrib.pop("causal", None)
                                        break

                            # Annotate "daher" in cases like "Das kann auch daher kommen, ..." as "causal":
                            if koennenIndex and koennenListIndex < index and finVerbStemListIndex == index+1:
                                lexeme.set("causal", "daher")
                                print(lexemeList_toString)
                                for w in lexemeList[koennenIndex+1:index]:
                                    if re.fullmatch("(ADV|APPR|PIS)", w.get("pos")) is None:
                                        lexeme.attrib.pop("causal", None)
                                        break


                    # ----- 7. von daher -----
                    if currentLemma == "daher" and index > 0 and lexemeList[index-1].get("lemma") == "von":
                        lexemeList[index].set("causal_2", "daher")
                        lexemeList[index-1].set("causal", "von_daher")


                    # ----- 8. deswegen -----
                    if currentLemma == "deswegen":
                        lexeme.set("causal", "deswegen")


                    # ----- 9. deshalb -----
                    if currentLemma == "deshalb":
                        lexeme.set("causal", "deswegen")


                    # ----- 10. darum -----
                    ### TODO: Check if these rules are correct! (Is "darum" consecutive only when it is at the beginning of a sentence and followed by a finit verb?)
                    if currentLemma == "darum" and index == 0:
                        if len(lexemeList) > 1 and re.fullmatch("V[AMV]FIN", lexemeList[index+1].get("pos")):
                            lexeme.set("causal", "darum")

                            # Exclude "Darum geht's":
                            if re.fullmatch("geht's", lexemeList[index+1].text):
                                lexeme.attrib.pop("causal", None)

                        # Exclude "Darum geht es":
                        if len(lexemeList) > 2 and lexemeList[index+1].get("lemma") == "gehen" and lexemeList[index+2].text == "es":
                            lexeme.attrib.pop("causal", None)


                    # ----- 11. dadurch -----
                    ### TODO: It's difficult to deal with "dadurch" with make rule-based annotation.

                    index += 1

            tree.write(os.path.join(r, filename), encoding="utf-8")
            processed_files += 1
            progress = processed_files / total_files * 100
            update_progress(progress)

logging.info("Done with annotating causal connectors.")