#UTHPortal server

Server side component of the UTHPortal application.

UTHPortal, an application for the students of the [University of Thessaly](http://www.uth.gr/), currently in the planning and hacking stages, will be a mobile app to serve information about courses and the university in general, right to their smartphone.

The server side component of the application gathers information from various sources, such as the courses webpages, the eClass platform and the mailing lists of the university, stores it to a database, and serves it as json files through a HTTP RESTful API.

See also the mobile component of the application: [UTHPortal Android](https://github.com/VolosHack/UTHPortal-Android)

A project of [VolosHack](http://voloshack.tk/), the University of Thessaly hacker group.

server technology stack
---
Python

MongoDB

Python modules
---
**Flask**, a micro web application framework http://flask.pocoo.org/

**PyMongo**, the Python driver for MongoDB http://api.mongodb.org/python/current/

**gevent**, a coroutine-based networking library http://www.gevent.org/

**Requests**, an HTTP library http://docs.python-requests.org/

**Beautiful Soup**, a library for pulling data out of HTML and XML files http://www.crummy.com/software/BeautifulSoup/

**Universal Feed Parser**, an Atom and RSS feed parser https://pythonhosted.org/feedparser/
