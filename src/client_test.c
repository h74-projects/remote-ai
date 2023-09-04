#include "../../h74/Network/ChatServerProject/ClientNet.h"

int main()
{
    ClientNet* client = createClient();
    char* buffer = "<sub>face</sub>";
    Send(client, buffer, 16);
    return 0;
}