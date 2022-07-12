# -*- coding: utf-8 -*-

"""

"""
import io
import os
import zipfile
import glob


from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.patch_stdout import patch_stdout

from pycaprio import Pycaprio
from pycaprio.mappings import InceptionFormat, DocumentState

from i2c_lib.constants import (XMI_CURATED_PATH,
                               XMI_CURATED_RETOKENIZED,
                               CONLL_CURATED_RETOKENIZED)
from i2c_lib.prompt_utils import (kb,
                                  bottom_toolbar,
                                  cancel,
                                  convert_to_html)


class InceptionInteract:
    def __init__(self, inception_host, project_name, inception_username, inception_password, conll_fmt):
        self.host = inception_host
        self.project_name = project_name.lower()
        self.username = inception_username
        self.password = inception_password
        self.conll_fmt = conll_fmt
        self.client = Pycaprio(self.host, authentication=(self.username, self.password))
        self.project_id = self._find_projectid_by_name()

    def _find_projectid_by_name(self):
        """Finds a project id in INCEpTION by its name.
        """
        matching_projects = [project for project in self.client.api.projects() if
                             project.project_name == self.project_name]
        # assert len(matching_projects) == 1
        return matching_projects[0].project_id

    def fetch_documents(self):
        documents = self.client.api.documents(self.project_id)
        return documents

    def extract_xmi_curated(self):
        curations = []
        documents = self.fetch_documents()
        documents_curated = [doc for doc in  documents if doc.document_state == DocumentState.CURATION_COMPLETE]
        title = convert_to_html(f'Downloading <style bg="yellow" fg="black">{len(documents_curated)} '
                     f'XMI curated files from INCEpTION...</style>')
        print("These documents will be downloaded from INCEpTION: \n")
        for doc in documents_curated:
            print(f'- {doc.document_name}\n')


        # check number of files download and confirm
        with patch_stdout():
            with ProgressBar(title=title, key_bindings=kb, bottom_toolbar=bottom_toolbar) as pb:
                for document in pb(documents_curated):
                    curated_content = self.client.api.curation(self.project_id, document, curation_format=InceptionFormat.XMI)
                    curations.append(curated_content)
                    for curation in curations:
                        z = zipfile.ZipFile(io.BytesIO(curation))
                        z.extractall(XMI_CURATED_PATH)
                    if cancel[0]:
                        break

    def xmi_to_conll(self):
        # list files in xmi_curated_retokenized
        xmis = glob.glob(f"{XMI_CURATED_RETOKENIZED}/*.xmi")
        temp_xmi_id = []
        # create temporary documents in INCEpTION
        for xmi in xmis:
            with open(xmi, mode='rb') as document:
                new_document = self.client.api.create_document(self.project_id,
                                                          os.path.split(xmi)[1],
                                                          document,
                                                          document_format=InceptionFormat.XMI)
            temp_xmi_id.append(new_document.document_id)

        # Retrieve new CONLL from INCEpTION instance
        documents_curated = [doc for doc in self.fetch_documents() if doc.document_state == "NEW"]
        title = convert_to_html(f'Convert <style bg="yellow" fg="black">{len(documents_curated)} XMI curated files to CONLL...</style>')
        with patch_stdout():
            with ProgressBar(title=title, key_bindings=kb, bottom_toolbar=bottom_toolbar) as pb:
                for document in pb(documents_curated):
                    document_content = self.client.api.document(self.project_id, document, document_format=self.conll_fmt)
                    path_conll = f"{CONLL_CURATED_RETOKENIZED}/{document.document_name[:-4]}.conll"
                    with open(path_conll, 'wb') as document_file:
                        document_file.write(document_content)

        # Remove temporary documents
        for xmi_id in temp_xmi_id:
            self.client.api.delete_document(self.project_id, xmi_id)
