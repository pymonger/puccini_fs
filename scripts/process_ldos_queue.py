#!/usr/bin/env python
import pika, socket, time

from pikaUtils import pika_callback
from ldos import indexInLDOS

pika.log.setup(pika.log.DEBUG, color=True)


@pika_callback("ldos_index")
def ldos_index_callback(ch, method, properties, body):
    pika.log.info("Indexing into LDOS: %s" % body)
    indexInLDOS(body)

if __name__ == "__main__":
    connection = None
    print "Starting up queue worker for ldos_index."
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='localhost'))
            break
        except socket.error, e:
            print "Failed to connect: %s" % str(e)
            time.sleep(1)
    
    #set ldos indexer
    channel = connection.channel()
    channel.queue_declare(queue='ldos_index', durable=True)
    pika.log.info(' [*] Waiting for ldos uploads to process.')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(ldos_index_callback,
                          queue='ldos_index')
    
    pika.log.info('To exit press CTRL+C')

    channel.start_consuming()
