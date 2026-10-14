#include <cfloat>
#include <cmath>
#ifndef INFINITY
#error MISSING_INFINITY
#endif
#ifndef NAN
#error MISSING_NAN
#endif
static_assert(__is_same(decltype(INFINITY), float));
static_assert(__is_same(decltype(NAN), float));
static_assert(__builtin_isinf(INFINITY) && INFINITY > 0);
static_assert(__builtin_isnan(NAN));
