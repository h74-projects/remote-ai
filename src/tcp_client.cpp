#include "tcp_client.hpp"

#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <string>
#include <mutex>
#include <iostream>

static int ClientOpenSocket();

Client::Client(int _port, int _family, std::string const &_address, size_t _bufferSize)
: m_cv{}
{
	struct sockaddr_in sin;
	memset(&sin, 0, sizeof(sin));
	sin.sin_family = _family;
	sin.sin_addr.s_addr = INADDR_ANY;
	sin.sin_port = htons(_port);
	m_address = _address;
	m_socket = ClientOpenSocket();
	m_port = _port;
	m_sin = sin;
    m_buffer = new char[_bufferSize];
}

int Client::CreateConnection()
{
	struct sockaddr_in sin;
	memset(&sin, 0 ,sizeof(sin));
	sin.sin_family = AF_INET;
	sin.sin_addr.s_addr = inet_addr(m_address.c_str());
	sin.sin_port = htons(m_port);
	if (connect(m_socket, (struct sockaddr *) &sin, sizeof(sin)) < 0) {
		perror("connection failed");
		return 0;
	}
	m_sin = sin;
	return 1;
}



int Client::ClientRecieveData()
{
	int expected_data_len = sizeof(m_buffer);
	int read_bytes = recv(m_socket, m_buffer, expected_data_len, 0);
	if (read_bytes == 0) {	
		close(m_socket);
		return 0;
	}
	else if (read_bytes < 0) {
		perror("recv failed");
		return 0;
	}
	else{
		if(strcmp(m_buffer,"!!")==0){
			close(m_socket);
			return 0;
		}
		else{
			return 1;
		}
	}

}

Client::~Client()
{
	close(m_socket);
    delete(m_buffer);
}

void *Client::GetDataBuffer()
{
	return &m_buffer;
}

std::string Client::get_str_income()
{
	std::mutex lock;
	lock.lock();
    std::string out{m_buffer};
	return out;
}

static int ClientOpenSocket()
{
	int server_fd;
	if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		perror("failed");
		return 0;
	}
	else{
		return server_fd;
	}
}

void Client::ClearBuffer()
{
	for(size_t i = 0; i < strlen(m_buffer); i++){
		if(m_buffer[i] == '\0'){
			break;
		} else {
			m_buffer[i] = '\0';
		}
	}
}
