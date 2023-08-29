#include "client.hpp"

Client::Client(int _socket, sockaddr_in _sin)
:m_sin(_sin)
, m_socket(_socket)
, m_to_close(false)
{
}

sockaddr_in &Client::addr()
{
    return m_sin;
}

int &Client::socket()
{
    return m_socket;
}

bool Client::is_closed()
{
    return m_to_close == true;
}

void Client::close()
{
    m_to_close = true;
}
