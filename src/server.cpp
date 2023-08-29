#include "server.hpp"
#include "found_object.hpp"
#include "topic.hpp"

RemoteAIServer::RemoteAIServer(int a_port)
: m_server{a_port, 128, read_income, close_client, NULL, NULL, *this}
, m_objects{}
, m_subscribers{}
{
    m_server.run_server();
}

void RemoteAIServer::read_income(ServerTCP<RemoteAIServer> &_server, Client &a_client, int _id, std::string const &_msg, int _length, RemoteAIServer &a_server)
{
    (void)a_client;
    (void)_length;
    Topic topic_name;
    if(a_server.is_subscribe(_msg)){
        a_server.m_subscribers[a_server.get_topic(_msg)].emplace_back(_id, a_client.addr());
        _server.send_message("200", _id);
        return;
    }
    else if(a_server.is_publish(_msg)){
        a_server.set_topic_object(_msg,topic_name);
    }
    if(topic_name && a_server.is_topic_listened(topic_name)){
        a_server.notify_all_subscribers(topic_name);
        _server.send_message("200", _id);
    }
}

void RemoteAIServer::close_client(ServerTCP<RemoteAIServer> &_server, int _id, RemoteAIServer &_context)
{
    (void)_server;
    (void)_context;
    std::cerr << "Client " <<_id<<" closed"<<std::endl;
}

bool RemoteAIServer::is_subscribe(std::string const &a_msg)
{
    size_t data_index = a_msg.find("sub/");
    if(data_index != std::string::npos){
        return true;
    }
    return false;
}

bool RemoteAIServer::is_publish(std::string const &a_msg)
{
    size_t data_index = a_msg.find("@");
    if(data_index != std::string::npos){
        return true;
    }
    return false;
}

Topic RemoteAIServer::get_topic(std::string const &a_msg)
{
    size_t start = a_msg.find("sub/");
    std::string topic_name = a_msg.substr(start+4);
    return Topic{topic_name};
}

void RemoteAIServer::set_topic_object(std::string const &a_msg, Topic &a_topic)
{
    size_t index_start = a_msg.find('@');
    size_t data_index = a_msg.find('|');
    if(data_index != std::string::npos){    
        FoundObject a_object{a_msg.substr(data_index+1)};
        a_topic = Topic{a_msg.substr(index_start+1, data_index-index_start-1)};
        m_objects[a_topic] = a_object;
    }
}

bool RemoteAIServer::is_topic_listened(Topic &a_topic)
{
    auto subs_topic = m_subscribers.find(a_topic);
    if(subs_topic != m_subscribers.end()){
        return true;
    }
    return false;
}

void RemoteAIServer::notify_all_subscribers(Topic const &a_topic)
{
    for(auto &client : m_subscribers[a_topic] ){
        m_server.send_message(m_objects[a_topic].data(),client.socket());
    }
}
