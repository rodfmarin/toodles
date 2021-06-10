import os
import json

import requests

NOTION_SECRET = os.getenv("NOTION_SECRET")


class NotionTextObject:
    """
    Notion Text Object
    """
    def __init__(self, content, link=None):

        if link is not None:
            self.text = [{
                "type": "text",
                "text": {
                    "content": content,
                    "link": {"url": link}
                }
            }]

        self.text = [{
            "type": "text",
            "text": {
                "content": content
            }
        }]


class NotionBlock:
    """
    Base Notion Block Class
    """
    def __init__(self, id=None, type=None, created_time=None, last_edited_time=None, has_children=False, object='block'):
        self.object = object
        if id is not None:
            self.id = id
        self.type = type
        if created_time is not None:
            self.created_time = created_time
        if last_edited_time is not None:
            self.last_edited_time = last_edited_time
        if has_children is True:
            self.has_children = has_children


class NotionParagraphBlock(NotionBlock):
    """
    Notion Paragraph Block, derived from Notion Block
    """
    def __init__(self, text, children=None):
        self.paragraph = NotionTextObject(text)
        self.type = "paragraph"
        if children is not None:
            self.children = children

        NotionBlock.__init__(self, type=self.type)


class ToodlesClient:

    def __init__(self, api_key):
        self.api_key = api_key

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }
        self.notion_api_url = "https://api.notion.com"
        self.notion_api_version = "/v1"
        self.search_endpoint = "/search"
        self.pages_endpoint = "/pages"
        self.blocks_endpoint = "/blocks"

        self.search_url = self.notion_api_url + self.notion_api_version + self.search_endpoint
        self.pages_url = self.notion_api_url + self.notion_api_version + self.pages_endpoint
        self.blocks_url = self.notion_api_url + self.notion_api_version + self.blocks_endpoint

    def get(self, url, data=None):
        """
        Do a get on a notion url
        :param url:
        :param d:
        :return:
        """

        r = requests.get(url, headers=self.headers, data=data)
        r.raise_for_status()
        return r.json()

    def post(self, url, data):
        """
        Do a post on a notion url
        :param url:
        :param data:
        :return:
        """
        r = requests.post(url, headers=self.headers, data=data)
        r.raise_for_status()
        return r.json()

    def patch(self, url, data):
        """
        Do a patch on a notion url
        :param url:
        :param data:
        :return:
        """
        r = requests.patch(url, headers=self.headers, data=data)
        r.raise_for_status()
        return r.json()

    def delete(self, url):
        """
        Do a http delete on a nortion url
        TODO: This doesn't work yet on beta
        :param url:
        :return:
        """
        # r = requests.delete(url, headers=self.headers)
        # r.raise_for_status()
        # return r.json()
        pass

    def query(self, query):
        """
        Do a notion query

        curl -X POST 'https://api.notion.com/v1/search' \
          -H 'Authorization: Bearer '"$NOTION_API_KEY"''
          -H 'Content-Type: application/json' \
          -H "Notion-Version: 2021-05-13" \
            --data '{
            "query":"External tasks",
            "sort":{
              "direction":"ascending",
              "timestamp":"last_edited_time"
            }
          }'
        """

        data = {
            "query": query,
            "sort": {
                "direction": "ascending",
                "timestamp": "last_edited_time"
            }
        }

        data = json.dumps(data, indent=4)
        r = self.post(url=self.search_url, data=data)

        return r

    def get_toodles_page(self):
        """
        Look for the Toodles page, return its id
        For now this makes a lot of assumptions
        TODO: Make this better
        :return:
        """

        q = self.query("Toodles-Note")

        try:
            if q.get('results'):
                return q["results"][0]["id"]
        except KeyError:
            print("no results")

    def get_page(self, page_id):
        """
        Retrieve a Notion Page
        :param page_id:
        :return:
        """

        url = self.pages_url + f"/{page_id}"

        return self.get(url)

    def get_blocks(self, block_id):
        """
        Retrieve a Notion Page
        :param block_id:
        :return:
        """

        url = self.blocks_url + f"/{block_id}/children"

        return self.get(url)

    def delete_block(self, block_id):
        """
        TODO: This doesn't work yet on beta
        Delete a block
        :param block_id:
        :return:
        """
        #
        # url = self.blocks_url + f"/{block_id}/children"
        #
        # return self.delete(url)
        pass

    def new_todo(self, todo_text):
        """
        We need to append a new paragraph block to our toodles page via
        PATCH https://api.notion.com/v1/blocks/{toodles_page_id}/children
        Create a new paragraph block, append to the toodles page
        :param toodles_page_id:
        :param todo_text:
        :return:
        """


        """
        curl -X PATCH 'https://api.notion.com/v1/blocks/9bd15f8d-8082-429b-82db-e6c4ea88413b/children' \
          -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
          -H "Content-Type: application/json" \
          -H "Notion-Version: 2021-05-13" \
          --data '{
            "children": [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "text": [{ "type": "text", "text": { "content": "Lacinato kale" } }]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Lacinato kale is a variety of kale with a long tradition in Italian...
                                    "link": { "url": "https://en.wikipedia.org/wiki/Lacinato_kale" }
                                }
                            }
                        ]
                    }
                }
            ]
        }'
        """


        toodles_page_id = self.get_toodles_page()
        url = self.blocks_url + f"/{toodles_page_id}/children"

        children = {
            "children": []
        }

        paragraph_block = NotionParagraphBlock(todo_text)
        children['children'].append(paragraph_block)
        children = json.dumps(children, default=lambda x: x.__dict__)
        self.patch(url, data=children)

        return

    def get_todos(self):
        """
        Return all children of the Toodles-Notes
        Which should all be paragraphs of _todo_ items
        TODO: we need to detect paging,cursor and get all items
        :return:
        """

        # Our main toodles page:
        tp = self.get_toodles_page()
        blocks = self.get_blocks(tp)

        todos = []

        for block in blocks['results']:
            todos.append(block["paragraph"]["text"][0]["text"]["content"])

        for item in todos:
            print(f"{item} \r")


def main():
    tc = ToodlesClient(NOTION_SECRET)
    #print(tc.get_toodles_page())
    #print(json.dumps(tc.get_blocks(tc.get_toodles_page()), indent=4))

    tc.get_todos()

if __name__ == "__main__":
    main()
