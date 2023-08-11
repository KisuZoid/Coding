//2
#include <stdio.h>
#include "cs50.h"
#include <string.h>

int main(void)
{
    string names[] = {"Kislay", "Kisu"};
    string numbers[] = {"+911234567890", "+911029384756"};

    string name = get_string("Name: ");
    for (int i = 0; i < 2; i++)
    {
        if (strcmp(names[i], name) == 0)
        {
            printf("Found %s\n", numbers[i]);
            return 0;
        }
    }
    printf("Not found\n");
    return 1;
}