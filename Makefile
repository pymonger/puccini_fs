puccini_fs : puccini_fs.o log.o utils.o
	gcc -g -o puccini_fs puccini_fs.o log.o utils.o -lrabbitmq `pkg-config fuse --libs`

puccini_fs.o : puccini_fs.c log.h params.h
	gcc -g -Wall -c puccini_fs.c -lrabbitmq `pkg-config fuse --cflags`

log.o : log.c log.h params.h
	gcc -g -Wall -c log.c -lrabbitmq `pkg-config fuse --cflags`

utils.o : utils.c utils.h
	gcc -g -Wall -c utils.c

clean:
	rm -f puccini_fs *.o
