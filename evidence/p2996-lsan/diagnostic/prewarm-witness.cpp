#include <aggregated_research/core.hpp>

#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#if __has_feature(reflection)
#error Reflection flags must remain private to the core implementation.
#endif


extern "C" bool _dyld_get_shared_cache_uuid(unsigned char uuid[16]);
struct dyld_shared_cache_dylib_text_info;
extern "C" int dyld_shared_cache_iterate_text(const unsigned char uuid[16], void (^callback)(const dyld_shared_cache_dylib_text_info*));
static void prewarm_dyld() {
    unsigned char uuid[16] = {};
    if (_dyld_get_shared_cache_uuid(uuid)) {
        if (dyld_shared_cache_iterate_text(uuid, ^(const dyld_shared_cache_dylib_text_info*){}) != 0) std::abort();
    }
}

__attribute__((noinline)) void leak_allocation() {
    auto* bytes = static_cast<volatile unsigned char*>(std::malloc(64));
    if (bytes == nullptr) std::abort();
    bytes[0] = 43;
}

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    prewarm_dyld();
    const auto probe = aggregated_research::reflection_probe();
    if (probe.value != 43 || probe.member_count != 1) return 3;
    std::printf("reflection value=%d, members=%u\n", probe.value, probe.member_count);
    std::fflush(stdout);
    const bool clean = std::strcmp(argv[1], "clean") == 0;
    const bool leak = std::strcmp(argv[1], "leak") == 0;
    const bool overflow = std::strcmp(argv[1], "overflow") == 0;
    if (!clean && !leak && !overflow) return 2;
    if (leak) leak_allocation();
    if (clean || overflow) {
        volatile int value = clean ? INT_MAX - 1 : INT_MAX;
        volatile int result = value + 1;
        if (result != INT_MAX) return 4;
    }
    return 0;
}
