import os, re, csv, shutil
import xml.etree.ElementTree as ET


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

def get_input_root():
    return "/Users/qiyu/PycharmProjects/Qi_LiAnS_noDU/data/output/newspapers/preprocessed"
