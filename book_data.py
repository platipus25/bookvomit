import csv
import http.client
import urllib
import json
import time
import logging

logger = logging.getLogger(__name__)

# https://www.gutenberg.org/ebooks/offline_catalogs.html#the-gutindex-listings-of-ebooks

# https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv

def gutenberg_download_book(text_number):
    url = f"https://www.gutenberg.org/files/{text_number}/{text_number}-0.txt"
    host = "www.gutenberg.org"
    conn = http.client.HTTPSConnection(host)
    conn.request("GET", f"/files/{text_number}/{text_number}-0.txt", headers={"Host": host})
    response = conn.getresponse()
    body = response.read()
    #print(body)
    return str(body)

def check_gutenberg_numbers(numbers):
    with open('pg_catalog.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile)

        for row in spamreader:
            if row["Text#"] in numbers:
                return row["Text#"]

def find_loc_item(title):
    host = "www.loc.gov"
    conn = http.client.HTTPSConnection(host)
    query = urllib.parse.quote_plus(f"{title}")
    conn.request("GET", f"/books/?fo=json&q={query}&c=4", headers={"Host": host})
    response = conn.getresponse()
    body = response.read()
    body = json.loads(body)
    logger.info(body)

def openlibrary_find_book(query):
    endpoint = "https://openlibrary.org/search.json"

    # https://openlibrary.org/search.json?q=the+great+gatsby&fields=title,author,id_project_gutenberg,key,type
    # https://openlibrary.org/works/OL468431W/editions.json
    # https://openlibrary.org/books/OL9219606M.json

    host = "openlibrary.org"
    query = urllib.parse.quote_plus(f"{query}")
    conn = http.client.HTTPSConnection(host)

    conn.request("GET", f"/search.json?q={query}&fields=title,author,id_project_gutenberg,key,type", headers={"Host": host})
    response = conn.getresponse()
    body = response.read()
    body = json.loads(body)

    found = body["docs"]

    gutenberg_works = {}

    for work in found:
        if "id_project_gutenberg" in work:
            logger.info(work)
            logger.info(work["id_project_gutenberg"])
            gutenberg_works[work["key"]] = work["id_project_gutenberg"]

    logger.info(len(found))
    
    #filtered = list(filter(lambda work: "id_project_gutenberg" in work, found))
    #print(len(filtered))

    editions_keys = list()

    for work in found[:2]:
        key = work["key"]

        num_read = 0
        max_read = 1000

        while num_read < max_read:
            conn.request("GET", f"{key}/editions.json?offset={num_read}", headers={"Host": host})
            body = json.loads(conn.getresponse().read())
            editions = body["entries"]

            max_read = min(max_read, body['size'])

            for edition in editions:
                logger.info(edition['title'])

                editions_keys.append(edition['key'])

            num_read += len(editions)
            #time.sleep(0.100)


    logger.info(f"len(editions): {len(editions_keys)}")
    logger.info("/books/OL9219606M" in editions_keys)

    #editions_keys = {"/books/OL9219606M"}

    good_editions = []
 
    for key in editions_keys:
        conn.request("GET", f"{key}.json", headers={"Host": host})
        body = json.loads(conn.getresponse().read())

        logger.info(body["title"])
        
        if "number_of_pages" in body:
            logger.info(body["number_of_pages"])
        if "physical_format" in body:
            logger.info(body["physical_format"])
        if "pagination" in body:
            logger.info(body["pagination"])
        if "physical_dimensions" in body:
            logger.info(body["physical_dimensions"])
        
        if "physical_dimensions" in body and "number_of_pages" in body:
            logger.info(body)
            good_editions.append(body)
            break
     
        #time.sleep(0.100)
       
    for i, edition in enumerate(good_editions):
        for work in edition['works']:
            good_editions[i]['key'] = work['key']
            if work['key'] in gutenberg_works:
                good_editions[i]["id_project_gutenberg"] = gutenberg_works[work['key']]
                break

    logger.info(good_editions)
    return good_editions

"""
with open('pg_catalog.csv', newline='') as csvfile:
    spamreader = csv.DictReader(csvfile)

    for row in spamreader:
        if "The Great Gatsby" in row["Title"]:
            print(row)
            #download_book(row["Text#"])
            #find_loc_item(row["Title"])
"""

def get_book(query):

    books = openlibrary_find_book(query)

    if not books:
        logger.info("Could not find the book")
        return None

    book = books[0]
    book = {
        "key": book["key"],
        "title": book["title"],
        "physical_format": book["physical_format"],
        "number_of_pages": book["number_of_pages"],
        "first_sentence": book["first_sentence"]["value"] if "first_sentence" in book else None,
        "physical_dimensions": book["physical_dimensions"],
        "weight": book.get("weight"),
        "id_project_gutenberg": book.get("id_project_gutenberg"),
        "contents": None,
    }

    logger.info(f"{book}")

    if book['id_project_gutenberg']:
        number = check_gutenberg_numbers(book['id_project_gutenberg'])
        book['id_project_gutenberg'] = number
        contents = gutenberg_download_book(number)
        book["contents"] = contents
        
        logger.info(contents[:10])
        if book["first_sentence"]:
            logger.info(contents.find(book['first_sentence']))

    return book
