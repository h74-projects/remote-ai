#ifndef TOPIC_INTERFACE_HPP
#define TOPIC_INTERFACE_HPP

#include <string>

class Topic{
public:
    Topic();
    Topic(std::string const &a_name);
    ~Topic() = default;
    bool operator==(std::string const &a_name) const;
    bool operator<(Topic const &a_topic) const;
    operator bool() const;
    std::string &name();
    std::string name() const;

private:
    std::string m_name;
};


#endif // TOPIC_INTERFACE_HPP