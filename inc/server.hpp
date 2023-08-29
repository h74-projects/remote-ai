#ifndef REMOTE_AI_SERVER_HPP
#define REMOTE_AI_SERVER_HPP

#include <map>
#include <string>

#include "tcp_server.hpp"
#include "topic.hpp"
#include "found_object.hpp"
#include "subscriber.hpp"
#include "client.hpp"

class RemoteAIServer{
public:
    RemoteAIServer(int a_port);

private:
    static void read_income(ServerTCP<RemoteAIServer> &_server, Client &a_client, int _id, std::string const &_msg, int _length, RemoteAIServer &_context);
    static void close_client(ServerTCP<RemoteAIServer> &_server,int _id, RemoteAIServer &_context);
    static int new_client(ServerTCP<RemoteAIServer> &_server,SocketData _sockData, int _id, RemoteAIServer &_context);
    static void on_fail(ServerTCP<RemoteAIServer> &_server,int _id, std::string const &_err, RemoteAIServer &_context);
    bool is_subscribe(std::string const &a_msg);
    bool is_publish(std::string const &a_msg);
    Topic get_topic(std::string const &a_msg);
    void set_topic_object(std::string const &a_msg, Topic &a_topic);
    bool is_topic_listened(Topic &a_topic);
    void notify_all_subscribers(Topic const &a_topic);
    friend class ServerTCP<RemoteAIServer>;

private:
    ServerTCP<RemoteAIServer> m_server;
    std::map<Topic, FoundObject> m_objects;
    std::map<Topic, std::vector<Client>> m_subscribers;
};


#endif //REMOTE_AI_SERVER_HPP