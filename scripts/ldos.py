import os, hashlib, httplib2, logging, shutil, json, uuid, pprint, mimetypes, types
from datetime import datetime
from subprocess import Popen, PIPE
from urllib import urlencode

from pysolr.Solr import Solr, SolrException

log = logging.getLogger()


IGNORE_FILES = [
    '._',
    '.DS_Store',
    '.localized',
    '.fseventsd',
    '.Spotlight',
    '.DocumentRevisions',
    '.TemporaryItems',
    '.Trash',
    'System*Volume*Information',
    'RECYCLER',
]

def getLDOSInfo():
    """Return LDOS root directory and solr url."""

    return "/data/public_fuse", "http://localhost:8984"

def ncdump(file):
    """Run ncdump locally on a file and extract metadata."""

    if not os.path.isfile(file): return None
    pop = Popen(['ncdump', '-h', file], stdin=PIPE, stdout=PIPE, stderr=PIPE, env=os.environ)
    try: sts = pop.wait()  #wait for child to terminate and get status
    except Exception, e: pass
    status = pop.returncode
    result = pop.stdout.read()
    stdErr = pop.stderr.read()
    return result

def tika(file):
    """Run tika locally on a file and extract metadata."""

    if not os.path.isfile(file): return None
    pop = Popen(['tika', '-j', file], stdin=PIPE, stdout=PIPE, stderr=PIPE, env=os.environ)
    try: sts = pop.wait()  #wait for child to terminate and get status
    except Exception, e: pass
    status = pop.returncode
    result = pop.stdout.read()
    stdErr = pop.stderr.read()
    return result

def indexInLDOS(file):
    """Index a file into LDOS."""

    #skip over any files to ignore
    for ign in IGNORE_FILES:
        if os.path.basename(file).startswith(ign): return False

    #get md5
    try: md5hash = hashlib.md5(open(file).read()).hexdigest()
    except IOError, e:
        log.warn("Got IOError trying to hash %s: %s" % (file, str(e)))
        log.warn("Not indexing: %s" % file)
        return

    #get LDOS info 
    ldosRoot, ldosSolr = getLDOSInfo()

    #create solr object
    s = Solr(httplib2.Http(), ldosSolr)

    # add SOLR entry
    documentFields = { 'path': os.path.join(ldosRoot, os.path.basename(file)) }

    # http://docs.python.org/library/uuid.html
    documentFields['doc_id'] = str( uuid.uuid1() )

    timestamp = datetime.now()
    timestampstr = '%s Z' % timestamp.isoformat('T')
    documentFields['doc_created'] = timestampstr
    documentFields['doc_lastmodified'] = timestampstr
    
    documentFields['hash'] = md5hash
    
    # http://www.iana.org/assignments/media-types/index.html
    content_type = mimetypes.guess_type(file, strict=False)[0]
    if content_type is None: content_type = "application/octet-stream"
    documentFields['content_type'] = content_type
    
    #get tika results
    #metadata = netcat('localhost', 8001, open(file).read())
    if file.endswith(".nc"): metadata = ncdump(file)
    else: metadata = tika(file)
    documentFields['metadata'] = metadata
    #pprint.pprint(documentFields)

# --------------------------------------------------------------------------

    try:
        print 'adding: %s' % str(documentFields)
        (response,content) = s.add(documentFields)
        log.debug('response: %s' % str(response) )

        log.debug('content: %s' % str(content) )
        print 'http status: %s' % response.status
        solrResponseHeader = content['responseHeader']
        print 'solr status: %s' % solrResponseHeader['status']

        print 'committing...'
        (response,content) = s.commit()
        log.debug('response: %s' % str(response) )
        log.debug('content: %s' % str(content) )
        print 'http status: %s' % response.status
        solrResponseHeader = content['responseHeader']
        print 'solr status: %s' % solrResponseHeader['status']
    except SolrException, e:
        log.warning('unable to make request to solr: %s' % str(e) )
    except Exception, e:
        log.warning('unable to make request to solr: %s' % str(e) )
    # end try-except
    print 'file="%s", content_type="%s", md5hash="%s", file="%s"' % \
        (file, documentFields['content_type'], md5hash, file)

    # run recognize service
    #http = httplib2.Http()
    #body = urlencode({'hash': md5hash,
    #                  'filename': file})
    #(rec_resp, rec_json) = http.request("http://localhost:5001/services/artifact/recognize", 'POST',
    #    body, {'Content-type': 'application/x-www-form-urlencoded'})
    #print "recognizer response: %s" % rec_resp
    #print "recognizer json: %s" % rec_json

    return True
