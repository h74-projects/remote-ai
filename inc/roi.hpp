#ifndef ROI_HPP
#define ROI_HPP
#include <vector>

class RemoteAIROI{
public:
    RemoteAIROI() = default;
    ~RemoteAIROI() = default;
    RemoteAIROI(RemoteAIROI const &) = default;
    std::pair<int,int> &operator[](int a_index);

private:
    std::vector<std::pair<int,int>> m_points;
};


#endif // ROI_HPP