#ifndef CLASSES_UNDER_TEST_
#define CLASSES_UNDER_TEST_

#include <iostream>
#include <stdexcept>

class BallException : public std::runtime_error {
public:
	BallException() : std::runtime_error("no ball games allowed here!") { }
};

class Ball{
	int m_rad;
public:
	Ball(int rad): m_rad(rad) {}
	int radius() const { return m_rad;}
	void scale(int s) { m_rad *= s; }
	bool operator==(const Ball& b) const { return m_rad == b.m_rad; }
};

bool operator!=(const Ball& a, const Ball& b) {
	return !(a == b);
}

std::ostream& operator<<(std::ostream& os, const Ball& b) {
	os << "Ball with radius == " <<  b.radius();
	return os;
}

#endif
