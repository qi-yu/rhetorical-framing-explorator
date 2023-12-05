import os, re, sys
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from src.config import Config


def df_to_xml(filepath, outputRoot):
    """
    Convert raw pandas dataframes to XML.
    """

    for r, d, f in os.walk(filepath):
        for filename in f:
            if filename.endswith(".csv") or filename.endswith(".tsv"):
                separator = ""
                if filename.endswith('.tsv'):
                    separator = "\t"
                if filename.endswith('.csv'):
                    separator = ","

                df = pd.read_csv(os.path.join(r, filename), sep=separator, encoding="utf-8")

                for idx, row in df.iterrows():
                    section = ET.Element("section")
                    topic = ET.SubElement(section, "topic")
                    utterance = ET.SubElement(topic, "utterance")
                    utterance.text = row["text"]

                    currentFileName = row["id"]

                    ET.ElementTree(section).write(os.path.join(outputRoot, currentFileName), encoding="utf-8", xml_declaration=True)


def parse_xml_tree(filepath):
    """Parse an XML-file using xml.etree.ElementTree.

    Args:
        filepath (str): The path of the file to be parsed.

    Returns:
        mytree: The parsed XML-tree.
        myroot: The root of the parsed XML-tree.
    """
    # print("Process file:", filepath, "...")
    mytree = ET.parse(filepath)
    myroot = mytree.getroot()
    return mytree, myroot


def prettify(elem):
    """Return a pretty-printed XML string for the Element.

    Args:
        elem: The XML element to be prettified.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")


def get_sentence_as_lexeme_list(sentence):
    """Get sentence as a list of lexemes.

    :param sentence: The sentence to be converted to lexeme list.
    :return: The sentence as a list of lexemes.
    """
    lexemeList = []
    for lexeme in sentence.findall("lexeme"):
        lexemeList.append(lexeme)

    return lexemeList

def get_sentence_as_text(sentence):
    """Get sentence as text.

    Arg:
        sentence: The sentence to be converted to text.

    Returns:
        sentencAsText (str): The sentence as text.
    """
    sentenceAsText = ""
    for lexeme in sentence.findall("lexeme"):
        sentenceAsText += lexeme.text + " "

    return sentenceAsText

def get_sentence_as_lemmatized_text(sentence):
    """Get sentence as lemmatized text.

    Arg:
        sentence: The sentence to be converted to text.

    Returns:
        sentencAsText (str): The sentence as text.
    """
    sentenceAsText = ""
    for lexeme in sentence.findall("lexeme"):
        sentenceAsText += lexeme.get("lemma") + " "

    return sentenceAsText


def get_du_as_lexeme_list(du):
    """Get discourse unit as a list of lexemes.

    :param du: The sentence to be converted to lexeme list.
    :return: The sentence as a list of lexemes.
    """
    return [lexeme for lexeme in du.findall("lexeme")]


def get_du_as_text(du):
    """Get discourse unit as text.

    Arg:
        du: The discourse unit to be converted to text.

    Returns:
        duAsText (str): The discourse unit as text.
    """
    duAsText = ""
    for lexeme in du.findall("lexeme"):
        duAsText += lexeme.text + " "

    return duAsText


def get_du_as_lemmatized_text(du):
    """Get discourse unit as lemmatized text.

    Arg:
        du: The discourse unit to be converted to text.

    Returns:
        duAsText (str): The discourse unit as text.
    """
    duAsText = ""
    for lexeme in du.findall("lexeme"):
        duAsText += lexeme.get("lemma") + " "

    return duAsText


def get_wordlist_from_txt(source):
    """Create a list of keywords from .txt files.

    Args:
        source: the path of the source lexicon.

    Returns:
        keywordList: A list of keywords.
    """
    keywordList = []
    with open(source) as f:
        for line in f.readlines():
            if line.startswith("#") is False:
                keywordList.append(line.strip())
    return keywordList


def annotate_finite_particle_verbs(lexemeList, cueList, label):
    """
    Annotating finite particle verbs. 
    They need to be handled specially, as their particle parts are separated from the verb stemms.
    """
    stemIndex = None
    stemListIndex = None
    particleGov = None
    particleListIndex = None

    for idx, lexeme in enumerate(lexemeList):
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
                if currentPV in cueList:
                    stemLexeme.set(label, currentPV)
                    particleLexeme.set(label + "_PTKVZ", currentPV)


def update_progress(step_counter, total_step_amount):
    """
    Updating annotation progress.
    """
    step_counter += 1
    progress = step_counter / total_step_amount * 100

    if not os.path.exists(Config.PROGRESS_PATH):
        os.mkdir(Config.PROGRESS_PATH)
        
    progress_file = os.path.join(Config.PROGRESS_PATH, sys.argv[1].split('.')[0] + '.txt') 
    with open(progress_file, 'w') as file:
        file.write(str(round(progress, 1)))

    return step_counter


def get_feature_list():
    feature_list = [#"negation",
                    #"within_indirect_speech", "within_direct_speech",
                    "exclamation", #"question",
                    "causal", #"consecutive", "adversative", "concessive", "conditional",
                    "common_ground", "resigned_accept", "weak_commit",
                    #"factive_verb", #"implicative_verb", "assertive_verb",
                    "booster", "hedge",
                    "adv_iter_cont", "scalar_particle",
                    #"representative", "declarative", "directive", "expressive", "commisive",
                    #"arousal", "valence", "concreteness", "imageability",
                    "natural_disaster_topoi", "social_disaster_topoi", "every_xth",
                    "economy", "identity", "legal", "morality", "policy", "politics", "public_opinion", "security", "welfare"
    ]

    return feature_list

