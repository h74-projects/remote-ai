#include "subscriber.hpp"

Subscriber::Subscriber(std::string const &a_ip, int a_port)
: m_ip(a_ip)
, m_port(a_port)
{
}

std::string &Subscriber::ip()
{
    return m_ip;
}

int &Subscriber::port()
{
    return m_port;
}
