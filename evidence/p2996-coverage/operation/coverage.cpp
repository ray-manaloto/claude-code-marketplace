#define main coverage_reflection_main
#include "p2996_reflection.cpp"
#undef main

extern "C" int coverage_branch(bool take) {
  if (take)
    return 7;
  return 9;
}

int main() {
  return coverage_reflection_main()
       + coverage_branch(true) + coverage_branch(false) - 16;
}
