#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

int array_size = 10000000;

#include "omp_apps.h"

int main() 
{
  printf("Dot Product of two arrays\n");
  char *report = compute_dotp(array_size);
  printf("%s\n", report);
  return 0;
}
