# -*- coding: utf-8 -*-

"""

"""
import io
import zipfile

from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.patch_stdout import patch_stdout

from pycaprio import Pycaprio
from pycaprio.mappings import InceptionFormat, DocumentState

from i2c_lib.constants import XMI_CURATED_PATH
from i2c_lib.prompt_utils import (kb,
                                  bottom_toolbar,
                                  cancel,
                                  convert_to_html)


class InceptionInteract:
    def __init__(self, inception_host, project_name, inception_username, inception_password):
        self.host = inception_host
        self.project_name = project_name.lower()
        self.username = inception_username
        self.password = inception_password
        self.client = Pycaprio(self.host, authentication=(str(self.username), str(self.password)))
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