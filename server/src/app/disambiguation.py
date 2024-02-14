import re, os, logging
from src.app.utils import get_wordlist_from_txt
from src.config import Config

logging.basicConfig(level=logging.INFO)

class Disambiguation:
    wordlist_base_path = Config.WORD_LIST_BASE_PATH
    word_lists = {}

    def __init__(self):
        for filename in os.listdir(self.wordlist_base_path):
            feature = filename.split(".")[0]
            wordlist = get_wordlist_from_txt(os.path.join(self.wordlist_base_path, filename))
            self.word_lists[feature] = wordlist
    
    
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


                currentPV = particleLemma + stemLemma
                if currentPV in cueList:
                    stemLexeme.set(label, currentPV)
                    particleLexeme.set(label + "_PTKVZ", currentPV)

                    
    def questions(self, lexemeList):
        attr_name = self.questions.__name__

        for lexeme in lexemeList:
            if lexeme.text == "?":
                lexeme.set(attr_name, "y")


    def exclamations(self, lexemeList):
        attr_name = self.exclamations.__name__

        for lexeme in lexemeList:
            if lexeme.text == "!":
                lexeme.set(attr_name, "y")


    def causal(self, lexemeList):
        attr_name = self.causal.__name__

        # ----- variables used for disambiguing "Grund" -----
        negGovList = []
         
        # ----- variables used for disambiguing "daher" -----
        finVerbStemIndex = None
        finVerbStemLemma = None
        finVerbStemListIndex = None
        koennenIndex = None
        koennenListIndex = None

        # ----- Start disambiguation -----
        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")

            ### ----- Part 1: Causal connectors ----- ###
            # ----- 1. weil -----
            if currentLemma == "weil":
                lexeme.set(attr_name, "weil")

            # ----- 2. da -----
            if currentLemma == "da" and currentPos == "KOUS":
                lexeme.set(attr_name, "da")

                # Exclude "da" that are not at the beginning of a sentence or a part-sentence:
                if idx > 0 and re.fullmatch("(KON|\$[,.(])", lexemeList[idx-1].get("pos")) is None:
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "da" directly followed by comma, e.g. "Da , wo die Häuser stehen, ...":
                if idx < len(lexemeList)-1 and lexemeList[idx+1].text == ",":
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "da" in cases like "Da wo wir große Gefährdungen haben":
                if idx < len(lexemeList)-1 and lexemeList[idx+1].get("lemma") == "wo":
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "da" directly followed by a finite verb:
                if idx < len(lexemeList)-1 and re.fullmatch("V[AMV]FIN", lexemeList[idx+1].get("pos")):
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "da" in "hier und da":
                if idx > 1 and lexemeList[idx-2].get("lemma") == "hier" and lexemeList[idx-1].get("lemma") == "und":
                    lexeme.attrib.pop(attr_name, None)


            # ----- 3. denn -----
            if currentLemma == "denn":

                # Exclude cases like "mehr denn je"
                if currentPos == "KON" and idx+1 < len(lexemeList) and lexemeList[idx+1].get("lemma") != "je":
                    lexeme.set(attr_name, "denn")

                if idx+1 < len(lexemeList) and lexemeList[idx+1].get("lemma") == ":":
                    lexeme.set(attr_name, "denn")

                # Exclude "denn" in "Es sei denn, ..."
                if idx-1 >= 0 and lexemeList[idx-1].text == "sei":
                    lexeme.attrib.pop(attr_name, None)


            # ----- 4. Grund -----
            # if lexeme.get("negation") is not None:
            #     negGovList.append(lexeme.get("governor"))
            #
            # if currentLemma == "Grund":
            #     grundIndex = lexeme.get("index")
            #     lexeme.set(attr_name, "Grund")
            #
            #     # Exclude "Grund" with negation, such as "Es gibt keinen Grund, ...": They are not reasoning.
            #     if grundIndex in negGovList:
            #         lexeme.attrib.pop(attr_name, None)



            ### ----- Part 2: Consecutive connectors ----- ###
            # ----- 5. also -----
            ### TODO: Check if these rules are accurate enough!
            if currentLemma == "also" and currentPos == "ADV" and lexemeList[-1].text != "?" and lexemeList[-2].text != "?":
                lexeme.set(attr_name, "also")

                # Exclude "also" at the beginning of a sentence or a part-sentence which is not followed by a finite verb:
                if idx == 0 and len(lexemeList) > 1 and re.fullmatch("V[AMV]FIN", lexemeList[1].get("pos")) is None:
                    lexeme.attrib.pop(attr_name, None)

                if idx > 0 and idx < len(lexemeList)-1 and re.match("\$[,.(]", lexemeList[idx-1].get("pos")) and re.fullmatch("V[AMV]FIN", lexemeList[idx+1].get("pos")) is None:
                    lexeme.attrib.pop(attr_name, None)


            # ----- 6. daher -----
            if re.fullmatch("(kommen|rühren|rennen|laufen|fliegen|reiten|bringen|reden|stapfen)", currentLemma):
                finVerbStemIndex = lexeme.get("index")
                finVerbStemLemma = currentLemma
                finVerbStemListIndex = idx

            if currentLemma == "können":
                koennenIndex = lexeme.get("index")
                koennenListIndex = idx

            if currentLemma == "daher":
                if lexeme.get("governor") != finVerbStemIndex:
                    lexeme.set(attr_name, "daher")

                    if lexeme.get("governor") == finVerbStemIndex and finVerbStemLemma and re.fullmatch("(kommen|rühren)", finVerbStemLemma) :
                        # Annotate "daher" in cases like "Das kommt/rührt (aber auch) daher, ..." as "causal":
                        if finVerbStemListIndex < idx:
                            lexeme.set(attr_name, "daher")
                            for w in lexemeList[finVerbStemListIndex+1:idx]:
                                if re.fullmatch("(ADV|APPR|PIS)", w.get("pos")) is None:
                                    lexeme.attrib.pop(attr_name, None)
                                    break

                        # Annotate "daher" in cases like "Das kann auch daher kommen, ..." as "causal":
                        if koennenIndex and koennenListIndex < idx and finVerbStemListIndex == idx+1:
                            lexeme.set(attr_name, "daher")
                            for w in lexemeList[koennenIndex+1:idx]:
                                if re.fullmatch("(ADV|APPR|PIS)", w.get("pos")) is None:
                                    lexeme.attrib.pop(attr_name, None)
                                    break


            # ----- 7. von daher -----
            if currentLemma == "daher" and idx > 0 and lexemeList[idx-1].get("lemma") == "von":
                lexemeList[idx].set(attr_name + "_2", "daher")
                lexemeList[idx-1].set(attr_name, "von_daher")


            # ----- 8. deswegen / deshalb -----
            if currentLemma in ["deswegen", "deshalb"]:
                lexeme.set(attr_name, currentLemma)

            # ----- 9. darum -----
            ### TODO: Check if these rules are correct! (Is "darum" consecutive only when it is at the beginning of a sentence and followed by a finit verb?)
            if currentLemma == "darum" and idx == 0:
                if len(lexemeList) > 1 and re.fullmatch("V[AMV]FIN", lexemeList[idx+1].get("pos")):
                    lexeme.set(attr_name, "darum")

                    # Exclude "Darum geht's":
                    if re.fullmatch("geht's", lexemeList[idx+1].text):
                        lexeme.attrib.pop(attr_name, None)

                # Exclude "Darum geht es":
                if len(lexemeList) > 2 and lexemeList[idx+1].get("lemma") == "gehen" and lexemeList[idx+2].text == "es":
                    lexeme.attrib.pop(attr_name, None)


            # ----- 10. dadurch -----
            ### TODO: It's difficult to deal with "dadurch" with make rule-based annotation.


    def adversative(self, lexemeList):
        attr_name = self.adversative.__name__

        findNichtNur = False # variable used for disambiguing "sondern" 
        findEinerseits = False # variable used for choosing label for "andererseits"

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")

            # ----- 1. Items that do not need disambiguation: -----
            if currentLemma in ["jedoch", "einerseits", "vielmehr", "andernfalls", "anderenfalls"]:
                lexeme.set(attr_name, currentLemma)

            # ----- 2. Items that need disambiguation: -----
            ## 2.1 wiederum
            # ### TODO: How to disambiguate "wiederum" as adversative connector for opposition and "wiederum" with the meaning "again"?
            # if currentLemma == "wiederum":
            #     lexeme.set(attr_name, "wiederum")

            ## 2.2 allerdings 
            ### TODO: How to disambiguate "allerdings" as adversative connector for opposition and "allerdings" as adverb for affirmation?
            if currentLemma == "allerdings":
                lexeme.set(attr_name, "allerdings")

            ## 2.3 sondern
            # Exclude "sondern" in "nicht nur..., sondern (auch)...":
            if currentLemma == "nicht" and idx < len(lexemeList)-1 and lexemeList[idx+1].get("lemma") == "nur":
                findNichtNur = True

            if currentLemma == "sondern":
                if findNichtNur != True:
                    lexeme.set(attr_name, "sondern")

                if idx < len(lexemeList)-1 and lexemeList[idx+1].get("lemma") == "auch":
                    lexeme.attrib.pop(attr_name, None)

            ## 2.4 andererseits 
            if currentLemma == "andererseits":
                if findEinerseits:
                    lexeme.set(attr_name + "_2", "andererseits")
                else: 
                    lexeme.set(attr_name, "andererseits")

            ## 2.5 zum einen 
            if re.fullmatch("[Zz]um", lexeme.text) and idx < len(lexemeList)-1 and lexemeList[idx+1].text == "einen":
                lexeme.set(attr_name, "zum_einen")
                lexemeList[idx+1].set(attr_name + "_2", "einen")

            ## 2.6 zum anderen 
            if re.fullmatch("[Zz]um", lexeme.text) and idx < len(lexemeList)-1 and lexemeList[idx+1].text == "anderen":
                lexeme.set(attr_name + "_3", "zum")
                lexemeList[idx + 1].set(attr_name + "_4", "anderen")

            ## 2.7 statt 
            if currentLemma == "statt" and currentPos != "PTKVZ":
                lexeme.set(attr_name, "statt")

                # # Exclude cases like "Einen Tag zuvor gab es einen Kompromiss statt Krawall", because they don't express opposition relation on discourse level:
                # if idx == 0:
                #     lexeme.set(attr_name, "statt")
                #
                # if idx > 0 and re.fullmatch("(\$,|KON)", lexemeList[idx-1].get("pos")):
                #     lexeme.set(attr_name, "statt")

            ## 2.8 anstatt 
            if currentLemma == "anstatt":
                lexeme.set(attr_name, "anstatt")

                # # Exclude cases like "Zudem beginnen immer mehr junge Menschen ein Studium anstatt einer Ausbildung", because they don't express opposition relation on discourse level:
                # if idx == 0:
                #     lexeme.set(attr_name, "anstatt")
                #
                # if idx > 0 and re.fullmatch("(\$,|KON)", lexemeList[idx-1].get("pos")):
                #     lexeme.set(attr_name, "anstatt")


    def boosters(self, lexemeList):
        attr_name = self.boosters.__name__
        booster_list = self.word_lists[self.boosters.__name__]

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")
            currentGovenor = lexeme.get("governor")

            # ----- 1. Monograms that do not need disambiguation: -----
            if currentLemma in booster_list:
                lexeme.set(attr_name, currentLemma)

            # ----- 2. N-grams -----
            ## 2.1 erst recht:
            if idx < len(lexemeList) - 1 and lexeme.get("lemma") == "erst" and lexemeList[idx + 1].get("lemma") == "recht":
                lexeme.set(attr_name, "erst_recht")
                lexemeList[idx+1].set(attr_name + "_2", "recht")

            ## 2.2 bei weitem:
            if idx < len(lexemeList) - 1 and lexeme.get("lemma") == "bei" and lexemeList[idx + 1].text == "weitem":
                lexeme.set(attr_name, "bei_weitem")
                lexemeList[idx+1].set(attr_name + "_2", "weitem")

            ## 2.3 ganz und gar:
            if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "ganz" and lexemeList[idx + 1].text == "und" and lexemeList[idx + 2].text == "gar":
                lexeme.set(attr_name, "ganz_und_gar")
                lexemeList[idx + 1].set(attr_name + "_2", "und")
                lexemeList[idx + 1].set(attr_name + "_3", "gar")

            # ----- 3. Items that need disambiguation:
            # 3.1 Items that should only be annotated as booster when bearing the POS "ADJD":
            if currentLemma in ["ausgesprochen", "entschieden", "komplett", "wesentlich"] and currentPos == "ADJD":
                lexeme.set(attr_name, currentLemma)

            ## 3.2 Items that should only be annotated as booster when bearing the POS "ADV":
            if currentLemma in ["tatsächlich", "viel", "weit"] and currentPos == "ADV":
                lexeme.set(attr_name, currentLemma)

            ## 3.3 Items that should only be annotated as booster only when modifying adjectives/adverbs:
            if currentLemma in ["denkbar", "echt", "richtig", "wirklich"]:
                for l in lexemeList:
                    if l.get("index") == currentGovenor and l.get("pos").startswith("AD"):
                        lexeme.set(attr_name, currentLemma)

            ## 3.4 absolut: exclude usages in "absolute [Zz]ahl$"
            if currentLemma == "absolut" and re.search("[Zz]ahl$", lexemeList[idx+1].get("lemma")) is None:
                lexeme.set(attr_name, currentLemma)

            ## 3.5. total:
            if currentLemma == "total" and currentPos in ["ADJD", "ADJA"]:
                lexeme.set(attr_name, currentLemma)

            ## 3.6. ganz:
            if currentLemma == "ganz" and currentPos in ["ADJD", "ADV"] and lexeme.get("booster") != "ganz_und_gar": # not already annotated as "ganz und gar"
                lexeme.set(attr_name, currentLemma)

            ## 3.7 höchst:
            if lexeme.text == "höchst":
                lexeme.set(attr_name, currentLemma)

            ## 3.8 recht:
            if currentLemma == "recht" and currentPos == "ADV" and lexeme.get("booster") != "erst_recht": # not already annotated as "erst_recht"
                for l in lexemeList:
                    if  l.get("index") == currentGovenor and l.get("lemma") not in ["haben", "behalten", "geben", "kommen", "bekommen"]:
                        lexeme.set(attr_name, currentLemma)

    
    def concessive(self, lexemeList):
        attr_name = self.concessive.__name__

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")

            # ----- 1. Items that do not need disambiguation: -----
            if currentLemma in ["dennoch", "trotzdem", "trotz", "gleichwohl", "wenngleich", "obschon", "nichtsdestotrotz", "nichtsdestoweniger"]:
                lexeme.set(attr_name, currentLemma)

            # ----- 2. Items that need disambiguation: -----
            ## 2.1 obwohl
            if currentLemma == "obwohl":
                lexeme.set(attr_name, "obwohl")

                # Exclude "obwohl" used for correcting the preceding proposition (i.e. followed by ,/./- + V2 sentences):
                # if idx < len(lexemeList) - 1 and re.fullmatch("[,.-]", lexemeList[idx+1].text):
                #     lexeme.attrib.pop(attr_name, None)

            ## 2.2 wobei
            if currentLemma == "wobei" and idx < len(lexemeList)-1 and re.fullmatch("[,.-]", lexemeList[idx+1].text):
                lexeme.set(attr_name, "wobei")

            ## 2.3 ungeachtet / ungeachtet dessen / dessen ungeachtet
            if currentLemma == "ungeachtet":
                lexeme.set(attr_name, "ungeachtet")

                if idx < len(lexemeList)-1 and lexemeList[idx+1].text == "dessen":
                    lexemeList[idx+1].set(attr_name + "_2", "ungeachtet")
                
                if idx > 0 and re.fullmatch("[Dd]essen", lexemeList[idx-1].text):
                    lexemeList[idx-1].set(attr_name + "_2", "ungeachtet")


            ## 2.4 zwar
            # Exclude "zwar" in "und zwar":
            if currentLemma == "zwar" and idx > 0 and lexemeList[idx-1].get("lemma") != "und":
                lexeme.set(attr_name, "zwar")

            ## 2.5 unbeschadet dessen 
            if currentLemma == "unbeschadet" and lexemeList[idx+1].get("feats").startswith("Case=Gen"):
                lexeme.set(attr_name, "unbeschadet")
            
                if lexemeList[idx+1].text == "dessen":
                    lexemeList[idx+1].set(attr_name + "_2", "dessen")


    def conditional(self, lexemeList):
        """
        Declaration of authorship:
        The annotation rules of this method was originally implemented by Marina Janka-Ramm.
        Qi Yu made the following changes:
            1) some minor adaption to the rule; 
            2) the integration of the rules into the architecture of the current app.
        """

        attr_name = self.conditional.__name__

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentWord = lexeme.text
            depRelation = lexeme.get("dependency_relation")

            # ----- 1. Items that do not need disambiguation  -----
            if currentLemma in ["wenn", "falls", "sofern", ]: # Qi: "ob" is excluded from this list. It is not always a conditional connector.
                lexeme.set(attr_name, currentLemma)

            # ----- 2. gesetzt  -----
            if currentWord == "Gesetzt" or currentWord == "gesetzt" and idx == 0:
                
                ## 2.1 gesetzt den Fall
                if len(lexemeList) > 2 and lexemeList[idx+1].get("lemma") == "der" and lexemeList[idx+2].get("lemma") == "Fall":
                    lexemeList[idx].set(attr_name, "gesetzt_den_Fall")
                    lexemeList[idx+1].set(attr_name + "_2", "den")
                    lexemeList[idx+2].set(attr_name + "_3", "Fall")
                
                ## 2.2  gesetzt
                if depRelation == "conj":
                    lexeme.set(attr_name, "gesetzt")


    def factive_verbs(self, lexemeList):
        attr_name = self.factive_verbs.__name__
        factive_list = self.word_lists[self.factive_verbs.__name__]

        # ----- 1. Items that do not need disambiguation -----
        for lexeme in lexemeList:
            if lexeme.get("lemma") in factive_list and re.fullmatch("(VVFIN|VVPP)", lexeme.get("pos")):
                lexeme.set(attr_name, lexeme.get("lemma"))

        # ----- 2. Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, factive_list, attr_name)


    def hedges(self, lexemeList):
        attr_name = self.hedges.__name__
        hedges_list = self.word_lists[self.hedges.__name__]

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")

            # ----- 1. Monograms that do not need disambiguation -----
            if currentLemma in hedges_list:
                lexeme.set(attr_name, currentLemma)

            # ----- 2. N-grams: -----
            ## 2.1 im Prinzip, im Wesentlichen,
            if idx < len(lexemeList) - 1 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].text in ["Prinzip", "Wesentlichen"]:
                lexeme.set(attr_name, "im_" + lexemeList[idx + 1].text)
                lexemeList[idx+1].set(attr_name + "_2", lexemeList[idx + 1].text)

            ## 2.2 in der Regel:
            if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].get("lemma") == "der" and lexemeList[idx + 2].get("lemma") == "Regel":
                lexeme.set(attr_name, "in_der_Regel")
                lexemeList[idx + 1].set(attr_name + "_2", "der")
                lexemeList[idx + 2].set(attr_name + "_3", "Regel")

            ## 2.3 in gewissem Maße:
            if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].text == "gewissem" and lexemeList[idx + 2].text == "Maße":
                lexeme.set(attr_name, "in_gewissem_Maße")
                lexemeList[idx + 1].set(attr_name + "_2", "gewissem")
                lexemeList[idx + 2].set(attr_name + "_3", "Maße")

            ## 2.4 im Grunde genommen:
            if idx < len(lexemeList) - 2 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].text == "Grunde" and lexemeList[idx + 2].text == "genommen":
                lexeme.set(attr_name, "im_Grunde_genommen")
                lexemeList[idx + 1].set(attr_name + "_2", "Grunde")
                lexemeList[idx + 2].set(attr_name + "_3", "genommen")

            # ## 2.5 in den meisten Fällen
            # if idx <= len(lexemeList)-4 and lexeme.text == "in" and lexemeList[idx+1].text == "den" and lexemeList[idx+2].text == "meisten" and lexemeList[idx+3].text == "Fällen":
            #     lexeme.set(attr_name, "in_den_meisten_Faellen")
            #     lexemeList[idx+1].set(attr_name + "_2", "den")
            #     lexemeList[idx+2].set(attr_name + "_3", "meisten")
            #     lexemeList[idx+3].set(attr_name + "_4", "Faellen")

            ## 2.6 zu großen Teilen
            # if idx <= len(lexemeList)-3 and lexeme.text == "zu" and lexemeList[idx+1].text == "großen" and lexemeList[idx+2].text == "Teilen":
            #     lexeme.set(attr_name, "zu_grossen_Teilen")
            #     lexemeList[idx + 1].set(attr_name + "_2", "grossen")
            #     lexemeList[idx + 2].set(attr_name + "_3", "Teilen")

            ## 2.7 Pi mal Daumen
            if idx <= len(lexemeList)-3 and lexeme.text == "Pi" and lexemeList[idx+1].text == "mal" and lexemeList[idx+2].text == "Daumen":
                lexeme.set(attr_name, "Pi_mal_Daumen")
                lexemeList[idx + 1].set(attr_name + "_2", "mal")
                lexemeList[idx + 2].set(attr_name + "_3", "Daumen")

            ## 2.8 im Großen und Ganzen
            if idx < len(lexemeList) - 3 and lexeme.get("lemma") == "in" and lexemeList[idx + 1].text == "Großen" and lexemeList[idx + 2].text == "und" and lexemeList[idx + 3].text == "Ganzen":
                lexeme.set(attr_name, "im_Großen_und_Ganzen")
                lexemeList[idx + 1].set(attr_name + "_2", "Großen")
                lexemeList[idx + 2].set(attr_name + "_3", "und")
                lexemeList[idx + 3].set(attr_name + "_4", "Ganzen")

            ## 2.9 streng genommen
            if idx < len(lexemeList) - 1 and lexeme.get("lemma") == "streng" and lexemeList[idx + 1].text == "genommen":
                lexeme.set(attr_name, "streng_genommen")
                lexemeList[idx+1].set(attr_name + "_2", "genommen")

            ## 2.10 unter bestimmten Umständen
            # if idx <= len(lexemeList)-3 and lexeme.get("lemma") == "unter" and lexemeList[idx+1].text == "bestimmten" and lexemeList[idx+2].text == "Umständen":
            #     lexeme.set(attr_name, "unter_bestimmten_Umstaenden")
            #     lexemeList[idx + 1].set(attr_name + "_2", "bestimmten")
            #     lexemeList[idx + 2].set(attr_name + "_3", "Umstaenden")
        
            # ----- 3. Items that need disambiguation: -----
            ## 3.1 Verbs:
            if currentLemma in  ["scheinen", "vermuten", "spekulieren"] and re.fullmatch("(VVFIN|VVPP)", currentPos):
                lexeme.set(attr_name, currentLemma)

            ## 3.2 Modal verbs:
            # TODO: CHECK IF THE RULES ARE CORRECT!
            if currentLemma in ["können", "müssen", "sollen", "werden"] and re.match("(könnt|müsst|sollt|würd)", lexeme.text):
                lexeme.set(attr_name, currentLemma)

            ## 3.3 Items that should only be annotated as hedge when bearing the POS "ADV":
            if currentLemma in ["etwas", "grob"] and currentPos == "ADV":
                lexeme.set(attr_name, currentLemma)

            ## 3.4 annähernd:
            if lexeme.get("lemma") == "annähernd":
                lexeme.set(attr_name, currentLemma)

            ## 3.5 wohl: annotated by the method "modal_particles.py"


    def modal_particles_for_common_ground(self, lexemeList):
        attr_name = self.modal_particles_for_common_ground.__name__

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")

            # ----- 1. ja -----
            if currentLemma == "ja":
                lexeme.set(attr_name, "ja")

                # Exclude cases like "Oh ja", "Ach ja", "Und ja" etc.:
                if idx == 1 and re.fullmatch("(ADV|KON)", lexemeList[0].get("pos")):
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "Na ja"
                if idx > 0 and lexemeList[idx-1].get("lemma") == "na":
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "wenn ja (,|:) ....."
                if idx > 0 and idx < len(lexemeList)-1 and lexemeList[idx - 1].get("lemma") == "wenn" and re.fullmatch("[,:]", lexemeList[idx+1].text):
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "ja" surrounded by punctuations
                if idx > 0 and idx < len(lexemeList)-1 and (re.fullmatch("\$[,.(]",lexemeList[idx-1].get("pos")) or re.fullmatch("\$[,.(]", lexemeList[idx+1].get("pos"))):
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "ja" at the beginning of a sentence or a part-sentence
                # if idx > 0 and re.fullmatch("\$[,.(]", lexemeList[idx-1].get("pos")):
                #     lexeme.attrib.pop(attr_name, None)

                # Exclude "ja" in "..., ja genau, ..."
                if idx < len(lexemeList) - 2 and lexemeList[idx+1].get("lemma") == "genau" and re.fullmatch("[,.!-]", lexemeList[idx+2].text):
                    lexeme.attrib.pop(attr_name, None)

            # ----- 2. doch -----
            # if currentLemma == "doch" and currentPos == "ADV":
            #     lexeme.set(attr_name, "doch")
            #
            #     # Exclude "doch" at the beginning of a sentence or a part-sentence:
            #     if idx == 0 or (idx > 0 and lexemeList[idx-1].get("pos") == "KON"):
            #         lexeme.attrib.pop(attr_name, None)
            #
            #     # Exclude "doch" in "doch noch...", e.g. "dann kam Seehofer doch noch einmal auf das Streitthema Obergrenze zu sprechen"
            #     if idx < len(lexemeList)-1 and lexemeList[idx+1].get("lemma") == "noch":
            #         lexeme.attrib.pop(attr_name, None)
            #
            #     # Exclude "doch" in "Doch doch":
            #     if idx < len(lexemeList) - 1 and lexemeList[idx+1].get("lemma") == "doch":
            #         lexeme.attrib.pop(attr_name, None)


    def modal_particles_for_resigned_acceptance(self, lexemeList):
        attr_name = self.modal_particles_for_resigned_acceptance.__name__

        for idx, lexeme in enumerate(lexemeList):
            currentLemma = lexeme.get("lemma")
            currentPos = lexeme.get("pos")
            
            # ----- 1. eben -----
            if currentLemma == "eben":
                lexeme.set(attr_name, "eben")

                # Exclude "eben" in "gerade eben":
                if idx > 0 and lexemeList[idx-1].get("lemma") == "gerade":
                    lexeme.attrib.pop(attr_name, None)

                # Exclude "eben" in "Ja eben, ..."
                if idx > 0 and lexemeList[idx-1].text == "Ja":
                    lexeme.attrib.pop(attr_name, None)

            # ----- 2. halt -----
            if currentLemma == "halt" and re.match("(ADV|ADJD)", currentPos):
                lexeme.set(attr_name, "halt")


    def modal_particles_for_weakened_commitment(self, lexemeList):
        attr_name = self.modal_particles_for_weakened_commitment.__name__
        attr_name_2 = self.hedges.__name__

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
                lexeme.set(attr_name, "wohl")
                lexeme.set(attr_name_2, "wohl")

                # Exclude "wohl" in "sehr wohl":
                if idx > 0 and lexemeList[idx-1].get("lemma") == "sehr":
                    lexeme.attrib.pop(attr_name, None)
                    lexeme.attrib.pop(attr_name_2, None)

            # Exclude "wohl" in "sich wohl fühlen":
            if currentLemma == "fühlen":
                fuehlenIndex = lexeme.get("index")

            if re.search("Reflex=Yes", lexeme.get("feats")):
                reflexGov = lexeme.get("governor")

            if wohlGov is not None and fuehlenIndex is not None and reflexGov is not None:
                if wohlGov == fuehlenIndex and reflexGov == fuehlenIndex:
                    lexemeList[wohlIndex].attrib.pop(attr_name, None)
                    lexemeList[wohlIndex].attrib.pop(attr_name_2, None)


    def adverbs_for_iteration_or_continuation(self, lexemeList):
        attr_name = self.adverbs_for_iteration_or_continuation.__name__
        iter_cont_list = self.word_lists[self.adverbs_for_iteration_or_continuation.__name__]
        
        for idx, lexeme in enumerate(lexemeList):
            # ----- 1. Items that do not need disambiguation -----
            if lexeme.get("lemma") in iter_cont_list:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- 2. N-grams -----
            # 2.1 immer mehr / immer noch
            if idx < len(lexemeList)-1 and lexeme.get("lemma") == "immer" and lexemeList[idx+1].get("lemma") in ["mehr", "noch"]:
                lexeme.set(attr_name, "immer_" + lexemeList[idx+1].get("lemma"))
                lexemeList[idx+1].set(attr_name + "_2", lexemeList[idx+1].get("lemma"))


    def scalar_particles(self, lexemeList):
        attr_name = self.scalar_particles.__name__
        scalar_particle_list = self.word_lists[self.scalar_particles.__name__]

        for idx, lexeme in enumerate(lexemeList):
            # ----- 1. Items that do not need disambiguation -----
            if lexeme.get("lemma") in scalar_particle_list:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- 2. N-grams -----
            ## 2.1 nicht einmal / nicht mal
            if idx < len(lexemeList)-1 and lexeme.get("lemma") == "nicht" and lexemeList[idx+1].get("lemma") in ["einmal", "mal"]:
                lexeme.set(attr_name, "nicht_" + lexemeList[idx+1].get("lemma"))
                lexemeList[idx+1].set(attr_name + "_2", lexemeList[idx+1].get("lemma"))

            ## 2.2 geschweige denn
            if idx < len(lexemeList)-1 and re.fullmatch("geschweigen?", lexeme.get("lemma")) and lexemeList[idx+1].get("lemma") == "denn":
                lexeme.set(attr_name, "geschweige_denn")
                lexemeList[idx+1].set(attr_name + "_2", "denn")

            #TODO: Items that are difficult to disambiguate: wiederum, selbst, allein, auch nur

    
    def indirect_speech(self, lexemeList):
        attr_name = self.indirect_speech.__name__
        has_konjunktiv_1 = False
        
        for lexeme in lexemeList:
            if re.search("Mood=Sub", lexeme.get("feats")):
                currentLemma = lexeme.get("lemma")
                currentText = lexeme.text

                ### ----- Third person singular -----
                if re.search("Number=Sing\|Person=3", lexeme.get("feats")):
                    if currentLemma[-2:] == "en" and currentText == currentLemma[:-2] + "e":
                        has_konjunktiv_1 = True

                    if currentLemma[-2:] != "en" and currentText == currentLemma[:-1] + "e":
                        has_konjunktiv_1 = True

                ### ----- Verb "sein" -----
                if re.fullmatch("(seie?st|seien|seiet|sei)", currentText):
                    has_konjunktiv_1 = True

        if has_konjunktiv_1 == True:
            for lexeme in lexemeList:
                lexeme.set(attr_name, "y")


    def direct_speech(self, allLexemesOfDocument):
        attr_name = self.direct_speech.__name__
        first_quotation_idx = None
        second_quotation_idx = None
        
        for idx, lexeme in enumerate(allLexemesOfDocument):
            if lexeme.text == '"':
                if first_quotation_idx is None:
                    first_quotation_idx = idx
                else:
                    second_quotation_idx = idx

                    for i in allLexemesOfDocument[first_quotation_idx + 1 : second_quotation_idx]:
                        i.set(attr_name, "y")

                        first_quotation_idx = None
                        second_quotation_idx = None

    
    def economy(self, lexemeList):
        attr_name = self.economy.__name__
        cueList = self.word_lists[self.economy.__name__]

        # ----- 1. Items that do not need disambiguation -----
        for lexeme in lexemeList:
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

        # ----- 2. Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)

    
    def identity(self, lexemeList):
        attr_name = self.identity.__name__
        cueList = self.word_lists[self.identity.__name__]

        # ----- 1. Items that do not need disambiguation -----
        for lexeme in lexemeList:
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- Deal with multi-word expressions / ambiguous words -----
            ## "Christin":
            if lexeme.text == "Christin" and lexeme.get("pos") != "NE":
                lexeme.set("identity", "Christin")

        # ----- 2. Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)

    
    def legal(self, lexemeList):
        attr_name = self.legal.__name__
        cueList = self.word_lists[self.legal.__name__]

        for idx, lexeme in enumerate(lexemeList):
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- Deal with multi-word expressions / ambiguous words -----
            ## "Burka-Verbot":
            if lexeme.text == "Burka" and idx < len(lexemeList) - 2 and lexemeList[idx+1].text == "-" and lexemeList[idx+2].text == "Verbot":
                lexeme.set("attr_name", "Burka-Verbot")
                lexemeList[idx + 1].set(attr_name + "_2", "-")
                lexemeList[idx + 2].set(attr_name + "_3", "Verbot")

        # ----- Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)


    def morality(self, lexemeList):
        attr_name = self.morality.__name__
        cueList = self.word_lists[self.morality.__name__]

        # ----- 1. Items that do not need disambiguation -----
        for lexeme in lexemeList:
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

        # ----- 2. Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)

    
    def policy(self, lexemeList):
        attr_name = self.policy.__name__
        cueList = self.word_lists[self.policy.__name__]

        for idx, lexeme in enumerate(lexemeList):
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- Deal with multi-word expressions / ambiguous words -----
            ## "Genfer Flüchtlingskonvention":
            if lexeme.text == "Genfer" and idx < len(lexemeList) - 1 and re.fullmatch("(Flüchtlingskonvention|Flüchtlingskonventionen|Konventionen|Abkommen)", lexemeList[idx+1].text):
                lexeme.set(attr_name, "Genfer_Fluechtlingskonvention")
                lexemeList[idx+1].set(attr_name + "_2", "Fluechtlingskonvention")

        # ----- Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)
       

    def politics(self, lexemeList):
        attr_name = self.politics.__name__
        cueList = self.word_lists[self.politics.__name__]

        for idx, lexeme in enumerate(lexemeList):
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- Deal with multi-word expressions / ambiguous words -----
            ## "grün-rot", "grün-schwarz" etc.:
            if idx < len(lexemeList) - 2 and lexeme.get("lemma") in ["gelb", "grün", "rot", "schwarz"] and lexemeList[idx+1].text == "-" and lexemeList[idx+2].get("lemma") in ["gelb", "grün", "rot", "schwarz"]:
                lexeme.set(attr_name, lexeme.get("lemma"))
                lexemeList[idx + 1].set(attr_name + "_2", "-")
                lexemeList[idx + 2].set(attr_name + "_3", lexemeList[idx+2].get("lemma"))

        # ----- Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)

    
    def public_opinion(self, lexemeList):
        attr_name = self.public_opinion.__name__
        cueList = self.word_lists[self.public_opinion.__name__]

        for idx, lexeme in enumerate(lexemeList):
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- Deal with multi-word expressions / ambiguous words -----
            ## "Öffentlich* Eindruck/Gefühl/Interesse":
            if lexeme.get("lemma") == "öffentlich" and idx < len(lexemeList) - 1 and lexemeList[idx+1].get("lemma") == "Eindruck":
                lexeme.set(attr_name, "oeffentlicher_Eindruck")
                lexemeList[idx+1].set(attr_name + "_2", "Eindruck")

            if lexeme.get("lemma") == "öffentlich" and idx < len(lexemeList) - 1 and lexemeList[idx+1].get("lemma") == "Gefühl":
                lexeme.set(attr_name, "oeffentliches_Gefuehl")
                lexemeList[idx+1].set(attr_name + "_2", "Gefuehl")

            if lexeme.get("lemma") == "öffentlich" and idx < len(lexemeList) - 1 and lexemeList[idx+1].get("lemma") == "Interesse":
                lexeme.set(attr_name, "oeffentliches_Interesse")
                lexemeList[idx+1].set(attr_name + "_2", "Interesse")

        # ----- Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)


    def security(self, lexemeList):
        attr_name = self.security.__name__
        cueList = self.word_lists[self.security.__name__]

        for idx, lexeme in enumerate(lexemeList):
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- Deal with multi-word expressions / ambiguous words -----
            ## "U-Haft":
            if lexeme.text == "U-" and idx < len(lexemeList) - 1 and lexemeList[idx+1].text == "Haft":
                lexeme.set(attr_name, "U-Haft")
                lexemeList[idx+1].set(attr_name + "_2", "Haft")

        # ----- Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)

    
    def welfare(self, lexemeList):
        attr_name = self.welfare.__name__
        cueList = self.word_lists[self.welfare.__name__]

        for idx, lexeme in enumerate(lexemeList):
            if lexeme.get("lemma") in cueList:
                lexeme.set(attr_name, lexeme.get("lemma"))

            # ----- Deal with multi-word expressions / ambiguous words -----
            ## "finanzielle Unterstützung": 
            if lexeme.get("lemma") == "finanziell" and idx < len(lexemeList) - 1 and lexemeList[idx+1].get("lemma") == "Unterstützung":
                lexeme.set(attr_name, "finanzielle_Unterstuetzung")
                lexemeList[idx+1].set(attr_name + "_2", "Unterstuetzung")
            
            ## "Soziale Sicherung":
            if lexeme.get("lemma") == "sozial" and idx < len(lexemeList) - 1 and lexemeList[idx+1].get("lemma") == "Sicherung":
                lexeme.set(attr_name, "soziale_Sicherung")
                lexemeList[idx+1].set(attr_name + "_2", "Sicherung")

        # ----- Deal with particle verbs -----
        self.finite_particle_verbs(lexemeList, cueList, attr_name)