#include <aggregated_research/core.hpp>

#if defined(RESEARCH_CORE_WITH_FMT)
#include <fmt/format.h>
#include <cstdio>
#else
#include <iostream>
#endif

#if defined(__clang__)
#if __has_feature(reflection)
#error Reflection implementation flags must not leak through the public interface.
#endif
#elif defined(__cpp_impl_reflection)
#error Reflection implementation flags must not leak through the public interface.
#endif

int main() {
    const auto result = aggregated_research::reflection_probe();
#if defined(RESEARCH_CORE_WITH_FMT)
    const auto text = fmt::format("reflection value={}, members={}\n", result.value, result.member_count);
    std::fputs(text.c_str(), stdout);
#else
    std::cout << "reflection value=" << result.value
              << ", members=" << result.member_count << '\n';
#endif
    return result.value == 43 && result.member_count == 1 ? 0 : 1;
}
