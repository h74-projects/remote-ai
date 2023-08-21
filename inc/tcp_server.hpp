#ifndef TCP_SERVER_HPP
#define TCP_SERVER_HPP

#include <stdio.h>
#include <netinet/in.h> 
#include <unistd.h> 
#include <sys/select.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <string>
#include <list>
#include <vector>
#include <map>
#include <netinet/tcp.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <iostream>
#include "client.hpp"

const size_t BUF_SIZE = 1024*1024;

typedef struct sockaddr_in SocketData;

enum ServerTCP_Status{SERVER_SUCCESS,SERVER_SELECT_ERROR,SERVER_SOCKET_ERROR,SERVER_UNINITIALIZED,SERVER_SEND_FAIL};

template <typename Context>
class ServerTCP{

using GotMessage = void(*)(ServerTCP<Context> &_server, Client &a_client, int _id, std::string const &_msg, int _length, Context &_context);
using CloseClient = void(*)(ServerTCP<Context> &_server,int _id, Context &_context);
using NewClient = int(*)(ServerTCP<Context> &_server,SocketData _sockData, int _id, Context &_context);
using OnFail = void(*)(ServerTCP<Context> &_server,int _id, std::string const &_err, Context &_context);

public:
        ServerTCP(int _port, int _backLog, GotMessage _gotMessage, CloseClient _closeClient, NewClient _newClient, OnFail _onFail, Context &_context);
        ~ServerTCP();
        void close_all(Client &_client);
        void socket_set(Client &_client);
        int read_incomming_data(Client &_client);
        int read_incomming_data(int const &);
        void get_clients_map(std::map<int, int> &_clients);
        ServerTCP_Status run_server();
        ServerTCP_Status send_message(std::string const &_data, int _sock);
        ServerTCP_Status stop_server();
        static void thread_server_run(ServerTCP *a_server);
        void close_client(Client &_client);
        char *get_buffer();
        void ClearBuffer();
	

private:
	void AddClient(struct sockaddr_in _sin, int _sock);
	void ReadClientsDataIn();
	void remove_client(Client &_client);
	void remove_client(int const &);
	int ListenMainSocket();
	int BindSockect();
	int OpenIncommingConnectionsSocket();
	void clean_up();
	int OpenSocket();
	Client *get_client_by_id(int const &a_id);
	

private:
        Context &m_context;
	struct sockaddr_in m_sin;
	int m_listenningSocket;
	std::list<Client> m_clients;
	int m_port;
	int m_backLog;
	fd_set m_fdSet;
	char m_buffer[BUF_SIZE];
	int m_activity;
	int m_numberOfClients;
	GotMessage m_gotMessage;
	CloseClient m_closeClient;
	NewClient m_newClient;
	OnFail m_onFail;
	char m_stop;
};



template <typename Context>
ServerTCP<Context>::ServerTCP(int _port, int _backLog, GotMessage _gotMessage, CloseClient _closeClient, NewClient _newClient, OnFail _onFail, Context &_context)
: m_context(_context)
{
        if(!_port || !_backLog || !_gotMessage){
            return;
        }
        m_listenningSocket = OpenSocket();
        if(m_listenningSocket == -1){
            return;
        }
        m_closeClient = _closeClient;
        m_newClient = _newClient;
        m_gotMessage = _gotMessage;
        m_onFail = _onFail;
        m_port = _port;
        m_backLog = _backLog;
        m_stop = 0;
        m_numberOfClients = 0;
        m_sin.sin_family = AF_INET;         
        m_sin.sin_port = htons(_port);  
        m_sin.sin_addr.s_addr = INADDR_ANY;
        OpenIncommingConnectionsSocket();
        BindSockect();
        ListenMainSocket();
        std::list<Client> m_clients = std::list<Client>{};
        ClearBuffer();
}

template <typename Context>
ServerTCP<Context>::~ServerTCP()
{
        for(auto client : m_clients){
                close_all(client);
        }
        close(m_listenningSocket);
}

