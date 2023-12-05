import re
from src.annotation.utils import get_wordlist_from_txt

class Annotation:

    def finite_particle_verbs(self, lexemeList, cueList, label):
        stemIndex = None
        stemListIndex = None
        particleGov = None
        particleListIndex = None

        for idx, lexeme in enumerate(lexemeList):
            if lexeme.get("pos") == "VVFIN":
                stemIndex = lexeme.get("index")
                stemListIndex = idx

            if re.fullmatch("(PTKVZ|ADV)", lexeme.get("pos")):
                particleGov = lexeme.get("governor")
                particleListIndex = idx

            if stemIndex and particleGov and particleGov == stemIndex:
                particleLexeme = lexemeList[particleListIndex]
                particleLemma = particleLexeme.get("lemma")
                stemLexeme = lexemeList[stemListIndex]
                stemLemma = stemLexeme.get("lemma")

                stemOptionList = stemLemma.split("|")
                for stem in stemOptionList:
                    currentPV = particleLemma + stem
                    if currentPV in cueList:
                        stemLexeme.set(label, currentPV)
                        particleLexeme.set(label + "_PTKVZ", currentPV)

                    
    def questions(self, lexemeList):
        for lexeme in lexemeList:
            if lexeme.text == "?":
                lexeme.set("question", "y")


    def exclamations(self, lexemeList):
        for lexeme in lexemeList:
            if lexeme.text == "!":
                lexeme.set("exclamation", "y")


    def causal(self, lexemeList):
        # ----- variables used for disambiguing "Grund" -----
        negGovList = []
         
        # ----- variables used for disambiguing "daher" -----
        finVerbStemIndex = None
        finVerbStemLemma = None
        finVerbStemListIndex = None
        koennenIndex = None
        koennenListIndex = None

        # ----- Start disambiguation -----
        for index, lexeme in enumerate(lexemeList):
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
                            for w in lexemeList[koennenIndex+1:index]:
                                if re.fullmatch("(ADV|APPR|PIS)", w.get("pos")) is None:
                                    lexeme.attrib.pop("causal", None)
                                    break


            # ----- 7. von daher -----
            if currentLemma == "daher" and index > 0 and lexemeList[index-1].get("lemma") == "von":
                lexemeList[index].set("causal_2", "daher")
                lexemeList[index-1].set("causal", "von_daher")


            # ----- 8. deswegen / deshalb -----
            if currentLemma in ["deswegen", "deshalb"]:
                lexeme.set("causal", currentLemma)

            # ----- 9. darum -----
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


            # ----- 10. dadurch -----
            ### TODO: It's difficult to deal with "dadurch" with make rule-based annotation.


    def adversative(self, lexemeList):
        findNichtNur = False # variable used for disambiguing "sondern" 
        findEinerseits = False # variable used for choosing label for "andererseits"

        for index, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")

            # ----- 1. Items that do not need disambiguation: -----
            if currentLemma in ["jedoch", "einerseits", "vielmehr", "andernfalls", "anderenfalls"]:
                lexeme.set("adversative", currentLemma)

            # ----- 2. Items that need disambiguation: -----
            ## 2.1 wiederum
            # ### TODO: How to disambiguate "wiederum" as adversative connector for opposition and "wiederum" with the meaning "again"?
            # if currentLemma == "wiederum":
            #     lexeme.set("adversative", "wiederum")

            ## 2.2 allerdings 
            ### TODO: How to disambiguate "allerdings" as adversative connector for opposition and "allerdings" as adverb for affirmation?
            if currentLemma == "allerdings":
                lexeme.set("adversative", "allerdings")

            ## 2.3 sondern
            # Exclude "sondern" in "nicht nur..., sondern (auch)...":
            if currentLemma == "nicht" and index < len(lexemeList)-1 and lexemeList[index+1].get("lemma") == "nur":
                findNichtNur = True

            if currentLemma == "sondern":
                if findNichtNur != True:
                    lexeme.set("adversative", "sondern")

                if index < len(lexemeList)-1 and lexemeList[index+1].get("lemma") == "auch":
                    lexeme.attrib.pop("adversative", None)

            ## 2.4 andererseits 
            if currentLemma == "andererseits":
                if findEinerseits:
                    lexeme.set("adversative_2", "andererseits")
                else: 
                    lexeme.set("adversative", "andererseits")

            ## 2.5 zum einen 
            if re.fullmatch("[Zz]u", lexeme.text) and index < len(lexemeList)-2 and re.fullmatch("dem", lexemeList[index+1].text) and re.fullmatch("einen", lexemeList[index+2].text):
                lexeme.set("adversative", "zum_einen")
                lexemeList[index+1].set("adversative_2", "dem")
                lexemeList[index+2].set("adversative_3", "einen")

            ## 2.6 zum anderen 
            if re.fullmatch("[Zz]u", lexeme.text) and index < len(lexemeList)-2 and re.fullmatch("dem", lexemeList[index+1].text) and re.fullmatch("anderen", lexemeList[index+2].text):
                lexeme.set("adversative_4", "zu")
                lexemeList[index + 1].set("adversative_5", "dem")
                lexemeList[index + 2].set("adversative_6", "anderen")

            ## 2.7 statt 
            if currentLemma == "statt" and currentPos != "PTKVZ":
                lexeme.set("adversative", "statt")

                # # Exclude cases like "Einen Tag zuvor gab es einen Kompromiss statt Krawall", because they don't express opposition relation on discourse level:
                # if index == 0:
                #     lexeme.set("adversative", "statt")
                #
                # if index > 0 and re.fullmatch("(\$,|KON)", lexemeList[index-1].get("pos")):
                #     lexeme.set("adversative", "statt")

            ## 2.8 anstatt 
            if currentLemma == "anstatt":
                lexeme.set("adversative", "anstatt")

                # # Exclude cases like "Zudem beginnen immer mehr junge Menschen ein Studium anstatt einer Ausbildung", because they don't express opposition relation on discourse level:
                # if index == 0:
                #     lexeme.set("adversative", "anstatt")
                #
                # if index > 0 and re.fullmatch("(\$,|KON)", lexemeList[index-1].get("pos")):
                #     lexeme.set("adversative", "anstatt")


    def boosters(self, lexemeList):
        booster_list = get_wordlist_from_txt("./src/annotation/wordlists/boosters.txt")

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

    
    def concessive(self, lexemeList):
        for index, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")

            # ----- 1. Items that do not need disambiguation: -----
            if currentLemma in ["dennoch", "trotzdem", "trotz", "gleichwohl", "wenngleich", "obschon", "nichtsdestotrotz", "nichtsdestoweniger"]:
                lexeme.set("concessive", currentLemma)

            # ----- 2. Items that need disambiguation: -----
            ## 2.1 obwohl
            if currentLemma == "obwohl":
                lexeme.set("concessive", "obwohl")

                # Exclude "obwohl" used for correcting the preceding proposition (i.e. followed by ,/./- + V2 sentences):
                # if index < len(lexemeList) - 1 and re.fullmatch("[,.-]", lexemeList[index+1].text):
                #     lexeme.attrib.pop("concessive", None)

            ## 2.2 wobei
            if currentLemma == "wobei" and index < len(lexemeList)-1 and re.fullmatch("[,.-]", lexemeList[index+1].text):
                lexeme.set("concessive", "wobei")

            ## 2.3 ungeachtet / ungeachtet dessen / dessen ungeachtet
            if currentLemma == "ungeachtet":
                lexeme.set("concessive", "ungeachtet")

                if index < len(lexemeList)-1 and lexemeList[index+1].text == "dessen":
                    lexemeList[index+1].set("concessive_2", "ungeachtet")
                
                if index > 0 and re.fullmatch("[Dd]essen", lexemeList[index-1].text):
                    lexemeList[index-1].set("concessive_2", "ungeachtet")


            ## 2.4 zwar
            # Exclude "zwar" in "und zwar":
            if currentLemma == "zwar" and index > 0 and lexemeList[index-1].get("lemma") != "und":
                lexeme.set("concessive", "zwar")

            ## 2.5 unbeschadet dessen 
            if currentLemma == "unbeschadet" and index < len(lexemeList)-1 and lexemeList[index+1].text == "dessen":
                lexeme.set("concessive", "unbeschadet_dessen")
                lexemeList[index+1].set("concessive_2", "dessen")


    def conditional(self, lexemeList):
        """
        Declaration of authorship:
        The annotation rules of this method was originally implemented by Marina Janka-Ramm.
        Qi Yu made some minor adaption and integrated them into the current app.
        """
        for index, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentWord = lexeme.text
            depRelation = lexeme.get("dependency_relation")

            # ----- 1. Items that do not need disambiguation  -----
            if currentLemma in ["wenn", "falls", "sofern", ]: # Qi: "ob" is excluded from this list. It is not always a conditional connector.
                lexeme.set("conditional", currentLemma)

            # ----- 2. gesetzt  -----
            if currentWord == "Gesetzt" or currentWord == "gesetzt" and index == 0:
                
                ## 2.1 gesetzt den Fall
                if len(lexemeList) > 2 and lexemeList[index+1].get("lemma") == "der" and lexemeList[index+2].get("lemma") == "Fall":
                    lexemeList[index].set("conditional", "gesetzt_den_Fall")
                    lexemeList[index+1].set("conditional_2", "den")
                    lexemeList[index+2].set("conditional_3", "Fall")
                
                ## 2.2  gesetzt
                if depRelation == "conj":
                    lexeme.set("conditional", "gesetzt")


    def factive_verbs(self, lexemeList):
        factive_list = get_wordlist_from_txt("./src/annotation/wordlists/factive_verbs.txt")

        # ----- 1. Items that do not need disambiguation -----
        for lexeme in lexemeList:
            if lexeme.get("lemma") in factive_list and re.fullmatch("(VVFIN|VVPP)", lexeme.get("pos")):
                lexeme.set("factive_verb", lexeme.get("lemma"))

        # ----- 2. Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, factive_list, "factive_verb")


    def hedges(self, lexemeList):
        hedges_list = get_wordlist_from_txt("./src/annotation/wordlists/hedges.txt")

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")

            # ----- 1. Monograms that do not need disambiguation -----
            if currentLemma in hedges_list:
                lexeme.set("hedge", currentLemma)

            # ----- 2. N-grams: -----
            ## 2.1 im Prinzip, im Wesentlichen, in der Regel:
            if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].get("lemma") == "der" and lexemeList[idx + 2].text in ["Prinzip", "Wesentlichen", "Regel"]:
                lexeme.set("hedge", "in_der_" + lexemeList[idx + 2].text)
                lexemeList[idx+1].set("hedge_2", "der")
                lexemeList[idx+2].set("hedge_3", lexemeList[idx + 2].get("lemma"))

            ## 2.2 in gewissem Maße:
            if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].text == "gewissem" and lexemeList[idx + 2].text == "Maße":
                lexeme.set("hedge", "in_gewissem_Maße" + lexemeList[idx + 2].text)
                lexemeList[idx + 1].set("hedge_2", "gewissem")
                lexemeList[idx + 2].set("hedge_3", "Maße")

            ## 2.3 im Grunde genommen:
            if idx < len(lexemeList) - 3 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].get("lemma") == "der" and lexemeList[idx + 2].text == "Grunde" and lexemeList[idx + 3].text == "genommen":
                lexeme.set("hedge", "im_Grunde_genommen" + lexemeList[idx + 2].text)
                lexemeList[idx + 1].set("hedge_2", "der")
                lexemeList[idx + 2].set("hedge_3", "Grunde")
                lexemeList[idx + 3].set("hedge_4", "genommen")

            # ## 2.4 in den meisten Fällen
            # if idx <= len(lexemeList)-4 and lexeme.text == "in" and lexemeList[idx+1].text == "den" and lexemeList[idx+2].text == "meisten" and lexemeList[idx+3].text == "Fällen":
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
            if idx < len(lexemeList) - 4 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].get("lemma") == "der" and lexemeList[idx + 2].text == "Großen" and lexemeList[idx + 3].text == "und" and lexemeList[idx + 4].text == "Ganzen":
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
            # if idx <= len(lexemeList)-3 and lexeme.get("lemma") == "unter" and lexemeList[idx+1].text == "bestimmten" and lexemeList[idx+2].text == "Umständen":
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


    def modal_particles_for_common_ground(self, lexemeList):
        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")

            # ----- 1. ja -----
            if currentLemma == "ja":
                lexeme.set("common_ground", "ja")

                # Exclude cases like "Oh ja", "Ach ja", "Und ja" etc.:
                if idx == 1 and re.fullmatch("(ADV|KON)", lexemeList[0].get("pos")):
                    lexeme.attrib.pop("common_ground", None)

                # Exclude "Na ja"
                if idx > 0 and lexemeList[idx-1].get("lemma") == "na":
                    lexeme.attrib.pop("common_ground", None)

                # Exclude "wenn ja (,|:) ....."
                if idx > 0 and idx < len(lexemeList)-1 and lexemeList[idx - 1].get("lemma") == "wenn" and re.fullmatch("[,:]", lexemeList[idx+1].text):
                    lexeme.attrib.pop("common_ground", None)

                # Exclude "ja" surrounded by punctuations
                if idx > 0 and idx < len(lexemeList)-1 and (re.fullmatch("\$[,.(]",lexemeList[idx-1].get("pos")) or re.fullmatch("\$[,.(]", lexemeList[idx+1].get("pos"))):
                    lexeme.attrib.pop("common_ground", None)

                # Exclude "ja" at the beginning of a sentence or a part-sentence
                # if idx > 0 and re.fullmatch("\$[,.(]", lexemeList[idx-1].get("pos")):
                #     lexeme.attrib.pop("common_ground", None)

                # Exclude "ja" in "..., ja genau, ..."
                if idx < len(lexemeList) - 2 and lexemeList[idx+1].get("lemma") == "genau" and re.fullmatch("[,.!-]", lexemeList[idx+2].text):
                    lexeme.attrib.pop("common_ground", None)

            # ----- 2. doch -----
            # if currentLemma == "doch" and currentPos == "ADV":
            #     lexeme.set("common_ground", "doch")
            #
            #     # Exclude "doch" at the beginning of a sentence or a part-sentence:
            #     if idx == 0 or (idx > 0 and lexemeList[idx-1].get("pos") == "KON"):
            #         lexeme.attrib.pop("common_ground", None)
            #
            #     # Exclude "doch" in "doch noch...", e.g. "dann kam Seehofer doch noch einmal auf das Streitthema Obergrenze zu sprechen"
            #     if idx < len(lexemeList)-1 and lexemeList[idx+1].get("lemma") == "noch":
            #         lexeme.attrib.pop("common_ground", None)
            #
            #     # Exclude "doch" in "Doch doch":
            #     if idx < len(lexemeList) - 1 and lexemeList[idx+1].get("lemma") == "doch":
            #         lexeme.attrib.pop("common_ground", None)


    def modal_particles_for_resigned_acceptance(self, lexemeList):
        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")
            
            # ----- 1. eben -----
            if currentLemma == "eben":
                lexeme.set("resigned_accept", "eben")

                # Exclude "eben" in "gerade eben":
                if idx > 0 and lexemeList[idx-1].get("lemma") == "gerade":
                    lexeme.attrib.pop("resigned_accept", None)

                # Exclude "eben" in "Ja eben, ..."
                if idx > 0 and lexemeList[idx-1].text == "Ja":
                    lexeme.attrib.pop("resigned_accept", None)

            # ----- 2. halt -----
            if currentLemma == "halt" and re.match("(ADV|ADJD)", currentPos):
                lexeme.set("resigned_accept", "halt")

    def modal_particles_for_weakened_commitment(self, lexemeList):
        # ----- variables used for disambiguing "wohl" -----
        wohlGov = None
        wohlIndex = None
        fuehlenIndex = None
        reflexGov = None

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")

            if currentLemma == "wohl" and currentPos == "ADV":
                wohlGov = lexeme.get("governor")
                wohlIndex = idx
                lexeme.set("weak_commit", "wohl")

                # Exclude "wohl" in "sehr wohl":
                if idx > 0 and lexemeList[idx-1].get("lemma") == "sehr":
                    lexeme.attrib.pop("weak_commit", None)

            # Exclude "wohl" in "sich wohl fühlen":
            if currentLemma == "fühlen":
                fuehlenIndex = lexeme.get("index")

            if re.search("Reflex=Yes", lexeme.get("feats")):
                reflexGov = lexeme.get("governor")

            if wohlGov is not None and fuehlenIndex is not None and reflexGov is not None:
                if wohlGov == fuehlenIndex and reflexGov == fuehlenIndex:
                    lexemeList[wohlIndex].attrib.pop("weak_commit", None)


    def adverbs_for_iteration_or_continuation(self, lexemeList):
        iter_cont_list = get_wordlist_from_txt("./src/annotation/wordlists/adverbs_for_iteration_or_continuation.txt")
        
        for idx, lexeme in enumerate(lexemeList):
            # ----- 1. Items that do not need disambiguation -----
            if lexeme.get("lemma") in iter_cont_list:
                lexeme.set("adv_iter_cont", lexeme.get("lemma"))

            # ----- 2. N-grams -----
            # 2.1 immer mehr
            if idx < len(lexemeList)-1 and lexeme.get("lemma") == "immer" and lexemeList[idx+1].get("lemma") == "mehr":
                lexeme.set("adv_iter_cont", "immer_mehr")
                lexemeList[idx+1].set("adv_iter_cont_2", "mehr")

            # 2.2 immer noch
            if idx < len(lexemeList)-1 and lexeme.get("lemma") == "immer" and lexemeList[idx+1].get("lemma") == "noch":
                lexeme.set("adv_iter_cont", "immer_noch")
                lexemeList[idx+1].set("adv_iter_cont_2", "noch")


    def scalar_particles(self, lexemeList):
        scalar_particle_list = get_wordlist_from_txt("./src/annotation/wordlists/scalar_particles.txt")

        for idx, lexeme in enumerate(lexemeList):
            # ----- 1. Items that do not need disambiguation -----
            if lexeme.get("lemma") in scalar_particle_list:
                lexeme.set("scalar_particle", lexeme.get("lemma"))

            # ----- 2. N-grams -----
            ## 2.1 nicht einmal / nicht mal
            if idx < len(lexemeList)-1 and lexeme.get("lemma") == "nicht" and lexemeList[idx+1].get("lemma") in ["einmal", "mal"]:
                lexeme.set("scalar_particle", "nicht_einmal")
                lexemeList[idx+1].set("scalar_particle_2", lexemeList[idx+1].get("lemma"))

            ## 2.2 geschweige denn
            if idx < len(lexemeList)-1 and re.fullmatch("geschweigen?", lexeme.get("lemma")) and lexemeList[idx+1].get("lemma") == "denn":
                lexeme.set("scalar_particle", "geschweige_denn")
                lexemeList[idx+1].set("scalar_particle_2", "denn")

            #TODO: Items that are difficult to disambiguate: wiederum, selbst, allein, auch nur

    