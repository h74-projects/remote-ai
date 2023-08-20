#include "mu_test.h"

#include <string>
#include <climits>

#include "classes_under_test.hpp"

BEGIN_TEST(_equality_on_integers)
	int a = 42;
	size_t s = 43;

	ASSERT_EQUAL(a, 42);
	ASSERT_EQUAL(s, 43);
	ASSERT_EQUAL(s, static_cast<size_t>(a) );

	int n = 42;
	long m = 42;

	ASSERT_EQUAL(n, m);
END_TEST

BEGIN_TEST(add_operations)
	int n = 42;
	int r = n++;

	ASSERT_EQUAL(n, 43);
	ASSERT_EQUAL(r, n-1);
END_TEST

BEGIN_TEST(abs_function)
	int n[] = {0, 2, 42, INT_MAX, -2, -42, -INT_MAX, INT_MIN};

	for(size_t i = 0; i < sizeof(n)/sizeof(*n); ++i){
		int abs_val = abs(n[i]);
		TRACE(n[i]);
		TRACE(abs_val);
		ASSERT_THAT( abs_val >= 0);
	}

END_TEST

BEGIN_TEST(empty_class_is_not_empty)
	class K{};

	ASSERT_THAT(sizeof(K) != 0);

	ASSERT_NOT_EQUAL(sizeof(K), 0);
	ASSERT_EQUAL(sizeof(K), 1);
END_TEST

BEGIN_TEST(default_string_is_empty)
	std::string s;

	ASSERT_THAT(s.size() == 0);
	ASSERT_EQUAL_STR(s.c_str(), "");
	ASSERT_THAT(s == "");
END_TEST

BEGIN_TEST(string_equality)
	const char* cstr = "abc";
	std::string s(cstr);
	ASSERT_EQUAL(s, cstr);

	std::string t;

	ASSERT_NOT_EQUAL(s, t);
	t = s;
	ASSERT_EQUAL(s, t);
END_TEST

BEGIN_TEST(tracers)
	TRACER << "hello world" << '\n';
	short mayo = 42;
	TRACE(mayo);

	double burger = 3.14;
	TRACER << "short " << mayo << " and a double " << burger << '\n';
	ASSERT_EQUAL(mayo, 42);
END_TEST


BEGIN_TEST(test_equal_on_classes)
	Ball small(5);
	Ball large(100);

	TRACE(small);
	TRACER << "balls " << small << " and " << large << '\n';
	TRACE(large);

	ASSERT_THAT(small == small);
	ASSERT_EQUAL(small, small);

	ASSERT_THAT(small != large);
	ASSERT_NOT_EQUAL(small, large);

	TRACER << "scaling small by 20\n";
	small.scale(20);
	TRACE(small);
	ASSERT_EQUAL(small, large);
END_TEST

BEGIN_TEST(access_null_ptr_will_seg)
	int * p = 0;
	ASSERT_EQUAL(p, 0);
	// next line will blow the segment
	ASSERT_EQUAL(*p, 42);
END_TEST

BEGIN_TEST(throw_ball)
	throw Ball(-2);
	ASSERT_THAT(false);
END_TEST

BEGIN_TEST(throw_std_ball_excpetion)
	throw BallException();
	ASSERT_THAT(false);
END_TEST

BEGIN_TEST(test_should_fail)
	ASSERT_FAIL("fail on demand");
END_TEST

BEGIN_TEST(test_should_pass)
	ASSERT_PASS();
END_TEST


BEGIN_TEST(test_with_no_assert_should_fail)
	const char *some = "hello";
	TRACE(some);
END_TEST

TEST_SUITE(因果応報 [inga ōhō: bad causes bring bad results])
	IGNORE_TEST(_equality_on_integers)
	TEST(add_operations)
	TEST(abs_function)

	TEST(empty_class_is_not_empty)
	TEST(default_string_is_empty)
	TEST(string_equality)

	TEST(tracers)
	TEST(test_equal_on_classes)

	TEST(access_null_ptr_will_seg)

	TEST(throw_ball)
	TEST(throw_std_ball_excpetion)

	IGNORE_TEST(test_should_fail)
	IGNORE_TEST(test_should_pass)

	TEST(test_with_no_assert_should_fail)
END_SUITE
