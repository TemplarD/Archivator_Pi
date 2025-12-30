# Тесты для Pi Archiver Core

# Тест Chudnovsky calculator
add_executable(test_chudnovsky test_chudnovsky.cpp)

# Линковка с основной библиотекой
target_link_libraries(test_chudnovsky 
    pi_archiver_core
    ${GMP_LIBRARY}
    ${MPFR_LIBRARY}
    pthread
)

# Добавляем тест в CTest
add_test(NAME ChudnovskyTest COMMAND test_chudnovsky)
