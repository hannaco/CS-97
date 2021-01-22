#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include <limits.h>
#include "rand64-mr.h"

unsigned long long mrand_32 (void) {
  long x;
  struct drand48_data randBuffer;
  srand48_r(time(NULL), &randBuffer);
  int res = mrand48_r(&randBuffer, &x);
  unsigned long long y = (unsigned long long)x;
  if (res >= 0) {
    return y;
  }
  else
    abort();
}

void mrand_32_fini (void) {
}
