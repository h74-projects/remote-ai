#ifndef REMOTE_AI_CLIENT_HPP
#define REMOTE_AI_CLIENT_HPP

#include <map>
#include <string>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h> 
#include <unistd.h>

typedef struct sockaddr_in SocketData;

class Client{
public:
	Client(int _socket, struct sockaddr_in _sin);

    struct sockaddr_in &addr();
    int &socket();
    bool is_closed();
    void close();

private:
	struct sockaddr_in m_sin;
	int m_socket;
	bool m_to_close;
};


#endif //REMOTE_AI_CLIENT_HPP