# -*- coding: utf-8 -*-

"""

"""
import glob
import os
import subprocess

import yaml

from i2c_lib.constants import *


class YamlChecker:
    def __init__(self, path):
        self.yml_path = path
        try:
            with open(self.yml_path, mode="r") as yml_file:
                self.yml_env = yaml.safe_load(yml_file)
        except yaml.parser.ParserError:
            self.yml_env = None
        self.bad_properties = []
        self.check_values_yaml()

    def check_values_yaml(self):
        for k, v in self.yml_env.items():
            for properties in v:
                for property_name, property_value in properties.items():
                    if property_value is None:
                        self.bad_properties.append((k, property_name, property_value))

def create_or_not(path):
    if not os.path.exists(path):
        os.mkdir(path)

def output_creation():
    # Try to remove the old dir tree output_annotated_corpus/
    subprocess.call(f'rm -r {OUTPUT_CORPUS}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    # Create the new dir tree output_annotated_corpus/
    for path in [
        OUTPUT_CORPUS,
        OUTPUT_TEMP_FILES,
        XMI_CURATED_RETOKENIZED,
        CONLL_CURATED_RETOKENIZED,
        DATA_SPLIT_N2,
        DATA_SPLIT_N3,
        DATA_SPLIT_N2_IDX,
        DATA_SPLIT_N3_IDX
    ]:
        create_or_not(path)


def clear_temp_cache(path: str):
    for f in glob.glob(path):
        os.remove(f)