# -*- coding: utf-8 -*-

import os

from prompt_toolkit.formatted_text import HTML

# define paths to output corpus with sub-folders
BASE = os.path.dirname("..")

OUTPUT_CORPUS = os.path.join(BASE, 'output_annotated_corpus')
OUTPUT_TEMP_FILES = os.path.join(BASE, 'temp_files')

# persistent path
XMI_CURATED_PATH = os.path.join(OUTPUT_CORPUS, 'XMI_curated')
DATA_SPLIT_N2 = os.path.join(OUTPUT_CORPUS, 'data_split_n2')
DATA_SPLIT_N2_IDX = os.path.join(OUTPUT_CORPUS, 'data_split_n2_idx')
DATA_SPLIT_N3 = os.path.join(OUTPUT_CORPUS, 'data_split_n3')
DATA_SPLIT_N3_IDX = os.path.join(OUTPUT_CORPUS, 'data_split_n3_idx')

# temporary path
XMI_CURATED_RETOKENIZED = os.path.join(OUTPUT_TEMP_FILES, 'xmi_curated_retokenized')
CONLL_CURATED_RETOKENIZED = os.path.join(OUTPUT_TEMP_FILES, 'conll_curated_retokenized')

TITLE = "Inception2Corpus CLI"

INTRODUCTION = HTML(f"""
{TITLE}
<i>©2022 | Author : L. Terriel (INRIA/ALMAnaCH)</i>
<i>This tool was created in context of NER4ARchives project.</i>

This tool allows you to recover curated and annotated documents from an INCEPTION instance and 
to generate a folder with a ready-to-use named-entity recognition corpus.

⚠️ <b>Before starting the pipeline, make sure you have completed USER_VAR_ENV.yml with the correct information.</b>

The pipeline will execute the components in the following order:

1) Fetch only curated XMIs from INCEpTION
2) Re-tokenize XMIs
3) Convert XMIs to CONLLs
4) Merge CONLLs in one (all.conll)
5) Compute corpus statistics (metrics.json)
6) Serialize corpus in (train/dev) and (train/dev/test) according to 
user's split ratio (n2/ and n3/ with sentences id and not)
7) Export all files in unique folder output_annotated_corpus/

Execution can be long: maybe it's time to take a tea or coffee break 🍵 😃

Are you sure to launch the pipeline ?
""")

ENDPROCESS = HTML(f"""

The pipeline is done. Complete corpus is accessible here : ./{OUTPUT_CORPUS}/

|- FOLDER DESCRIPTION -|

./{OUTPUT_CORPUS}/
 |
 |- data_split_n2/ : The all_reduced.conll divided into 2 sets (train, test)
 |
 |- data_split_n3/ : The all_reduced.conll divided into 3 sets (train, test, eval)
 |
 |- data_split_n3_idx/ : The all_reduced.conll divided into 3 sets (train, test, eval) with sentences ID
 |
 |- data_split_n2_idx/ : The all_reduced.conll divided into 2 sets (train, test) with sentences ID
 |
 |- XMI_curated/ : Original XMI to import into INCEpTION
 |
 |- meta_corpus.json : corpus metadata and statistics
 |- all.conll : All documents in CONLL format
 |- all_reduced.conll : All documents in CONLL format reduced to only annotated sentences

Press Ok to quit.
""")

STYLES_GENERAL = {
    'dialog': 'bg:#85c1e9',
    'button': 'bg:#d35400 '
}

STYLES_VALID = {
    'dialog': 'bg:#82e0aa',
    'button': 'bg:#d35400 '
}

STYLES_ERROR = {
    'dialog': 'bg:#e74c3c',
    'button': 'bg:#d35400 '
}
