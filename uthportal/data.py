#!/usr/bin/env python
# -*- coding: utf-8 -*-


### inf.courses ########################################
courses_data = { }

courses_data['ce120'] = {
    'code': 'ce120',
    'announcements': {
        'link': 'http://inf-server.inf.uth.gr/courses/CE120/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Προγραμματισμός 1',
        'link': 'http://inf-server.inf.uth.gr/courses/CE120/',
    }
}

courses_data['ce121'] = {
    'code': 'ce121',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE121/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Προγραμματισμός 2',
        'link': 'http://inf-server.inf.uth.gr/courses/CE121/',
    }
}

courses_data['ce213'] = {
    'code': 'ce213',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE213/news.html',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Αριθμητική Ανάλυση',
        'link': 'http://inf-server.inf.uth.gr/courses/CE213/',
    }
}

courses_data['ce230'] = {
    'code': 'ce230',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE230/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Ανάλυση Κυκλωμάτων',
        'link': 'http://inf-server.inf.uth.gr/courses/CE230/'
    }
}

courses_data['ce232'] = {
    'code': 'ce232',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE232/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Οργάνωση και Σχεδίαση Η/Υ',
        'link': 'http://inf-server.inf.uth.gr/courses/CE232/'
    }
}

courses_data['ce321'] = {
    'code': 'ce321',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE321/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Λειτουργικά Συστήματα',
        'link': 'http://inf-server.inf.uth.gr/courses/CE321/',
    }
}

courses_data['ce420'] = {
    'code': 'ce420',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE420/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Σχεδίαση και Ανάπτυξη Λογισμικού',
        'link': 'http://inf-server.inf.uth.gr/courses/CE420/',
    }
}

courses_data['ce431'] = {
    'code': 'ce431',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE431/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Αρχιτεκτονική Παράλληλων Συστημάτων',
        'link': 'http://inf-server.inf.uth.gr/courses/CE431/'
    }
}


courses_data['ce536'] = {
    'code': 'ce536',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE536/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Εργαστήριο Αναλογικών Συστημάτων VLSI',
        'link': 'http://inf-server.inf.uth.gr/courses/CE536/'
    }
}


courses_data['ce538'] = {
    'code': 'ce538',
    'announcements': {
        'link':'http://inf-server.inf.uth.gr/courses/CE536/',
        'site': [ ],
        'emails': [ ],
        'last_updated': u''
    },
    'info': {
        'name': 'Αρχιτεκτονική Παράλληλων Συστημάτων',
        'link': 'http://inf-server.inf.uth.gr/courses/CE538/'
    }
}

### uth.rss ############################################

uth_rss = { }
uth_rss_suffix = '?format=feed&type=rss'

uth_rss['news'] = {
    'type': 'news',
    'link': 'http://uth.gr/news',
    'link_suffix': uth_rss_suffix,
    'title': u'Νέα Πανεπιστημίου Θεσσαλίας',
    'entries': [ ],
    'last_updated': u''
}

uth_rss['events'] = {
    'type': 'events',
    'link': 'http://uth.gr/events',
    'link_suffix': uth_rss_suffix,
    'title': u'Προσεχείς Εκδηλώσεις Π.Θ',
    'entries': [ ],
    'last_updated': u''
}

uth_rss['genannounce'] = {
    'type': 'genannounce',
    'link': 'http://uth.gr/genannounce',
    'link_suffix': uth_rss_suffix,
    'title': u'Γενικές Ανακοινώσεις Π.Θ',
    'entries': [ ],
    'last_updated': u''
}

### Init collections ###################################

## Structure
## 'database-path' : ( dict-of-documents, id-key-of-document )
instructions = {
        'inf.courses' : ( courses_data, 'code' ),
        'uth.rss' : ( uth_rss, 'type' )
}
