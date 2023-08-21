#include "tcp_server.hpp"

#include <stdio.h>
#include <netinet/in.h> 
#include <netinet/tcp.h>
#include <unistd.h> 
#include <sys/select.h>
#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <string>
#include <list>
#include <iostream>
#include <vector>

const size_t BUF_SIZE = 1024;

ServerTCP::ServerTCP(int _port, int _backLog, GotMessage _gotMessage, CloseClient _closeClient, NewClient _newClient, OnFail _onFail, void *_context)
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
    m_context = _context;
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

ServerTCP::~ServerTCP()
{
        for(auto client : m_clients){
                close_all(client);
        }
        close(m_listenningSocket);
}


ServerTCP_Status ServerTCP::run_server()
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
        FD_ZERO(&(m_fdSet));
        m_activity = 0;
            FD_SET(m_listenningSocket, &(m_fdSet));
                for(auto client : m_clients){
                        socket_set(client);
                }
        m_activity = select(FD_SETSIZE, &(m_fdSet), NULL, NULL, NULL);
        if(m_activity >= 0 ){
                        if (FD_ISSET(m_listenningSocket, &(m_fdSet))){
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
                        }
                        else{
                        if(m_newClient){
                                    if(!m_newClient(*this, sin, new_sock, m_context)){
                                        close(new_sock);
                                    }
                                    else{
                                        AddClient(sin,new_sock);
                                }
                                }
                                else{
                                                        AddClient(sin,new_sock);
                                                }
                        }
                }
                else{
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
        }
        else{
                return SERVER_SELECT_ERROR;
        }
    }
        for(auto client : m_clients){
        close_all(client);
    }
        close(m_listenningSocket);
    return SERVER_SUCCESS;
}
 
ServerTCP_Status ServerTCP::send_message(std::string const &_data, int _sock)
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

ServerTCP_Status ServerTCP::stop_server()
{
        m_stop = 1;
        return SERVER_SUCCESS;
}

void ServerTCP::close_all(Client &_client)
{
        close(_client.m_socket);
        if(m_closeClient){
        m_closeClient(*this,_client.m_socket, m_context);
    }
}

void ServerTCP::AddClient(struct sockaddr_in _sin, int _sock)
{
    Client client{_sock, _sin};
        m_clients.push_back(client);
    ++(m_numberOfClients);
}
void ServerTCP::clean_up()
{
        for(auto client : m_clients){
                if(client.m_to_close){
                        close(client.m_socket);
            --m_numberOfClients;
                        remove_client(client);
                }
        }
        ClearBuffer();  
}
void ServerTCP::ReadClientsDataIn()
{
        for(auto client : m_clients){
                if(client.m_to_close){
                        continue;
                } else {
                        read_incomming_data(client);
                }       
        }
}

void ServerTCP::socket_set(Client &_client)
{
    FD_SET(_client.m_socket, &(m_fdSet));
}


void ServerTCP::remove_client(Client &_client)
{
        for(auto it = m_clients.begin(); it != m_clients.end(); ++it){
                if(it->m_socket == _client.m_socket){
            m_clients.erase(it);
            return;
        }
        }
}

void ServerTCP::remove_client(int const &a_id)
{
        for(auto it = m_clients.begin(); it != m_clients.end(); ++it){
                if(it->m_socket == a_id){
            m_clients.erase(it);
            return;
        }
        }
}

int ServerTCP::read_incomming_data(Client &_client)
{
        int result;
    if(FD_ISSET(_client.m_socket, &(m_fdSet))){

        result = recv(_client.m_socket, m_buffer, BUFFER_SIZE, 0);
        if (result == 0) {
            if(m_onFail){
                m_onFail(*this,_client.m_socket, strerror(errno), m_context);
            }
                if(m_closeClient){
                                m_closeClient(*this,_client.m_socket, m_context);
                }
                        _client.m_to_close = true;
        } 
        else if (result > 0){
                        m_gotMessage(*this, _client, _client.m_socket, m_buffer, result, m_context);
        } 
        else if (result == -1) {
                if(m_onFail){
                m_onFail(*this, _client.m_socket, std::string{strerror(errno)}, m_context);
            }
                        _client.m_to_close = true;
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
Client *ServerTCP::get_client_by_id(int const &a_id)
{
        for(auto it = m_clients.begin(); it!= m_clients.end(); ++it){
        if(it->m_socket == a_id){
            return &*it;
        }
    }
    return nullptr;
}
int ServerTCP::read_incomming_data(int const &a_id)
{
    return read_incomming_data(*get_client_by_id(a_id));
}

void ServerTCP::get_clients_map(std::map<int, int> &a_clients_map)
{
        a_clients_map.clear();
        for(auto it = m_clients.begin(); it!= m_clients.end(); ++it){
                a_clients_map[it->m_socket] = it->m_socket;
        }
}

int ServerTCP::OpenIncommingConnectionsSocket()
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

int ServerTCP::BindSockect()
{
        if ((bind(m_listenningSocket, (struct sockaddr *)&(m_sin), sizeof(struct sockaddr_in))) != 0) {
                perror("bind failed");
                close(m_listenningSocket);
                return 0;   
        }
        return 1;
}

int ServerTCP::ListenMainSocket()
{
        if ((listen(m_listenningSocket, m_backLog)) < 0){
       perror("listen failed");
       close(m_listenningSocket);
       return 0;
        }
        return 1;
}

int ServerTCP::OpenSocket()
{
        int sock;
    sock = socket(AF_INET, SOCK_STREAM, 0); 
    if (sock == -1) {
        perror("failed:");
        return -1;
    }
    return sock;
}

void ServerTCP::thread_server_run(ServerTCP *a_server)
{
        try{
                a_server->run_server();
        } catch(...){
                thread_server_run(a_server);
        }
}

void ServerTCP::close_client(Client &_client)
{
    close(_client.m_socket);
    --(m_numberOfClients);
    if(m_onFail){
        m_onFail(*this,_client.m_socket, strerror(errno), m_context);
    }
    if(m_closeClient){
                m_closeClient(*this,_client.m_socket, m_context);
    }
        remove_client(_client);
}

void ServerTCP::ClearBuffer()
{
        for(auto &c : m_buffer){
                if(c == '\0'){
                        break;
                } else {
                        c = '\0';
                }
        }
}


char *ServerTCP::get_buffer()
{
        return m_buffer;
}


