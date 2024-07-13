import csv
import http.client
import urllib
import json
import time

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

def find_loc_item(title):
    host = "www.loc.gov"
    conn = http.client.HTTPSConnection(host)
    query = urllib.parse.quote_plus(f"{title}")
    conn.request("GET", f"/books/?fo=json&q={query}&c=4", headers={"Host": host})
    response = conn.getresponse()
    body = response.read()
    body = json.loads(body)
    print(body)

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

    for work in found:
        if "id_project_gutenberg" in work:
            print(work)
            print(work["id_project_gutenberg"])

    print(len(found))
    
    #filtered = list(filter(lambda work: "id_project_gutenberg" in work, found))
    #print(len(filtered))

    editions_keys = list()

    for work in found[:1]:
        key = work["key"]

        num_read = 0
        max_read = 1000

        while num_read < max_read:
            conn.request("GET", f"{key}/editions.json?offset={num_read}", headers={"Host": host})
            body = json.loads(conn.getresponse().read())
            editions = body["entries"]

            max_read = min(max_read, body['size'])

            for edition in editions:
                print(edition['title'])

                editions_keys.append(edition['key'])

            num_read += len(editions)
            #time.sleep(0.100)


    print("len(editions):", len(editions_keys))
    print("/books/OL9219606M" in editions_keys)

    #editions_keys = {"/books/OL9219606M"}

    good_editions = []
 
    for key in editions_keys:
        conn.request("GET", f"{key}.json", headers={"Host": host})
        body = json.loads(conn.getresponse().read())

        print(body["title"])
        
        if "number_of_pages" in body:
            print(body["number_of_pages"])
        if "physical_format" in body:
            print(body["physical_format"])
        if "pagination" in body:
            print(body["pagination"])
        if "physical_dimensions" in body:
            print(body["physical_dimensions"])
        
        if "physical_dimensions" in body and "number_of_pages" in body:
            print(body)
            good_editions.append(body)
            break
     
        #time.sleep(0.100)
        

    print(good_editions)
    return good_editions


with open('pg_catalog.csv', newline='') as csvfile:
    spamreader = csv.DictReader(csvfile)

    for row in spamreader:
        if "The Great Gatsby" in row["Title"]:
            print(row)
            #download_book(row["Text#"])
            #find_loc_item(row["Title"])


books = openlibrary_find_book("New Collected Rhymes")

if not books:
    print("Could not find the book")


