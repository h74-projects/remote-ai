#include "found_object.hpp"
#include <vector>
#include <string>

FoundObject::FoundObject(std::string const &a_data)
{
    std::vector<size_t> indexes;
    size_t i = 0;
    while( indexes.size() < 6){
        if(a_data[i]=='|'){
            indexes.push_back(i);
        }
        ++i;
    }
    m_time_taken = std::stoul(a_data.substr(0, indexes[0]));
    m_source = a_data.substr(indexes[0], indexes[1]);
    m_roi[0].first = std::stoi(a_data.substr(indexes[1], indexes[2]));
    m_roi[0].second = std::stoi(a_data.substr(indexes[2], indexes[3]));
    m_roi[1].first = std::stoi(a_data.substr(indexes[3], indexes[4]));
    m_roi[1].second = std::stoi(a_data.substr(indexes[4], indexes[5]));
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
