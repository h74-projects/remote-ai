#ifndef ROI_HPP
#define ROI_HPP
#include <vector>

class RemoteAIROI{
public:
    RemoteAIROI() = default;
    ~RemoteAIROI() = default;
    RemoteAIROI(RemoteAIROI const &) = default;
    int &x();
    int &y();
    int &w();
    int &h();

private:
    int m_x;
    int m_y;
    int m_w;
    int m_h;
};


#endif // ROI_HPP