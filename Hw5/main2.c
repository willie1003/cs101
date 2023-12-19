#include <stdio.h>

int main()
{
    int PI;
    int a=1;
    for(int i=1;i<=20000;i++){
        PI+=400000/((2*i-1)*a);
        printf("%d\n",PI);
        a*=-1;
        if(PI==314159){
            printf("%d",2*i-1);
            break;
        }
    }
    
    return 0;
}
