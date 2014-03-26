#UTHPortal server

Server side component of the UTHPortal application.

UTHPortal, an application for the students of the [University of Thessaly](http://www.uth.gr/), currently in the planning and hacking stages, will be a mobile app to serve information about courses and the university in general, right to their smartphone.

The server side component of the application gathers information from various sources, such as the courses webpages, the eClass platform and the mailing lists of the university, stores it to a database, and serves it as json files through a HTTP RESTful API.

See also the mobile component of the application: [UTHPortal Android](https://github.com/VolosHack/UTHPortal-Android)

A project of [VolosHack](http://voloshack.tk/), the University of Thessaly hacker group.

technology stack
---
**[Python](https://www.python.org/)**: widely used, general-purpose, high-level programming language

**[MongoDB](https://www.mongodb.org/)**: document-oriented database

Python modules
---
**[Flask](http://flask.pocoo.org/)**: lightweight web application framework

**[PyMongo](http://api.mongodb.org/python/current/)**: driver for MongoDB

**[gevent](http://www.gevent.org/)**: coroutine-based networking library

**[Requests](http://docs.python-requests.org/)**: HTTP library

**[Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)**: library for pulling data out of HTML and XML files

**[Universal Feed Parser](https://pythonhosted.org/feedparser/)**: Atom and RSS feed parser
