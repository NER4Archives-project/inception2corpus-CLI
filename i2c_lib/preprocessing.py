# -*- coding: utf-8 -*-

"""

"""

import os
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

import logging
import re
from unicodedata import category

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import ProgressBar

from cassis import load_cas_from_xmi, load_typesystem, typesystem, cas

from i2c_lib.prompt_utils import kb, bottom_toolbar, convert_to_html

logging.basicConfig(filename="../retokenized_log.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", filemode="w")



class Retokenizer:
    def __init__(self, xmi_path: str, xmi: cas.Cas, xml: typesystem.TypeSystem) -> None:
        """ Change token annotations
        :param str xmi: path to existing xmi annotation file. open.
        :param str xml: path to xml schema file. open typesytem
        :return: None
        :rtype: None
        """

        self.xmi = xmi_path
        self.typesystem = xml
        self.cas = xmi
        self.tokenType = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"

    def retokenize(self,
                   split_apostrophes: bool = True,
                   remove_unprintable_char: bool = True
                   ):
        """Retokenize the document.
        Perform splitting off of apostrophes and hyphens from tokens into new tokens
        and remove tokens with unprintable characters.
        """

        cas = self.cas
        tokenType = self.tokenType

        # final token to add
        tokens = []
        # remove_token = []

        for idx, tok in enumerate(cas.select(tokenType)):
            tok_text = tok.get_covered_text()
            # first remove unprintable characters
            if remove_unprintable_char:
                self.remove_unprintable_tokens(cas, tok_text, tokenType, idx)
            # second split off apostrophes
            if split_apostrophes:
                new_tok = self.split_off_apostrophes(tok_text, tok)
                if new_tok is not None:
                    tokens += self.split_off_apostrophes(tok_text, tok)

        # add new retok tokens
        if len(tokens) > 0:
            cas.add_all(tokens)

        # clean all text
        if remove_unprintable_char:
            text = cas.sofa_string
            text_clean = "".join(ch if category(ch)[0] != "C" else "_" for ch in text)
            cas.sofa_string = text_clean

        assert len(text) == len(text_clean)


    def split_off_apostrophes(self, tok_text: str, tok):
        """
        Split off apostrophes when glued together with token
        Example:
        2020-02-17 10:20:28,567 - root - INFO - Token 'Finanz-Budger's' was tokenized into ['Finanz-Budger', "'", 's']
        """
        if "'" in tok_text and len(tok_text) > 1:
            # Add here a constraint for tokens as Val-d'Oise / aujourd'hui
            if not re.search(r"[\-]", str(tok_text)) and not re.search(r"[\w]{2,}['][\w]+", str(tok_text)):
                return self.splitting_at_symbol(tok, "'")


    def remove_unprintable_tokens(self, cas: cas.Cas, tok_text: str, tokenType: str, idx: int):
        """
        Remove annotations of tokens that contain non-printable characters.
        Non-printable characters are Unicode control sequences which may cause
        problems when processing further. Non-printable characters are replaced
        with an underscore in the original text.
        """

        tok_clean = "".join(ch for ch in tok_text if category(ch)[0] != "C")
        if tok_text != tok_clean:
            del cas._current_view.type_index[tokenType][idx]


    def splitting_at_symbol(self, tok, symbol: str):
        """Split a token into its subtokens at a particular symbol (e.g., apostroph).
        A token may yield multiple subtokens.
        :param type tok: Original Token object .
        :param str symbol: Symbol at which token get splitted into subtokens.
        :return: Atomic subtokens equivalent to token when concatenated.
        :rtype: List of Token objects
        """

        Token = self.typesystem.get_type(self.tokenType)

        tokens = []
        tok_text = tok.get_covered_text()
        tok_splits = tok_text.split(symbol)

        # insert splitting symbol at every second position
        i = 1
        while i < len(tok_splits):
            tok_splits.insert(i, symbol)
            i += 2

        # consider the empty string when the splitting symbols
        # occurs at the end of a token (e.g. Alex')
        if not tok_splits[-1]:
            del tok_splits[-1]

        # redefine the boundary of the first token up to the first split
        # adapt for aptostrophe here :
        if "'" in tok_splits:
            tok_splits[0:2] = [''.join(tok_splits[0 : 2])]


        split_pos = len(tok_splits[0])
        tok.end = tok.get('begin') + split_pos

        # add new segments for remaining tokens
        # apostrophes are also tokens
        for split in tok_splits[1:]:
            start = tok.get('begin') + split_pos
            end = tok.get('begin') + split_pos + len(split)
            tokens.append(Token(begin=start, end=end))
            split_pos += len(split)

        try:
            assert tok_text == "".join(tok_splits)
            logging.info(f"Token '{tok_text}' was tokenized into {tok_splits} in document: {os.path.split(self.xmi)[1]}")
        except AssertionError:
            pass
            logging.info(f"Token '{tok_text}' couldn't be properly tokenized into {tok_splits} in document: {os.path.split(self.xmi)[1]}")

        return tokens


def index_inception_files(dir_data: str, suffix: str=".xmi") -> list:
    """Index all .xmi files in the provided directory
    :param type dir_data: Path to top-level dir.
    :param type suffix: Only consider files of this type.
    :return: List of found files.
    :rtype: list
    """

    return sorted([path for path in Path(dir_data).rglob("*" + suffix)])


def open_xmi(xmi, ts):
    with open(xmi, "rb") as f:
        return load_cas_from_xmi(f, typesystem=ts, trusted=True)


def generate_candidates(data: tuple):
    return (open_xmi(data[0], data[2]), data[0], data[1])


def batch_retokenization(dir_in: str, dir_out: str, f_schema: str):
    """Start a batch retokenization of xmi files in the given folder .
    :param str dir_in: Top-level folder containing the .xmi-files.
    :param str dir_out: Top-level output folder for the converted documents.
    :param str f_schema: Path to the .XML-file of the schema.
    :return: None.
    :rtype: None
    """

    with open(f_schema, "rb") as f:
        typesystem_input = load_typesystem(f)

    xmi_in_files = index_inception_files(dir_in)

    xmi_out_files = [Path(str(p).replace(dir_in, dir_out)) for p in xmi_in_files]

    with ThreadPoolExecutor(max_workers=os.cpu_count()+4) as executor:
        results = executor.map(generate_candidates, [(xmi_in,
                                                      xmi_out,
                                                      typesystem_input) for xmi_in, xmi_out in zip(xmi_in_files, xmi_out_files)])

    candidates = [r for r in results]

    title = convert_to_html(
        f'Re-tokenization for <style bg="yellow" fg="black">{len(candidates)} XMI curated files...</style>')

    with patch_stdout():
        with ProgressBar(title=title, key_bindings=kb, bottom_toolbar=bottom_toolbar) as pb:
            for res in pb(candidates):
                res[2].parent.mkdir(parents=True, exist_ok=True)
                base = os.path.basename(res[2])
                f_xmi_out = str(res[2]).replace(base, f"curated_retokenized_{base}")
                retokenizer = Retokenizer(xmi_path=res[1],
                                          xmi=res[0],
                                          xml=typesystem_input)
                retokenizer.retokenize()
                retokenizer.cas.to_xmi(f_xmi_out, pretty_print=True)




