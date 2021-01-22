/* Generate N bytes of random output.  */

/* When generating output this program uses the x86-64 RDRAND
   instruction if available to generate random numbers, falling back
   on /dev/random and stdio otherwise. */

#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "rand64-hw.h"
#include "rand64-sw.h"
#include "rand64-mr.h"
#include "output.h"
#include "options.h"

/* Main program, which outputs N bytes of random data.  */
int
main (int argc, char **argv)
{
  int output = -1;
  char* input = parseOpts(argc, argv, &output);
  /* Check arguments.  */
  bool valid = false;
  long long nbytes;
  int i = 1;
  if(output != -2 && strcmp(input, "error") != 0){
    while (i < argc) {
      if(strcmp(argv[i], "-i") == 0){
	i++;
      } else if (strcmp(argv[i], "-o") == 0) {
	i++;
      } else {
	char *endptr;
	errno = 0;
	nbytes = strtoll (argv[i], &endptr, 10);
	if (errno)
	  perror (argv[i]);
	else
	  valid = !*endptr && 0 <= nbytes;
      }
      i++;
    }
  } else {
    return 1;
  }
  if (!valid)
    {
      fprintf (stderr, "%s: usage: %s NBYTES -i <input> -o <output>\n", argv[0], argv[0]);
      return 1;
    }

  /* If there's no work to do, don't worry about which library to use.  */
  if (nbytes == 0)
    return 0;

  /* Now that we know we have work to do, arrange to use the
     appropriate library.  */

  unsigned long long (*rand64) (void);
  void (*finalize) (void);
  if(strcmp(input, "mrand48_r") != 0){
      if(strcmp(input, "rdrand") == 0){
	if (rdrand_supported ()) {
	    hardware_rand64_init();
	    rand64 = hardware_rand64;
	    finalize = hardware_rand64_fini;
	}
	else {
	  printf("rdrand not supported.");
	  return 1;
	}
      } 
      else if(strcmp(input, "none") == 0) {
	if (rdrand_supported ()) {
	    hardware_rand64_init();
	    rand64 = hardware_rand64;
	    finalize = hardware_rand64_fini;
	}
	else {
	software_rand64_init("/dev/random");
	rand64 = software_rand64;
	finalize = software_rand64_fini;
	}
      }
      else {
	software_rand64_init(input);
	rand64 = software_rand64;
	finalize = software_rand64_fini;
      }
  }
  else if(strcmp(input, "mrand48_r") == 0){
    rand64 = mrand_32;
    finalize = mrand_32_fini;
  }

  int wordsize = sizeof rand64 ();
  int output_errno = 0;
  
  if(output == -1) {
    do {
	unsigned long long x = rand64 ();
	int outbytes = nbytes < wordsize ? nbytes : wordsize;
	if (!writebytes (x, outbytes)) {
	    output_errno = errno;
	    break;
	}
	nbytes -= outbytes;
    } while (0 < nbytes);
  }
  else {
    char toWrite[nbytes];
    int i = 0;
    int len = nbytes;
    do {
      unsigned long long x = rand64 ();
      int outbytes = nbytes < wordsize ? nbytes : wordsize;
      int j;
      for(j = 0; j < outbytes; j++) {
	toWrite[i] = (x >> (8*j)) & 0xff;
	i++;
      }
      nbytes -= outbytes;
    } while(0 < nbytes);
    char* ptr = toWrite;
    int k;
    for(k = 0; k < len/output; k++) {
      write(1, ptr, output);
      ptr += output;
    }
    int resid = len % output;
    if (resid != 0)
      write(1, ptr, resid);
  }

  if (fclose (stdout) != 0)
    output_errno = errno;

  if (output_errno)
    {
      errno = output_errno;
      perror ("output");
    }

  finalize ();
  return !!output_errno;
}
 
