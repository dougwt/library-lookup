import urllib2
import xml.etree.ElementTree as ET

class Book():
    def __init__(self, isbn='', title='', author=''):
        self.isbn = isbn
        self.title = title
        self.author = author

    def __str__(self):
        result =  'ISBN:\t%s\n' % self.isbn
        result += 'Title:\t%s\n' % self.title
        result += 'Author:\t%s\n' % self.author
        return result.encode('utf-8')

    def search_library(self, title):
        """Searches the King County Library System eBook (Overdrive) catalog.

        Returns False if the book is not found.
        """

        # target URL for the form submission
        search_url = 'http://overdrive.downloads.kcls.org/' + \
            '0F2E027C-35D9-43DD-B841-33524FCB0AEB/10/293/en/BANGSearch.dll'

        return False


    def search_amazon(self, title):
        """Searches Amazon Prime Lending Library

        Returns False if the book is not found.
        """

        # http://www.amazon.com/s?k=prime+eligible&n=154606011

        return False


class BookCollection():
    def __init__(self):
        self.books = []

    def __str__(self):
        result = ''
        for book in self.books:
            result += '%s \n' % book
        return result

    def fetch_goodreads_shelf(self, user_id='393281', shelf='to-read'):
        """Returns a list of books from a Goodreads user's bookshelf."""

        feed_url = 'http://www.goodreads.com/review/list/' + user_id + \
            '.xml?key=lABxjgPANTVFx8nAItPQ&v=2&shelf=' + shelf

        # fetch the XML feed
        feed = urllib2.urlopen(feed_url)
        tree = ET.parse(feed)
        feed.close()

        # crawl through the XML feed looking for each book element
        # then add the relevant data for each book to our list
        element = tree.find('reviews')
        for subelement in element:
            book = subelement.find('book')

            title = self.strip_series(book.find('title').text.strip())
            isbn = book.find('isbn').text
            author = book.find('authors').find('author').find('name').text

            self.books.append(Book(isbn, title, author))

    def strip_series(self, title):
        """Removes the series name from a given title.

        Example: A Game of Thrones (A Song of Ice and Fire #1)
        """

        return str.split(title, '(')[0]


def main():
    books = BookCollection()
    books.fetch_goodreads_shelf()
    print books

if __name__ == '__main__':
    main()
