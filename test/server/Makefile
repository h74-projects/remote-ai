INC_PATH = ../../inc
SRC_PATH = ../../src
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

OBJECTS = $(SRC_PATH)/server.o $(SRC_PATH)/roi.o $(SRC_PATH)/topic.o $(SRC_PATH)/found_object.o $(SRC_PATH)/subscriber.o $(SRC_PATH)/client.o utest.o

TARGET = utest

all: utest

utest : $(OBJECTS)

vala: $(TARGET)
	valgrind --leak-check=yes -s ./$(TARGET)

clean:
	@$(RM) $(TARGET) $(OBJECTS)

.PHONY: clean all check


# dependencies
client.o: $(INC_PATH)/client.hpp
subscriber.o: $(INC_PATH)/subscriber.hpp
found_object.o: $(INC_PATH)/found_object.hpp
topic.o: $(INC_PATH)/topic.hpp
roi.o: $(INC_PATH)/roi.hpp
server.o: $(INC_PATH)/server.hpp $(INC_PATH)/tcp_server.hpp
utest.o: $(INC_PATH)/server.hpp