template <typename Context>
ServerTCP_Status ServerTCP<Context>::run_server()
{
        int new_sock;
        int yes = 1;
        struct sockaddr_in sin;
        socklen_t addrlen;
        m_stop = 0;
        addrlen = sizeof(struct sockaddr_in);
        if (m_listenningSocket == -1) {
            if(m_onFail){
                    m_onFail(*this, -1, std::string{strerror(errno)}, m_context);
            }
            return SERVER_SOCKET_ERROR; 
        }

        while(!m_stop){
                FD_ZERO(&(this->m_fdSet));
                m_activity = 0;
                FD_SET(this->m_listenningSocket, &(this->m_fdSet));
                for(auto client : m_clients){
                        socket_set(client);
                }
                m_activity = select(FD_SETSIZE, &(m_fdSet), NULL, NULL, NULL);
                if(m_activity >= 0 ){
                        if (FD_ISSET(this->m_listenningSocket, &(this->m_fdSet))){
                                new_sock = accept(m_listenningSocket, (struct sockaddr*)&sin, &addrlen);
                                setsockopt(new_sock, IPPROTO_TCP, TCP_NODELAY, (char *) &yes, sizeof(int));
                                if(new_sock >= 0){
                                        if(m_numberOfClients >= m_backLog){
                                                close(new_sock);
                                                if(m_onFail){
                                                        m_onFail(*this, new_sock, "Server busy", m_context);
                                                }
                                                if(m_closeClient){
                                                        m_closeClient(*this, new_sock, m_context);
                                                }
                                        } else {
                                                if(m_newClient){
                                                        if(!m_newClient(*this, sin, new_sock, m_context)){
                                                                close(new_sock);
                                                        } else {
                                                                AddClient(sin,new_sock);
                                                        }
                                                } else {
                                                        AddClient(sin,new_sock);
                                                }
                                        }
                                } else {
                                        if(m_onFail){
                                                m_onFail(*this, new_sock, std::string{strerror(errno)}, m_context);
                                        }
                                }
                                (m_activity)--;
                                if(m_activity <= 0){
                                        continue;
                                }
                        }
                        ReadClientsDataIn();
                        clean_up();
                } else {
                        return SERVER_SELECT_ERROR;
                }
        }
        for(auto client : m_clients){
                close_all(client);
        }
        close(m_listenningSocket);
        return SERVER_SUCCESS;
}

template <typename Context>
ServerTCP_Status ServerTCP<Context>::send_message(std::string const &_data, int _sock)
{
        int sent_bytes;
        sent_bytes = send(_sock, _data.data(), _data.size(), 0);
        if (sent_bytes < 0) {
                if(m_onFail){
                        m_onFail(*this, _sock, std::string{strerror(errno)}, m_context);
                }
                return SERVER_SEND_FAIL;
        }
        return SERVER_SUCCESS;
}

template <typename Context>
ServerTCP_Status ServerTCP<Context>::stop_server()
{
        m_stop = 1;
        return SERVER_SUCCESS;
}

template <typename Context>
void ServerTCP<Context>::close_all(Client &_client)
{
        close(_client.socket());
        if(m_closeClient){
                m_closeClient(*this,_client.socket(), m_context);
        }
}

template <typename Context>
void ServerTCP<Context>::AddClient(struct sockaddr_in _sin, int _sock)
{
        Client client{_sock, _sin};
        m_clients.push_back(client);
        ++(m_numberOfClients);
}

template <typename Context>
void ServerTCP<Context>::clean_up()
{
        for(auto client : m_clients){
                if(client.is_closed()){
                        close(client.socket());
                        --m_numberOfClients;
                        remove_client(client);
                }
        }
        ClearBuffer();  
}

template <typename Context>
void ServerTCP<Context>::ReadClientsDataIn()
{
        for(auto client : m_clients){
                if(client.is_closed()){
                        continue;
                } else {
                        read_incomming_data(client);
                }       
        }
}

template <typename Context>
void ServerTCP<Context>::socket_set(Client &_client)
{
    FD_SET(_client.socket(), &(this->m_fdSet));
}

template <typename Context>
void ServerTCP<Context>::remove_client(Client &_client)
{
        for(auto it = m_clients.begin(); it != m_clients.end(); ++it){
                if(it->socket() == _client.socket()){
                        m_clients.erase(it);
                        return;
                }
        }
}

