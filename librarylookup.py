import bottlenose
import ConfigParser
import lxml.html
import lxml.etree
import requests
import urllib2

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

    def search_library(self):
        """Searches the King County Library System eBook (OverDrive) catalog.

        Returns False if the book is not found.
        """

        # target URL for the form submission
        search_url = 'http://overdrive.downloads.kcls.org/' + \
            '0F2E027C-35D9-43DD-B841-33524FCB0AEB/10/293/en/BANGSearch.dll'

        # Available fields from original form:
        # Title, Creator, Keyword, ISBN, Format=420
        # Language, Publisher, Subject, Award
        # PerPage=5, Sort='SortBy=Relevancy'

        # build the form_data used to submit the form
        form_data = dict(Title=self.title, Format='420', PerPage='5', Sort='SortBy=Relevancy')
        initial_result = requests.post(search_url, data=form_data)

        # fetch redirected URL for the results page
        results_url = 'http://ebooks.kcls.org' + initial_result.headers['location']

        # fetch HTML from the results page
        final_result = requests.get(results_url)
        html_result = final_result.content

        # create list of resulting book titles
        root = lxml.html.fromstring(html_result)
        results = root.xpath('//table/tr/td/table/tr/td/b/a')

        matching_results = 0
        for result in results:
            if result.text == self.title:   # Titles must match exactly
                matching_results += 1

        return matching_results > 0


    def search_amazon(self):
        """Searches Amazon Prime Lending Library

        Returns False if the book is not found.
        """

        # read AWS details from config file
        config = ConfigParser.RawConfigParser()
        config.read('librarylookup.cfg')
        access_key = config.get('Amazon Web Services', 'amazon_access_key_id')
        secret_key = config.get('Amazon Web Services', 'amazon_secret_key')
        assoc_tag = config.get('Amazon Web Services', 'amazon_assoc_tag')

        # connect to AWS API and fetch search results
        amazon = bottlenose.Amazon(access_key, secret_key, assoc_tag)
        xml_result = amazon.ItemSearch(Keywords=self.title +" Lending Library",
            SearchIndex="Books")

        # Prepare the XPath used to location TotalResults
        # ItemSearchResponse (Root) -> Items -> TotalResults
        namespace = '{http://webservices.amazon.com/AWSECommerceService/2011-08-01}'
        xpath = namespace + 'Items/' + namespace + 'TotalResults'

        # Find TotalResults from the XML
        total_results = int(lxml.etree.fromstring(xml_result).findtext(xpath))

        return total_results > 0


class BookCollection():
    def __init__(self):
        self.books = []

    def __str__(self):
        result = ''
        for book in self.books:
            result += '%s \n' % book
        return result

    def find_title(self, title):
        for book in self.books:
            if book.title == title:
                return book

    def add(self, isbn, title, author):
        self.books.append(Book(isbn, title, author))

    def fetch_goodreads_shelf(self, user_id='393281', shelf='to-read'):
        """Returns a list of books from a Goodreads user's bookshelf."""

        # read Goodreads dev key from config file
        config = ConfigParser.RawConfigParser()
        config.read('librarylookup.cfg')
        access_key = config.get('Goodreads', 'goodreads_access_key')

        feed_url = 'http://www.goodreads.com/review/list/' + user_id + \
            '.xml?key=' + access_key + '&v=2&shelf=' + shelf

        # fetch the XML feed
        feed = urllib2.urlopen(feed_url)
        tree = lxml.etree.parse(feed)
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
    myBooks = BookCollection()
    myBooks.fetch_goodreads_shelf()
    myBooks.add('0439023483', 'The Hunger Games', 'Suzanne Collins')
    print myBooks.find_title('The Hunger Games').search_amazon()
    # myBooks.add('0439023483', 'Twilight', 'Stephenie Meyer')
    # print myBooks.find_title('Twilight').search_library()
    # print myBooks.books[0].search_amazon()

if __name__ == '__main__':
    main()