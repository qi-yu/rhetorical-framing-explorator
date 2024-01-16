import os, sys, zipfile
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom


def convert_to_xml(filepath, outputpath):
    """
    Convert .zip, .csv and .tsv files to XML.
    """
    for r, d, f in os.walk(filepath):
        for filename in f:
            if filename.endswith(".zip"):
                 with zipfile.ZipFile(os.path.join(r, filename), 'r') as zip_ref:
                     zip_ref.extractall(outputpath)

            if (filename.endswith(".csv") or filename.endswith(".tsv")) and filename.startswith(".") is False:
                separator = ""
                if filename.endswith('.tsv'):
                    separator = "\t"
                if filename.endswith('.csv'):
                    separator = ","

                df = pd.read_csv(os.path.join(r, filename), sep=separator, encoding="utf-8")

                for idx, row in df.iterrows():
                    document = ET.Element("document")
                    document.text = row["text"]
                    document.set("id", row["id"])
                    
                    if "label" in df.columns:
                        document.set("label", row["label"])

                    currentFileName = row["id"] + ".xml"

                    ET.ElementTree(document).write(os.path.join(outputpath, currentFileName), encoding="utf-8", xml_declaration=True)


def parse_xml_tree(filepath):
    """Parse an XML-file using xml.etree.ElementTree.

    Args:
        filepath (str): The path of the file to be parsed.

    Returns:
        mytree: The parsed XML-tree.
        myroot: The root of the parsed XML-tree.
    """
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


def update_progress(step_counter, total_step_amount, save_path):
    """
    Updating annotation progress.
    """
    step_counter += 1
    progress = step_counter / total_step_amount * 100
    
    with open(save_path, 'w') as file:
        file.write(str(round(progress)))

    return step_counter

