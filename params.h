// There are a couple of symbols that need to be #defined before
// #including all the headers.

#ifndef _PARAMS_H_
#define _PARAMS_H_

// The FUSE API has been changed a number of times.  So, our code
// needs to define the version of the API that we assume.  As of this
// writing, the most current API version is 28
#define FUSE_USE_VERSION 28

// need this to get pwrite().  I have to use setvbuf() instead of
// setlinebuf() later in consequence.
#define _XOPEN_SOURCE 500

// maintain puccini_fs state in here
#include <limits.h>
#include <stdio.h>
struct puccini_state {
    FILE *logfile;
    char *rootdir;
};
#define PUCCINI_DATA ((struct puccini_state *) fuse_get_context()->private_data)

#endif
