#include <meta>
#include <iostream>
#include <string>
#include <type_traits>

#if !defined(__cpp_impl_reflection) || !defined(__cpp_lib_reflection)
#error Reflection must be enabled in the compiler and standard library.
#endif

struct Record { int value; };
constexpr auto member = std::meta::nonstatic_data_members_of(
    ^^Record, std::meta::access_context::current())[0];
static_assert(std::meta::identifier_of(member) == "value");
static_assert(std::is_same_v<typename [:std::meta::type_of(member):], int>);
static_assert(__cplusplus > 202302L);

int main() {
    Record record{42};
    record.[:member:] += 1;
    // A nontrivial runtime string and stream also exercise the selected libstdc++.
    const std::string message = std::string("reflection value=")
        + std::to_string(record.[:member:]);
    std::cout << message << '\n';
    return record.value == 43 ? 0 : 1;
}
