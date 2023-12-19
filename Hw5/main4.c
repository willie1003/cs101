#include <stdio.h>

int main()
{
    int i=345;
    int small=i%10;
    int big;
    
    if(i/1000==0){
        big=0;
    }
    else{
        big=i/1000-i/10000*10;
    }
    
    i=i-small-big*1000;
    i=i+big+small*1000;

    printf("%d",i);
    return 0;
}
