
import os, re, logging
from src.config import Config
from src.annotation.utils import parse_xml_tree, get_sentence_as_lexeme_list, get_sentence_as_text, get_wordlist_from_txt

logging.basicConfig(level=logging.INFO)

inputRoot = Config.PREPROCESSED_FILE_PATH

factive_list = get_wordlist_from_txt("./src/annotation/wordlists/factive_verbs.txt")

logging.info("Annotating factive verbs...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)
                lexemeList_toString = get_sentence_as_text(s)

                # ----- Variables used for particle verbs with stems and particles separated -----
                stemIndex = None
                stemListIndex = None
                particleGov = None
                particleListIndex = None

                for idx, lexeme in enumerate(lexemeList):
                    if lexeme.get("lemma") in factive_list and re.fullmatch("(VVFIN|VVPP)", lexeme.get("pos")):
                        lexeme.set("factive_verb", lexeme.get("lemma"))

                    # ----- 1. Deal with particle verbs -----
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
                            if currentPV in factive_list:
                                stemLexeme.set("factive_verb", currentPV)
                                particleLexeme.set("factive_verb_PTKVZ", currentPV)

            tree.write(os.path.join(r, filename), encoding="utf-8")

logging.info("Done with annotating factive verbs.")