#ifndef FOUND_OBJECT_HPP
#define FOUND_OBJECT_HPP
#include <map>
#include <ctime>
#include <string>

#include "roi.hpp"

class FoundObject{
public:
    FoundObject() = default;
    FoundObject(std::string const &a_data);
    FoundObject(FoundObject &a_data) = default;
    ~FoundObject() = default;

public:
    time_t time() const;
    std::string source() const;
    RemoteAIROI roi() const;
    std::string &data();


private:
    time_t m_time_taken;
    std::string m_source;
    RemoteAIROI m_roi;
    std::string m_raw;
};


#endif // FOUND_OBJECT_HPP