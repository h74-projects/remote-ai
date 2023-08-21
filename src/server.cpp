#include "server.hpp"
#include "found_object.hpp"
#include "topic.hpp"

RemoteAIServer::RemoteAIServer(int a_port)
: m_server{a_port, 128, read_income, close_client, new_client, on_fail, *this}
, m_objects{}
, m_subscribers{}
{
}

void RemoteAIServer::read_income(ServerTCP<RemoteAIServer> &_server, Client &a_client, int _id, std::string const &_msg, int _length, RemoteAIServer &a_server)
{
    (void)_server;
    (void)a_client;
    (void)_length;
    (void)_id;
    size_t data_index = _msg.find("|");
    a_server.m_objects[Topic{_msg.substr(0,data_index)}] = FoundObject{_msg.substr(data_index)};
}
