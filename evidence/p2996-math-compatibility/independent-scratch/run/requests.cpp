#if REQUEST_FIRST
#define __need_infinity_nan
#include <float.h>
#if defined(__CLANG_FLOAT_H) || defined(_LIBCPP_FLOAT_H)
#error PREMATURE_FULL_GUARD
#endif
#endif
#include <float.h>
#ifndef FLT_MANT_DIG
#error MISSING_FULL_HEADER
#endif
#define __need_infinity_nan
#include <float.h>
#define __need_infinity_nan
#include <float.h>
#ifdef __need_infinity_nan
#error UNCONSUMED_REQUEST
#endif
static_assert(__builtin_isinf(INFINITY));
static_assert(__builtin_isnan(NAN));
