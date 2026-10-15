#include <aggregated_research/core.hpp>

#include <iostream>

#if defined(__clang__)
#if __has_feature(reflection)
#error Reflection implementation flags must not leak through the public interface.
#endif
#elif defined(__cpp_impl_reflection)
#error Reflection implementation flags must not leak through the public interface.
#endif

int main() {
    const auto result = aggregated_research::reflection_probe();
    std::cout << "reflection value=" << result.value
              << ", members=" << result.member_count << '\n';
    return result.value == 43 && result.member_count == 1 ? 0 : 1;
}
