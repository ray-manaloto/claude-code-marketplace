#include <aggregated_research/core.hpp>

#include <climits>
#include <cstdio>
#include <cstring>

#if defined(__clang__)
#if __has_feature(reflection)
#error Reflection flags must remain private to the core implementation.
#endif
#elif defined(__cpp_impl_reflection)
#error Reflection flags must remain private to the core implementation.
#endif

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    const auto probe = aggregated_research::reflection_probe();
    if (probe.value != 43 || probe.member_count != 1) return 3;
    std::printf("reflection value=%d, members=%u\n", probe.value, probe.member_count);
    std::fflush(stdout);
    const bool clean = std::strcmp(argv[1], "clean") == 0;
    if (clean || std::strcmp(argv[1], "memory") == 0) {
        auto* allocation = new int[4]{0, 0, 0, 0};
        volatile int* values = allocation;
        volatile int index = clean ? 3 : 4;
        volatile int value = values[index];
        delete[] allocation;
        if (!clean || value != 0) return 4;
    }
    if (clean || std::strcmp(argv[1], "overflow") == 0) {
        volatile int value = clean ? INT_MAX - 1 : INT_MAX;
        volatile int result = value + 1;
        return result == INT_MAX ? 0 : 4;
    }
    return 2;
}
