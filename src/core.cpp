#include <aggregated_research/core.hpp>

#include <meta>
#include <type_traits>

#if defined(__clang__)
#if !__has_feature(reflection) || !defined(_LIBCPP_VERSION) || _LIBCPP_VERSION != 210000
#error Reflection requires the qualified P2996 compiler and libc++.
#endif
#elif !defined(__cpp_impl_reflection) || !defined(__cpp_lib_reflection)
#error Reflection must be enabled in the compiler and standard library.
#endif

namespace aggregated_research {
namespace {
struct Record { std::int32_t value; };
constexpr auto member = std::meta::nonstatic_data_members_of(
    ^^Record, std::meta::access_context::current())[0];
constexpr auto member_count = std::meta::nonstatic_data_members_of(
    ^^Record, std::meta::access_context::current()).size();
static_assert(member_count == 1);
static_assert(std::meta::identifier_of(member) == "value");
static_assert(std::is_same_v<typename [:std::meta::type_of(member):], std::int32_t>);
static_assert(std::is_trivially_default_constructible_v<ReflectionProbe>);
static_assert(std::is_trivially_copyable_v<ReflectionProbe>);
static_assert(std::is_standard_layout_v<ReflectionProbe>);
}  // namespace

ReflectionProbe reflection_probe() noexcept {
    Record record{42};
    record.[:member:] += 1;
    return {record.[:member:], static_cast<std::uint32_t>(member_count)};
}
}  // namespace aggregated_research
