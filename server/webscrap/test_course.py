from util import fetch_html, get_bsoup, slugify
from courses.announcements import parsers
from os.path import isfile

if __name__ == '__main__':
    def print_dict():
        link = 'http://inf-server.inf.uth.gr/courses/CE121/'
        filename = slugify(link)

        if not isfile(filename):
            data = fetch_html(link)
            with open(filename,'wb') as f:
                f.write(data)
        else:
            with open(filename,'r') as f:
                data = f.read()

        list = parsers['ce121'](get_bsoup(data))

        for item in list:
            for key in item:
                print key + ':' + unicode(item[key])

    print_dict()

