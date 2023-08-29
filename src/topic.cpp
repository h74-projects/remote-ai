#include "topic.hpp"

Topic::Topic()
: m_name{}
{
}

Topic::Topic(std::string const &a_name)
: m_name(a_name)
{
}

bool Topic::operator==(std::string const &a_name) const
{
    return m_name == a_name;
}

bool Topic::operator<(Topic const &a_topic) const
{
    return m_name.compare(a_topic.m_name) < 0;
}

Topic::operator bool() const
{
    return m_name.size() > 0;
}

std::string &Topic::name()
{
    return m_name;
}
