#include <stdio.h>

int main()
{
    int i,j;
    
    for(i=1;i<=7;i++){
        
        printf("%*d",8-i,i);
        for(j=1;j<=i-1;j++){
            printf("%*d",2,i);
        }
        printf("\n");
    }
    
    return 0;
}
