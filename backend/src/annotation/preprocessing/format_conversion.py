import os
import pandas as pd
import xml.etree.ElementTree as ET
from src.config import Config

def df_to_xml(filepath):
    outputRoot = Config.RAW_FILE_PATH

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