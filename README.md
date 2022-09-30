<img src="./documentation/logo-i2c.png" width=150 align=right>

# inception2corpus-CLI
A CLI for retrieving a corpus annotated with named entities from INCEpTION instance to an archived and reusable corpus in context of any NER project.

*This tool was created in the context of the NER4Archives project (INRIA/Archives nationales); it is adaptable and reusable for any other project under the terms of the [MIT license](./LICENSE)*.


![Python Version](https://img.shields.io/badge/Python-%3E%3D%203.7-%2313aab7) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://badge.fury.io/py/inception2corpus.svg)](https://badge.fury.io/py/inception2corpus)


The CLI launches a linear process, called a "pipeline", which executes the components in the following order:

- Fetch curated documents (XMI format) from an INCEpTION instance (check state of document in Inception > "Monitoring" window);

![curated-doc](./documentation/curated_doc_inception.png)

- preprocessing curated documents (retokenize, remove unprintable characters etc.);
- Convert XMI to CONLL files (inception2corpus use [xmi2conll cli](https://github.com/Lucaterre/xmi2conll) as a module);
- Merge CONLL files in one;
- Provides a report containing statistics and metadata about the corpus;
- Reduce (get only sentences annotated and reject other) and serialize dataset in 2 (train/dev) and 3 sets (train/dev/test) according to a ratio defined by the user

At the end of the execution of the program, an `output_annotated_corpus folder/` is provided at the root working directory, for more details see this [section](#Output-folder-description).

## 🛠️ Installation (easy way)

1. You need Python 3.7 or higher is installed (if not, install it [here](https://www.python.org/downloads/)).

2. First, create a new directory and set a code environment with virtualenv and correct Python version, follow these steps (depending on OS):

    ### MacOSx / Linux

    ```bash
    virtualenv --python=/usr/bin/python3.7 venv
    ```

    then, activate this new code environment with:

    ```bash
    source venv/bin/activate
    ```

    ### Windows

    ```bash
    py -m venv venv
    ```

    then, activate this new code environment with:

    ```bash
    .\venv\Scripts\activate
    ```

3. Finally, install `inception2corpus` CLI via pip with:

    ```bash
    pip install inception2corpus
    ```

## 🛠️ Installation (for developers only)

```bash
# 1. clone git repository
git clone https://github.com/NER4Archives-project/inception2corpus-CLI.git
# 2. Go to repository and create a new virtual env (follow steps in easy way installation)
# 3. install packages
# (on MACOSx/LINUX): 
pip install -r requirements.txt
# (on Windows): 
pip install -r .\requirements.txt
```

## ▶️ Usage

1. `inception2corpus` CLI use a YAML file as argument to specify INCEpTION HOST information,
corpus metadata, conll format, serialization options etc.
You can use and update the template here [USER_VAR_ENV.yml](./USER_VAR_ENV.yml).

2. When configuration YAML file is completed use this command:
   ```bash
   inception2corpus ./USER_VAR_ENV.yml
   ```
3. At the end of this process, a new output directory is created at the root of working
directory (`./output_annotated_corpus folder/`) that contains your final corpus, ready to train.
Also, a new `temp_files/` folder is created at the root, leave it or delete it as you want.


## 📁 Full output folder description

```
./output_annotated_corpus folder/
 |
 |- output_annotated_corpus folder.zip/
 |           |
 |           |- data_split_n2/ : The all_reduced.conll divided into 2 sets (train, dev)
 |           |
 |           |- data_split_n3/ : The all_reduced.conll divided into 3 sets (train, dev, test)
 |           |
 |           |- data_split_n3_idx/ : The all_reduced.conll divided into 3 sets (train, dev, test) with sentences ID
 |           |
 |           |- data_split_n2_idx/ : The all_reduced.conll divided into 2 sets (train, dev) with sentences ID
 |           |
 |           |- XMI_curated/ : Original XMI to import into INCEpTION
 |           |
 |           |- all.conll : All documents in CONLL format
 |           |- all_reduced.conll : All documents in CONLL format reduced to only annotated sentences
 |
 |- meta_corpus.json : corpus metadata and statistics

```
