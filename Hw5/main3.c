#include <stdio.h>

int main()
{
    int a,b;
    for(int i=1;i<=90;i++){
        a=i/10+1;
        b=i%10;
        if(b==0){
            printf("\n");
            continue;
        }
        printf("%d*%d=%d\t",a,b,a*b);
    }
    
    return 0;
}
