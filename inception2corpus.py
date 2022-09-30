#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

import click
import requests.exceptions

from i2c_lib.prompt_utils import (_report_log,
                                  generate_dialog,
                                  generate_yes_no_dialog,
                                  generate_figlet)
from i2c_lib.preprocessing import batch_retokenization
from i2c_lib.inception_connection import InceptionInteract
from i2c_lib.corpus_statistics import CorpusStatistics
from i2c_lib.serialization import Serialization
from i2c_lib.io_utils import (YamlChecker,
                              output_creation,
                              clear_temp_cache)
from i2c_lib.constants import *

import x2c


@click.command()
@click.argument('yaml_env_file',
                nargs=1)
@x2c.timing
def main(yaml_env_file: str) -> None:
    """INCEPTION2CORPUS PIPELINE CLI - 2022

    YAML_ENV_FILE (str): path to YAML file contains environnement variable
    """
    result = generate_yes_no_dialog(title=TITLE, text=INTRODUCTION)

    if result:
        yaml_object = YamlChecker(path=yaml_env_file)
        yml_env = yaml_object.yml_env
        # Check YAML conformity
        if yml_env is None:
            generate_dialog(msg="❌ It seems the YAML file is not compliant. "
                                "Check it and restart.\n\nPress ENTER to quit.",
                            type="E")
            sys.exit()
        # Check YAML values
        if len(yaml_object.bad_properties) > 0:
            to_control = ""
            for bp in yaml_object.bad_properties:
                to_control += f"- {bp[0]} - {bp[1]}" + "\n"
            generate_dialog(
                msg=f"❌ It seems the YAML file contains errors for the following "
                    f"values:\n\n{to_control}\nCheck it and restart.\n\nPress ENTER to quit.",
                type="E")
            sys.exit()
        else:
            generate_dialog(
                msg="✅ YAML FILE check is valid, "
                    "the pipeline can start.\n\nPress ENTER to continue.",
                type="V")

        # Try to connect to INCEPTION instance
        try:
            client_inception = InceptionInteract(inception_host=yml_env['inception_user'][0]['inception_host'],
                                                 project_name=yml_env['inception_user'][1]['project_name'],
                                                 inception_username=yml_env['inception_user'][2]['username'],
                                                 inception_password=yml_env['inception_user'][3]['password'])
        except requests.exceptions.JSONDecodeError:
            client_inception = None

        if client_inception is None:
            generate_dialog(
                msg=f"❌ It seems that the information provided for the connection to INCEpTION is invalid. "
                    f"Check inception_user parameter in YAML file and restart.\n\nPress ENTER to quit.",
                type="E")
            sys.exit()

        # The pipeline begin here

        # Output_annotated_corpus/ creation
        _report_log(message=f"Creating the new folder: {OUTPUT_CORPUS} ...", type_log="V")
        output_creation()
        clear_temp_cache(f'{XMI_CURATED_RETOKENIZED}/*.xmi')
        clear_temp_cache(f'{CONLL_CURATED_RETOKENIZED}/*.conll')
        _report_log(message=f"{OUTPUT_CORPUS} is created.", type_log="S")

        # 1) Fetch all curated XMI curated
        _report_log(message="Fetch XMI curated from INCEpTION in progress...", type_log="V")
        client_inception.extract_xmi_curated()
        _report_log(message=f"XMI curated files are saved in {XMI_CURATED_PATH}", type_log="S")

        # 2) Re-tokenized XMI Curated
        _report_log(message="XMI Re-tokenization in progress... (Please wait, this is a long process)", type_log="V")
        batch_retokenization(dir_in=XMI_CURATED_PATH, dir_out=XMI_CURATED_RETOKENIZED,
                             f_schema=XMI_CURATED_PATH + '/TypeSystem.xml')
        _report_log(message="XMI curated files are re-tokenized, "
                            "you can check the log here : ./retokenized_log.log",
                    type_log="S")

        # 3) Convert XMIs to CONLL
        _report_log(message="Convert XMI to CONLL format in progress...", type_log="V")
        x2c.Xmi2Conll(
            xmi=XMI_CURATED_RETOKENIZED,
            typesystem_input=f'{XMI_CURATED_PATH}/TypeSystem.xml',
            output=CONLL_CURATED_RETOKENIZED,
            type_name_annotations=yml_env['conll_structure'][0]['feature_structure'],
            sep=yml_env['conll_structure'][1]['type_separator']
        )
        _report_log(message="All XMI are converted in CONLL format",
                    type_log="S")

        # 4) Merge all conll in one all.conll (with batch recipe)
        _report_log(message="Merge CONLL files in progress...", type_log="V")
        subprocess.call(f'cat {CONLL_CURATED_RETOKENIZED}/*.conll > {OUTPUT_CORPUS}/all.conll', shell=True)
        _report_log(message=f"CONLL are merge in one, check: {OUTPUT_CORPUS}/all.conll",
                    type_log="S")

        # 5) Compute statistics on corpus
        _report_log(message=f"Compute corpus statistics from {OUTPUT_CORPUS}/all.conll",
                    type_log="V")
        CorpusStatistics(corpus_metadata=yml_env)
        _report_log(message=f"Corpus statistics are generated, check: {OUTPUT_CORPUS}/meta_corpus.json",
                    type_log="S")

        # 6) Reduce and split n2, n3 reduced df with ratio and save 10 files in correct dir
        _report_log(message="Corpus reduction, shuffled and serialization (split in 2 and 3 sets) in progress...", type_log="V")
        # indicate the output report stratification
        s = Serialization(metadata=yml_env)
        _report_log(message=s.report)
        _report_log(message=f"Corpus is reduced, shuffled and splitted, "
                            f"please check folders: "
                            f"{DATA_SPLIT_N2} | "
                            f"{DATA_SPLIT_N2_IDX} | "
                            f"{DATA_SPLIT_N3} | "
                            f"{DATA_SPLIT_N3_IDX}",
                    type_log="S")

        # create an archive .zip for output
        _report_log(message=f"Create archive of {OUTPUT_CORPUS}...", type_log="I")
        subprocess.call(f'zip -r {OUTPUT_CORPUS}/output_annotated_corpus {OUTPUT_CORPUS}/* -x {OUTPUT_CORPUS}/meta_corpus.json', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        # remove old files from output_annotated_corpus/
        subprocess.call(
            f"find {OUTPUT_CORPUS}/* -not \( -name '*zip' -or -name '*json' \) -delete",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        # clear temp files
        _report_log(message="Clear temporary files in progress...", type_log="I")
        clear_temp_cache(f'{XMI_CURATED_RETOKENIZED}/*.xmi')
        clear_temp_cache(f'{CONLL_CURATED_RETOKENIZED}/*.conll')

        _report_log(message=f"FINISHED: corpus is available here: {OUTPUT_CORPUS}/{OUTPUT_CORPUS}.zip", type_log="I")


if __name__ == '__main__':
    main()
