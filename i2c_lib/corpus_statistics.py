# -*- coding: utf-8 -*-

"""

"""

from collections import Counter
from datetime import datetime
import json

from nltk.tree import Tree
from nltk.chunk import conlltags2tree

from i2c_lib.constants import *

class CorpusStatistics:
    def __init__(self, corpus_metadata):
        self.name_corpus = corpus_metadata['corpus_metadata'][0]['name_corpus']
        self.version = corpus_metadata['corpus_metadata'][1]['version']
        self.kappa_iaa = corpus_metadata['corpus_metadata'][2]['kappa_iaa']
        self.from_corpus = corpus_metadata['corpus_metadata'][3]['from_corpus']

        with open(f"{OUTPUT_CORPUS}/all.conll", mode="r", encoding="utf-8") as f:
            self.conll = f.read()

        self.out_json = self.compute_stats()
        self.write_json()

    def compute_stats(self) -> dict:
        sentences = 1
        sentences_annotated = 1
        tokens = []
        tags = []
        tokens_tagged = []
        # Liste intermediare pour tester si la phrases contient des mentions annotées.
        inter_sentences_annotated = []

        for row in self.conll.splitlines():
            # si méthode n°1 : sep = "\t"
            # si méthode n°2 : sep = " "
            pair = row.split(" ")
            # Si utilisation de la méthode n°2 :
            # Si la longueur de la liste est égale à 1, cela signifie
            # que l'on passe à une nouvelle phrase.
            if len(pair) == 1:
                # Si utilisation de la méthode n°1 :
                # if pair[0] == "" and pair[1] == "":
                sentences += 1
                if len(inter_sentences_annotated) > 0:
                    sentences_annotated += 1
                    inter_sentences_annotated = []
                else:
                    inter_sentences_annotated = []
            else:
                mention = pair[0]
                ner_tag = pair[1]
                tokens.append(mention)
                tags.append(ner_tag)
                if ner_tag != "O":
                    inter_sentences_annotated.append(ner_tag)
                    mention_tagged = mention
                    tokens_tagged.append(mention_tagged)

        conlltags = [(token, "_", tg) for token, tg in zip(tokens, tags)]
        ne_tree = conlltags2tree(conlltags)
        original_text = []
        for subtree in ne_tree:
            # On passe les tags "O"
            if type(subtree) == Tree:
                original_label = subtree.label()
                original_string = " ".join([token for token, _ in subtree.leaves()])
                original_text.append((original_string, original_label))

        iob = dict(Counter(tags))
        merge_iob = dict(Counter([t[1] for t in original_text]))
        del iob['O']

        return {
                    "name corpus": self.name_corpus,
                    "version": self.version,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "from_corpus": self.from_corpus,
                    "kappa": self.kappa_iaa,
                    "statistics": {
                                  "Total sentences": sentences,
                                  "Total sentences annotated": sentences_annotated,
                                  "Total tokens annotated (IOB)": sum(iob.values()),
                                  "Total tokens annotated (merge IOB)": sum(merge_iob.values()),
                                  "Total tokens annotated details (IOB)": iob,
                                  "Total tokens annotated details (merge IOB)": merge_iob
    }
}

    def write_json(self):
        with open(f'{OUTPUT_CORPUS}/meta_corpus.json', mode="w") as f:
            json.dump(self.out_json, f)

