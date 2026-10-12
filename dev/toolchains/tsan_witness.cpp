#include <aggregated_research/core.hpp>

#include <climits>
#include <cstdio>
#include <cstring>
#include <pthread.h>

#if __has_feature(reflection)
#error Reflection flags must remain private to the core implementation.
#endif

struct Shared {
    volatile int value;
};

void* write_value(void* argument) {
    static_cast<Shared*>(argument)->value = 1;
    return nullptr;
}

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    const auto probe = aggregated_research::reflection_probe();
    if (probe.value != 43 || probe.member_count != 1) return 3;
    std::printf("reflection value=%d, members=%u\n", probe.value, probe.member_count);
    std::fflush(stdout);
    const bool clean = std::strcmp(argv[1], "clean") == 0;
    if (clean || std::strcmp(argv[1], "race") == 0) {
        Shared shared{0};
        pthread_t worker;
        if (pthread_create(&worker, nullptr, write_value, &shared) != 0) return 4;
        if (!clean) shared.value = 2;
        if (pthread_join(worker, nullptr) != 0) return 4;
        if (!clean) return 4;
        shared.value = 2;
        if (shared.value != 2) return 4;
    }
    if (clean || std::strcmp(argv[1], "overflow") == 0) {
        volatile int value = clean ? INT_MAX - 1 : INT_MAX;
        volatile int result = value + 1;
        return result == INT_MAX ? 0 : 4;
    }
    return 2;
}
