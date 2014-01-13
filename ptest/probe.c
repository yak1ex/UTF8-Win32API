#include <stdio.h>
#include <stdlib.h>

static void outonehex(unsigned char c)
{
    if(c <= 9) {
        putc(c + '0', stdout);
    } else {
        putc(c - 10 + 'A', stdout);
    }
}

static void outhex(unsigned char c)
{
    outonehex((c >> 4) & 0xF);
    outonehex(c & 0xF);
}

static void outhexstr(char *p)
{
    while(*p) outhex(*p++);
    putc('\n', stdout);
}

int main(int argc, char **argv)
{
    int i;
    char **env;
    puts("[ENV]");
    for(env = environ; env && *env; ++env) {
        putc('#', stdout); puts(*env);
        outhexstr(*env);
    }
    puts("[ARGV]");
    for(i = 0; i < argc; ++i) {
        putc('#', stdout); puts(argv[i]);
        outhexstr(argv[i]);
    }
    return 0;
}
