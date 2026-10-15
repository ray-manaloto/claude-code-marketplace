add_test(nonzero "/bin/sh" "-c" [=[printf 'reflection value=43, members=1\n'; exit 1]=])
set_tests_properties(nonzero PROPERTIES TIMEOUT 10)
