#pragma once

#include <cstdint>

namespace aggregated_research {

// Foundation witness only; no research provider or adapter behavior is exposed yet.
struct ReflectionProbe {
    std::int32_t value;
    std::uint32_t member_count;
};

[[nodiscard]] ReflectionProbe reflection_probe() noexcept;

}  // namespace aggregated_research
