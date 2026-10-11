#include <meta>
#include "value.h"

static_assert(std::meta::is_type(^^FixtureValue));

int main() {
  FixtureValue value{7};
  return value.value == 7 ? 0 : 1;
}
