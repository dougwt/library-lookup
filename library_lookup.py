import urllib2
import xml.etree.ElementTree as ET

def get_goodreads_shelf(user_id='393281', shelf='to-read'):
    """Returns a list of books from a Goodreads user's bookshelf."""

    feed_url = 'http://www.goodreads.com/review/list/'
    feed_url += user_id + '.xml?key=lABxjgPANTVFx8nAItPQ&v=2' 
    feed_url += '&shelf=' + shelf

    # fetch the XML feed
    feed = urllib2.urlopen(feed_url)
    tree = ET.parse(feed)
    feed.close()

    books = []

    # crawl through the XML feed looking for each book element
    # then add the relevant data for each book to our list
    element = tree.find('reviews')
    for subelement in element:
        title = strip_series(subelement.find('book').find('title').text.strip())
        isbn = subelement.find('book').find('isbn').text
        author = subelement.find('book').find('authors').find('author').find('name').text
        books.append({'title':title, 'isbn':isbn, 'author':author})

    return books


def strip_series(title):
    """Removes the series name from a given title.
    
    Example: A Game of Thrones (A Song of Ice and Fire #1)
    """

    return str.split(title, '(')[0]


def search_library(title):
    """Searches the King County Library System eBook (Overdrive) catalogue.

    Returns False if the book is not found.
    """
    
    # http://overdrive.downloads.kcls.org/0F2E027C-35D9-43DD-B841-33524FCB0AEB/10/293/en/BANGSearch.dll 
    return False


def main():

    books = get_goodreads_shelf()

    for book in books:
        print 'ISBN:\t', book['isbn']
        print 'Title:\t', book['title']
        print 'Author:\t', book['author']
        print

if __name__ == '__main__':
    main()
