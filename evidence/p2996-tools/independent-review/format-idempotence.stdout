#if !__has_feature(reflection)
#error "P2996 reflection requires -freflection"
#else
#include <iostream>
#include <meta>
#include <stdexcept>
#include <string>
#include <type_traits>

static_assert(_LIBCPP_VERSION == 210000);
static_assert(__cplusplus > 202302L);
struct Record {
  int value;
};
constexpr auto member = std::meta::nonstatic_data_members_of(
    ^^Record, std::meta::access_context::current())[0];
static_assert(std::meta::identifier_of(member) == "value");
static_assert(std::is_same_v<typename[:std::meta::type_of(member):], int>);

int main() {
  Record record{42};
  record.[:member:] += 1;
  const std::string message =
      std::string("reflection value=") + std::to_string(record.[:member:]);
  try {
    throw std::runtime_error(message);
  } catch (const std::exception &error) {
    if (std::string(error.what()) != message)
      return 2;
    std::cout << error.what() << " exception=ok\n";
  }
  return record.value == 43 ? 0 : 1;
}
#endif
