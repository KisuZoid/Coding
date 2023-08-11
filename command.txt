cd : change directory
cp : copy file
ls : list of files
mkdir : make directory
mv : move/rename
rm : remove
rmdir : remove directory
cd .. : previous directory


for using mingw, let program is called program.c
 use: gcc program.c -o program    in command line

 for adding cs50 library, go to Coding>cs50>libcs50-main>src
 and copy both the files and pasted it to your local code space from where you can include this in your code using:

 #include "cs50.h"

 for run the program use: gcc program.c -o program cs50.c
  and then use: ./program