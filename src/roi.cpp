#include "roi.hpp"

std::pair<int, int> &RemoteAIROI::operator[](int a_index)
{
    return m_points[a_index];
}

int &RemoteAIROI::x()
{
    return m_x;
}
