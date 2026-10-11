#if __has_feature(reflection)
#error "Reflection must remain target-private"
#endif
#include <string>
int main() { return std::string("private").size() != 7; }
