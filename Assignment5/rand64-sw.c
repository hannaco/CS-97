#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rand64-sw.h"


/* Software implementation.  */

/* Input stream containing random bytes.  */
FILE *urandstream;

/*Storing file name */
char* name;

/* Size of the file. */
long size;

/*Seed*/
time_t t;

/* Initialize the software rand64 implementation.  */
void 
software_rand64_init (char filename[])
{
  if(filename[0] != '/') {
    printf("Invalid argument to -i -- ");
    abort ();
  }
  urandstream = fopen (filename, "r");
  if (! urandstream)
    abort ();
  if(strcmp(filename, "/dev/random") != 0) {
    fseek(urandstream, 0, SEEK_END); // seek to end of file
    size = ftell(urandstream); // get current file pointer
    fseek(urandstream, 0, SEEK_SET);
  }
  name = realloc(name, strlen(filename)+1);
  strcpy(name, filename);
  srand((unsigned) time(&t));
}

/* Return a random value, using software operations.  */
unsigned long long 
software_rand64 (void)
{
  unsigned long long int x;
  if(strcmp(name, "/dev/random") == 0) {
    if (fread (&x, sizeof x, 1, urandstream) != 1)
      abort ();
  }
  else {
    char words[8];
    int i;
    for(i = 0; i < 8; i++) {
      fseek(urandstream, 0, SEEK_SET);
      int num = (rand() % (size + 1));
      fseek(urandstream, num, 0);
      if (fread (&words[i], sizeof(words[i]), 1, urandstream) != 1)
	abort();
      x = (x << 8) | words[i];
    }
  }
  return x;
}

/* Finalize the software rand64 implementation.  */
void 
software_rand64_fini (void)
{
  fclose (urandstream);
}

