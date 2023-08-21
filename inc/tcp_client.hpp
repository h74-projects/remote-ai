#ifndef CLIENT_TCP_HPP
#define CLIENT_TCP_HPP

#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <errno.h>
#include <string>
#include <condition_variable>

class Client{
public:
	Client(int _port, int _family, std::string const &_address, size_t _bufferSize = 4096);
	Client(Client const &) = default;
	Client &operator=(Client const &) = default;
	~Client();
	int CreateConnection();
	int ClientRecieveData();
	void *GetDataBuffer();
	std::string get_str_income();
	void ClearBuffer();

	template <typename T>
	int ClientSendData(T a_data, size_t a_length);

private:
	std::condition_variable m_cv;
	int m_socket;
	int m_port;
	int m_sinFamily;
	unsigned int m_sin_len;
	struct sockaddr_in m_sin;
	char *m_buffer;
	std::string m_address;
	
};

template <typename T>
int Client::ClientSendData(T _data, size_t a_length)
{
	int sent_bytes = send(m_socket, (unsigned char *)_data, a_length, 0);
	if (sent_bytes < 0) {
		perror("send failed");
		return 0;
	}
	return 1;
}


#endif //CLIENT_TCP_HPP