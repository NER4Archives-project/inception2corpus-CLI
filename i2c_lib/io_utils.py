# -*- coding: utf-8 -*-

"""

"""
import glob
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

def output_creation():
    # Try to remove the old dir tree output_annotated_corpus/
    subprocess.call(f'rm -r {OUTPUT_CORPUS}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    # Create the new dir tree output_annotated_corpus/
    os.mkdir(OUTPUT_CORPUS)
    os.mkdir(DATA_SPLIT_N2)
    os.mkdir(DATA_SPLIT_N3)
    os.mkdir(DATA_SPLIT_N2_IDX)
    os.mkdir(DATA_SPLIT_N3_IDX)


def clear_temp_cache(path: str):
    for f in glob.glob(path):
        os.remove(f)