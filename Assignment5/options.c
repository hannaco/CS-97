#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include "options.h"

char* parseOpts(int argc, char* argv[], int* output){
  int opt;
  while((opt = getopt(argc, argv, "i:o:")) != -1) {
    switch(opt) {
    case 'o':
      *output = atoi(optarg);
      break;
    case 'i':
      return optarg;
    case '?':
      if(optopt == 'i')
	return "error";
      else
	*output = -2;
      break;
    }
  }
  return "none";
}
