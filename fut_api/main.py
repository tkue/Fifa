import requests
import json

_URL = 'https://www.easports.com/fifa/ultimate-team/api/fut/item?page=1'
_BASE_URL = 'https://www.easports.com/fifa/ultimate-team/api/fut'

def get_url_by_page(page_number: int):
    return '{0}/item?page={1}'.format(_BASE_URL, str(page_number))

def get_request_by_page(page_number: int):
    return requests.get(get_url_by_page(page_number))

def get_total_pages():
    r = get_request_by_page(1)
    j = json.loads(r.text)
    return j['totalPages']

def get_all_items():
    total_pages = get_total_pages()

    all_items = []

    for i in range(total_pages):
        i += 1
        print('Page: {0} / {1}'.format(str(i), str(total_pages)))

        r = get_request_by_page(i)
        j = json.loads(r.text)

        items = j['items']

        for item in items:
            all_items.append(item)

    return all_items

def write_items_to_json(all_items: [], filename: str):
    with open(filename, 'w+') as f:
        f.write('[\n')
        for i, item in enumerate(all_items):
            item_to_write = str(item).replace('\'', '"')\
                                    .replace('None', '""')\
                                    .replace('False', '"False"')\
                                    .replace('True', '"True"')
            if i == 0:
                f.write(item_to_write)
                f.write('\n')
            else:
                f.write('{0}{1}'.format(',', item_to_write))
                f.write('\n')
        f.write(']')


if __name__ == '__main__':
    total_pages = get_total_pages()
    all_items = get_all_items()

    filename = 'fut.json'
    write_items_to_json(all_items, filename)
