# Databricks notebook source
import json

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

from ETL.commons.google_auth import get_token_path, get_gcloud_api_creds, auth, local_creds_file_path
from ETL.commons.unittest_utils import create_tempfile_from_string_data


doc_id = "1xjKBiyJpx-_BLMixYVK6ao30lPnvkgIeUSIuJH-RcmE"

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
DISCOVERY_DOC = "https://docs.googleapis.com/$discovery/rest?version=v1"


def add_current_and_child_tabs(tab, all_tabs):
    all_tabs.append(tab)
    if tab.get('childTabs'):
        for tab in tab.get('childTabs'):
            add_current_and_child_tabs(tab, all_tabs)


def get_all_tabs(doc):
    all_tabs = []
    # Iterate over all tabs and recursively add any child tabs to generate a
    # flat list of Tabs.
    for tab in doc.get('tabs'):
        add_current_and_child_tabs(tab, all_tabs)
    return all_tabs


def read_rich_link_element(element):
    rich_link = element.get('richLink')
    if not rich_link:
        return ''
    rich_link_properties = rich_link.get('richLinkProperties')
    rich_link_title = rich_link_properties.get('title')
    rich_link_uri = rich_link_properties.get('uri')

    return ", ".join([el for el in [rich_link_title, rich_link_uri] if el])


def read_paragraph_element(element):
    text_run = element.get('textRun')
    rich_link = read_rich_link_element(element)

    if not text_run:
        return '' + rich_link

    return text_run.get('content') + rich_link


def read_structural_elements(elements):
    text = []
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += [read_paragraph_element(elem)]
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may
            # be nested.
            table = value.get('table')
            table_data = []
            for row in table.get('tableRows'):
                row_data = []
                cells = row.get('tableCells')
                for cell in cells:
                    cell_data = read_structural_elements(cell.get('content'))
                    row_data.append("|".join(cell_data) if isinstance(cell_data, list) else cell_data)
                table_data.append(row_data)
            text += [table_data]
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += [read_structural_elements(toc.get('content'))]

    return text


def run_meetings_pull(env):
    token_path = get_token_path(gdrive=True)
    store = file.Storage(token_path)
    creds = store.get()
    creds_dict = get_gcloud_api_creds(env)
    creds_file_dir = create_tempfile_from_string_data(json.dumps(creds_dict).encode())
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(creds_file_dir, SCOPES)
        creds = tools.run_flow(flow, store)

    service = discovery.build(
        "docs", "v1", http=creds.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC,
    )
    doc = service.documents().get(documentId=doc_id, includeTabsContent=True).execute()
    all_tabs = get_all_tabs(doc)
    for tab in all_tabs:
        file_name = f"{tab['tabProperties']['title']}_{tab['tabProperties']['tabId']}_{tab['tabProperties']['index']}.json"
        # Get the DocumentTab from the generic Tab.
        document_tab = tab.get('documentTab')
        doc_content = document_tab.get('body').get('content')
        doc_content_filt = read_structural_elements(doc_content)

        json_object = json.dumps(doc_content_filt, indent=4)
        with open(file_name, "w") as outfile:
            outfile.write(json_object)

    # print(json.dumps(doc, indent=4, sort_keys=True))
    # json_object = json.dumps(doc, indent=4)

    # Writing to sample.json
    # with open("meeting_notes_file.json", "w") as outfile:
    #     outfile.write(json_object)


if __name__ == "__main__":
    run_meetings_pull(locals())

# REF: https://developers.google.com/workspace/docs/api/samples/output-json
# REF: https://developers.google.com/workspace/docs/api/samples/extract-text