template <typename Context>
void ServerTCP<Context>::remove_client(int const &a_id)
{
        for(auto it = m_clients.begin(); it != m_clients.end(); ++it){
                if(it->socket() == a_id){
                        m_clients.erase(it);
                        return;
                }
        }
}

template <typename Context>
int ServerTCP<Context>::read_incomming_data(Client &_client)
{
        int result;
        if(FD_ISSET(_client.socket(), &(this->m_fdSet))){     
                result = recv(_client.socket(), m_buffer, BUF_SIZE, 0);
                if (result == 0) {
                        if(m_onFail){
                                m_onFail(*this,_client.socket(), strerror(errno), m_context);
                        }
                        if(m_closeClient){
                                m_closeClient(*this,_client.socket(), m_context);
                        }
                        _client.close();
                } 
                else if (result > 0){
                        m_gotMessage(*this, _client, _client.socket(), m_buffer, result, m_context);
                } 
                else if (result == -1) {
                        if(m_onFail){
                                m_onFail(*this, _client.socket(), std::string{strerror(errno)}, m_context);
                        }
                        _client.close();
                }
                --m_activity;
                if(m_activity <= 0){
                        clean_up();
                        return 0;
                }
                return 1;
        }
        return 1;
}

template <typename Context>
Client *ServerTCP<Context>::get_client_by_id(int const &a_id)
{
        for(auto it = m_clients.begin(); it!= m_clients.end(); ++it){
                if(it->socket() == a_id){
                        return &*it;
                }
        }
        return nullptr;
}

template <typename Context>
int ServerTCP<Context>::read_incomming_data(int const &a_id)
{
        return read_incomming_data(*get_client_by_id(a_id));
}

template <typename Context>
void ServerTCP<Context>::get_clients_map(std::map<int, int> &a_clients_map)
{
        a_clients_map.clear();
        for(auto it = m_clients.begin(); it!= m_clients.end(); ++it){
                a_clients_map[it->socket()] = it->socket();
        }
}

template <typename Context>
int ServerTCP<Context>::OpenIncommingConnectionsSocket()
{
        int optval = 1;
        if (setsockopt(m_listenningSocket, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) < 0){
                perror("reuse failed"); 
                return 0;
        }

        setsockopt(m_listenningSocket,            /* socket affected */
                        IPPROTO_TCP,     /* set option at TCP level */
                        TCP_NODELAY,     /* name of option */
                        (char *) &optval,  /* the cast is historical cruft */
                        sizeof(int));  
        return 1;
}

template <typename Context>
int ServerTCP<Context>::BindSockect()
{
        if ((bind(m_listenningSocket, (struct sockaddr *)&(m_sin), sizeof(struct sockaddr_in))) != 0) {
                perror("bind failed");
                close(m_listenningSocket);
                return 0;   
        }
        return 1;
}

template <typename Context>
int ServerTCP<Context>::ListenMainSocket()
{
        if ((listen(m_listenningSocket, m_backLog)) < 0){
                perror("listen failed");
                close(m_listenningSocket);
                return 0;
        }
        return 1;
}

template <typename Context>
int ServerTCP<Context>::OpenSocket()
{
        int sock;
        sock = socket(AF_INET, SOCK_STREAM, 0); 
        if (sock == -1) {
                perror("failed:");
                return -1;
        }
        return sock;
}

template <typename Context>
void ServerTCP<Context>::thread_server_run(ServerTCP *a_server)
{
        try{
                a_server->run_server();
        } catch(...){
                thread_server_run(a_server);
        }
}


template <typename Context>
void ServerTCP<Context>::close_client(Client &_client)
{
        close(_client.socket());
        --(m_numberOfClients);
        if(m_onFail){
                m_onFail(*this,_client.socket(), strerror(errno), m_context);
        }
        if(m_closeClient){
                m_closeClient(*this,_client.socket(), m_context);
        }
        remove_client(_client);
}

template <typename Context>
void ServerTCP<Context>::ClearBuffer()
{
        for(auto &c : m_buffer){
                if(c == '\0'){
                        break;
                } else {
                        c = '\0';
                }
        }
}

template <typename Context>
char *ServerTCP<Context>::get_buffer()
{
        return m_buffer;
}



#endif /* TCP_SERVER_HPP */
