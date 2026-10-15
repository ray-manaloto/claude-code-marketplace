#include <stdexcept>
int probe(); int main() { return probe() == 42 ? 0 : 1; }
