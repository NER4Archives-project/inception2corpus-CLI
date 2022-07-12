# -*- coding: utf-8 -*-

"""

"""

import random

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from i2c_lib.constants import *

class Serialization:
    def __init__(self, metadata):
        with open(f"{OUTPUT_CORPUS}/all.conll", mode="r", encoding="utf-8") as f:
            self.conll = f.read()

        self.ratio_n2 = metadata['corpus_stratification'][0]['train_dev_ratio']
        self.ratio_n3 = metadata['corpus_stratification'][1]['train_dev_test_ratio']

        self.conll_to_df = self.conll_to_dataframe()
        self.df_reduced = self.dataframe_reduction()

        # save df_reduced with whitespaces between sentences and no sentence ID
        self.drop_sentence_id_column(
            self.add_whitespaces_between_sentences(
                self.df_reduced)
        ).to_csv(f"{OUTPUT_CORPUS}/all_reduced.conll", sep="\t", index=False, header=False)

        self.df_reduced_shuffled = self.dataframe_shuffle()

        # n2 and n3 without sentence idx
        self.n2_train, self.n2_dev = self.split_train_test()
        self.n3_train, self.n3_dev, self.n3_test = self.split_train_test_validation()

        def split_to_dir(data, name, path_noidx, path_idx):
            data.to_csv(f"{path_idx}/{name}.conll", sep="\t", index=False, header=False)
            self.drop_sentence_id_column(data).to_csv(f"{path_noidx}/{name}.conll", sep="\t", index=False, header=False)


        for dataset in [(self.n2_train, 'train', DATA_SPLIT_N2, DATA_SPLIT_N2_IDX),
                        (self.n2_dev, 'dev', DATA_SPLIT_N2, DATA_SPLIT_N2_IDX),
                        (self.n3_train, 'train', DATA_SPLIT_N3, DATA_SPLIT_N3_IDX),
                        (self.n3_dev, 'dev', DATA_SPLIT_N3, DATA_SPLIT_N3_IDX),
                        (self.n3_test, 'test', DATA_SPLIT_N3, DATA_SPLIT_N3_IDX),
                        ]:
            split_to_dir(dataset[0], dataset[1], dataset[2], dataset[3])

        #for dataset in [self.n3_train, self.n3_test, self.n3_val]:
        #    pass


        self.total_original = len(self.df_reduced_shuffled)

        n2_train_stats = (len(self.n2_train) / self.total_original)
        n2_test_stats = (len(self.n2_dev) / self.total_original)
        n3_train_stats = (len(self.n3_train) / self.total_original)
        n3_test_stats = (len(self.n3_dev) / self.total_original)
        n3_validation_stats = (len(self.n3_test) / self.total_original)
        self.report = f"""
                    === Statistics sample stratification ===

                    N2 sample
                    ---------

                    * Train part : {round(n2_train_stats, 3)} % | Total : {len(self.n2_train)} data
                    * Dev part : {round(n2_test_stats, 3)} % | Total : {len(self.n2_dev)} data

                    N3 sample
                    ---------

                    * Train part : {round(n3_train_stats, 3)} % | Total : {len(self.n3_train)} data
                    * Dev part : {round(n3_test_stats, 3)} % | Total : {len(self.n3_dev)} data
                    * Test part : {round(n3_validation_stats, 3)} % | Total : {len(self.n3_test)} data

            """




        # safe versions in output folder ...

    @staticmethod
    def keep_sentences_id(df):
        d = dict(zip(df['Sentence'].unique(), np.arange(1, len(df['Sentence_ID'].unique()) + 1)))
        df['Sentence_ID'] = df['Sentence_ID'].map(d)
        return df

    @staticmethod
    def add_whitespaces_between_sentences(df):
        mask = df['Sentence_ID'].ne(df['Sentence_ID'].shift(-1))
        df_inter = pd.DataFrame('', index=mask.index[mask] + .5, columns=df.columns)
        df = pd.concat([df, df_inter]).sort_index().reset_index(drop=True).iloc[:-1]
        return df

    @staticmethod
    def drop_sentence_id_column(df):
        return df.drop(columns=['Sentence_ID'])

    def conll_to_dataframe(self):
        to_dataframe = []

        counter = 1
        for row in self.conll.splitlines():
            pair = row.split(" ")
            if len(pair) == 1:
                # if pair == [""] is breakline
                association = ('break', 'break', 'break')
                counter += 1
                to_dataframe.append(association)
            else:
                mention = pair[0].strip()
                label = pair[1].strip()
                if mention != "":
                    association = (counter, pair[0].strip(), pair[1].strip())
                    to_dataframe.append(association)
        df_conll = pd.DataFrame(to_dataframe, columns =['Sentence_ID', 'Mention', 'Tag'])
        df_conll = df_conll.astype(str)
        return df_conll

    def dataframe_reduction(self):
        empty_sentences = self.conll_to_df.loc[
            ((self.conll_to_df.Tag.str.startswith('B-') | self.conll_to_df.Tag.str.startswith('I-')) & self.conll_to_df.Tag.str.contains('O')), 'Sentence_ID']
        df_reduced = self.conll_to_df.loc[self.conll_to_df['Sentence_ID'].isin(empty_sentences)]

        #df = df[~df.Sentence.str.contains("break")]
        return df_reduced

    def dataframe_shuffle(self):
        groups = [group for _, group in self.df_reduced.groupby("Sentence_ID")]
        random.shuffle(groups)
        df_shuffle = pd.concat(groups).reset_index(drop=True)
        return df_shuffle

    def split_train_test(self):
        # shuffle sur False car df déjà mélangé
        train, test = train_test_split(self.df_reduced_shuffled, test_size=self.ratio_n2[1], random_state=42, shuffle=False)
        return train, test

    def split_train_test_validation(self):
        train, test, validate = np.split(self.df_reduced_shuffled,
                                         [int(self.ratio_n3[0] * len(self.df_reduced_shuffled)), int(.8 * len(self.df_reduced_shuffled))])

        return train, test, validate

