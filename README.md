# inception2corpus-CLI


![Python Version](https://img.shields.io/badge/Python-%3E%3D%203.7-%2313aab7) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A CLI for retrieving a corpus annotated with named entities from INCEpTION instance to an archived and reusable corpus in context of any NER project.

*This tool was created in the context of the NER4Archives project (INRIA/Archives nationales); it is adaptable and reusable for any other project under the terms of the [MIT license](./LICENSE)*.

The CLI launches a linear process, called a "pipeline", which executes the components in the following order:

- Fetch curated documents from INCEpTION instance (XMI);
- Re-tokenize curated documents;
- Convert XMI to CONLL files;
- Merge CONLL files in one;
- Provides a report containing statistics and metadata about the corpus;
- Reduce (get only sentences annotated and reject other) and serialize dataset in 2 (train/test) and 3 sets (train/test/eval) according to a ratio defined by the user

At the end of the execution of the program, an `output_annotated_corpus folder/` is provided in the root tool's folder, for more details see this [section](#Output-folder-description).

## 🛠️ Installation

1. In `./inception2corpus-CLI/` location, open a terminal

2. Check if Python 3.7 or higher is installed

```bash
python --version
```

if not, install it [here](https://www.python.org/downloads/)

3. Create a code environment with virtualenv and correct Python version

```bash
virtualenv --python=/usr/bin/python3.7 venv
```

4. Activate this code environment

```bash
source venv/bin/activate
```

5. Finally, install the required packages

```bash
pip install -r requirements.txt
```

## ⚠️  Configuration before launch the tool

- Do not delete the `temp_files/` folder, leave it
- Do not delete the `i2c_lib/` folder, leave it
- Go to the [USER_VAR_ENV.yml](./USER_VAR_ENV.yml) file and fill it with the correct information.

## ▶️ Usage

In terminal, run : 

```bash
python inception2corpus.py
```

## 📁 Output folder description

```
./output_annotated_corpus folder/
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

```
