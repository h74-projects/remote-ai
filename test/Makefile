INC_PATH = ../inc
SRC_PATH = ../src
CXX = g++
CC = $(CXX)

CFLAGS = -Wall -Werror
CFLAGS+= -Wextra
CFLAGS+= -pedantic
CFLAGS+= -DDEBUG

CXXFLAGS = $(CFLAGS)
CXXFLAGS += -std=c++17

# flags for preprocessor
CPPFLAGS = -I$(INC_PATH)/

OBJECTS = $(SRC_PATH)/template.o utest.o

TARGET = utest

all: utest

utest : $(OBJECTS)

vala: $(TARGET)
	valgrind --leak-check=yes -s ./$(TARGET)

clean:
	@$(RM) $(TARGET) $(OBJECTS)

.PHONY: clean all check


# dependencies
template.o: $(INC_PATH)/template.hpp
utest.o: $(INC_PATH)/template.hpp
