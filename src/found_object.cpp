#include "found_object.hpp"
#include <vector>
#include <string>
#include <iostream>
#include <memory>

FoundObject::FoundObject(std::string const &a_data)
{
    std::vector<size_t> indexes;
    size_t i = 0;
    while( indexes.size() < 5){
        if(a_data[i]=='|'){
            indexes.push_back(i);
        }
        ++i;
    }
    m_time_taken = std::stoul(a_data.substr(0, indexes[0]));
    m_source = a_data.substr(indexes[0]+1, indexes[1]);
    m_roi.x() = std::stoi(a_data.substr(indexes[1]+1, indexes[2]));
    m_roi.y() = std::stoi(a_data.substr(indexes[2]+1, indexes[3]));
    m_roi.w() = std::stoi(a_data.substr(indexes[3]+1, indexes[4]));
    m_roi.h() = std::stoi(a_data.substr(indexes[4]+1));
    m_raw = a_data;
}

time_t FoundObject::time() const
{
    return m_time_taken;
}

std::string FoundObject::source() const
{
    return m_source;
}

RemoteAIROI FoundObject::roi() const
{
    return m_roi;
}

std::string &FoundObject::data()
{
    return m_raw;
}
