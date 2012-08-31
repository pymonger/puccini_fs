#!/usr/bin/env python
import sys, pprint, os, json
from subprocess import Popen, PIPE

from pika import BasicProperties
from pika.adapters import BlockingConnection
from pika.connection import ConnectionParameters

CONNECTION = None
COUNT = 0

def handle_delivery(channel, method_frame, header_frame, body):
    global COUNT
    # Receive the data in 3 frames from RabbitMQ
    #print "demo_receive: Basic.Deliver %s delivery-tag %i: %s" % \
    #      (header_frame.content_type,
    #       method_frame.delivery_tag,
    #       body)

    j = json.loads(body)
    queue_name = str(j["queue_name"])
    #pprint.pprint(j)
    print "#" * 80
    print "queue: %s" % queue_name
    print "delivery-tag: %i" % method_frame.delivery_tag
    print "-" * 80
    print "error: %s" % j["error"]
    print "traceback: %s" % j["traceback"]

    #ask for an action
    while COUNT > 0:
        print "Please select an action:"
        print "1. Print body of message"
        print "2. Move message back on %s queue" % queue_name
        print "3. Remove message from error queue"
        print "4. Do nothing"
        print "\nPress CTRL-C to quit."
        option = raw_input("Select [1,2,3,4] ")
        if option == '1': print "body: %s" % j["body"]
        elif option == '2':
            channel2 = CONNECTION.channel()
            channel2.queue_declare(queue=queue_name, durable=True)
            channel2.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=j['body'],
                          properties=BasicProperties(
                             delivery_mode = 2, # make message persistent
                          ))

            # Acknowledge the message
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            COUNT -= 1
            break
        elif option == '3':
            # Acknowledge the message
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            COUNT -= 1
            break
        elif option == '4': break

    #quit if no more
    if COUNT == 0:
        channel.stop_consuming()
        CONNECTION.close()
        sys.exit()

if __name__ == '__main__':

    #get message count on error queue
    pop = Popen(["sudo", "rabbitmqctl", "list_queues"], 
                stdin=PIPE, stdout=PIPE, stderr=PIPE, env=os.environ)
    try: sts = pop.wait()  #wait for child to terminate and get status
    except Exception, e: print str(e)
    status = pop.returncode
    #print "returncode is:",status
    stdOut = pop.stdout.read()
    stdErr = pop.stderr.read()
    for line in stdOut.split('\n'):
        if line.startswith("error_queue"):
            COUNT = int(line.split()[1])
            break
    print "Total number of messages in error_queue:", COUNT
    if COUNT == 0: sys.exit()

    # Connect to RabbitMQ
    host = (len(sys.argv) > 1) and sys.argv[1] or '127.0.0.1'
    CONNECTION = BlockingConnection(ConnectionParameters(host))

    # Open the channel
    channel = CONNECTION.channel()

    # Declare the queue
    channel.queue_declare(queue="error_queue",
                          durable=True,
                          exclusive=False,
                          auto_delete=False)

    # Add a queue to consume
    channel.basic_consume(handle_delivery, queue='error_queue')

    # Start consuming, block until keyboard interrupt
    try:
        channel.start_consuming()
        print "Press CTRL-C to quit."
    except KeyboardInterrupt:

        # Someone pressed CTRL-C, stop consuming and close
        channel.stop_consuming()
        CONNECTION.close()
