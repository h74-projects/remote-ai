#ifndef SUBSCRIBER_INTERFACE_HPP
#define SUBSCRIBER_INTERFACE_HPP

#include <string>

class Subscriber{
public:
    Subscriber(std::string const &a_ip, int a_port);
    ~Subscriber() = default;

    std::string &ip();
    int &port();

private:
    std::string m_ip;
    int m_port;
};


#endif // SUBSCRIBER_INTERFACE_HPP