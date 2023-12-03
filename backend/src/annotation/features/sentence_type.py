#!/usr/bin/env python3

# Author: Qi Yu
# Date: 17.02.2022

#####################################################################################
#                         Project Information
#
# This is a dictionary- and rule-based annotation for interrogatives and exclamatives.
#
#####################################################################################

import os, re
from main.utilities.annotation_utils import parse_xml_tree, get_input_root, get_sentence_as_lexeme_list, get_sentence_as_text

inputRoot = get_input_root()

print("Annotating sentence type...")
for r, d, f in os.walk(inputRoot):
    for filename in f:
        if filename.endswith(".xml"):
            tree, root = parse_xml_tree(os.path.join(r, filename))

            for s in root.iter("sentence"):
                lexemeList = get_sentence_as_lexeme_list(s)

                for lexeme in lexemeList:
                    if lexeme.text == "?":
                        lexeme.set("question", "y")

                    if lexeme.text == "!":
                        lexeme.set("exclamation", "y")

            tree.write(os.path.join(r, filename), encoding="utf-8")

print("Done with annotating sentence type.")