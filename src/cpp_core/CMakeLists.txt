cmake_minimum_required(VERSION 3.12)
project(pi_archiver_core VERSION 1.0.0 LANGUAGES CXX)

# Установка стандартов C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Опции компиляции
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -mtune=native")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")

# Поиск библиотек
find_package(PkgConfig REQUIRED)

# GMP (стандартная библиотека высокоточных вычислений)
find_path(GMP_INCLUDE_DIR gmp.h)
find_library(GMP_LIBRARY gmp)

# MPFR (библиотека вещественных чисел)
find_path(MPFR_INCLUDE_DIR mpfr.h)
find_library(MPFR_LIBRARY mpfr)

# Проверяем что библиотеки найдены
if(NOT GMP_INCLUDE_DIR OR NOT GMP_LIBRARY)
    message(FATAL_ERROR "GMP library not found. Install libgmp-dev")
endif()

if(NOT MPFR_INCLUDE_DIR OR NOT MPFR_LIBRARY)
    message(FATAL_ERROR "MPFR library not found. Install libmpfr-dev")
endif()

# Включаемые директории
include_directories(${GMP_INCLUDE_DIR} ${MPFR_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Источники
set(CORE_SOURCES
    src/chudnovsky_calculator.cpp
)

set(HEADERS
    include/chudnovsky_calculator.h
)

# Создаем статическую библиотеку
add_library(pi_archiver_core STATIC ${CORE_SOURCES})

# Линковка с библиотеками
target_link_libraries(pi_archiver_core 
    ${GMP_LIBRARY}
    ${MPFR_LIBRARY}
    pthread
)

# Установка
install(TARGETS pi_archiver_core
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(FILES ${HEADERS}
    DESTINATION include/pi_archiver
)

# Тесты
option(BUILD_TESTS "Build tests" ON)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
    
    # Оптимизированный тест (только в основном CMakeLists.txt)
    add_executable(test_optimized tests/test_optimized.cpp)
    target_link_libraries(test_optimized pi_archiver_core gmp mpfr)
    
    # Финальный unified тест
    add_executable(test_final tests/test_final.cpp)
    target_link_libraries(test_final pi_archiver_core gmp mpfr)
    
    # Тест для 1 миллиона цифр
    add_executable(test_1M tests/test_1M.cpp)
    target_link_libraries(test_1M pi_archiver_core gmp mpfr)
    
    # Тест универсальной оптимизации
    add_executable(test_universal tests/test_universal.cpp)
    target_link_libraries(test_universal pi_archiver_core gmp mpfr)
    
    # Тест для средних наборов (30K-200K)
    add_executable(test_medium tests/test_medium.cpp)
    target_link_libraries(test_medium pi_archiver_core gmp mpfr)
    
    # Тест умного выбора потоков
    add_executable(test_smart_threads tests/test_smart_threads.cpp)
    target_link_libraries(test_smart_threads pi_archiver_core gmp mpfr)
    
    # Тест адаптивной системы потоков
    add_executable(test_adaptive tests/test_adaptive.cpp)
    target_link_libraries(test_adaptive pi_archiver_core gmp mpfr)
endif()

# Python биндинги
option(BUILD_PYTHON_BINDINGS "Build Python bindings" OFF)
if(BUILD_PYTHON_BINDINGS)
    find_package(pybind11 REQUIRED)
    pybind11_add_module(pi_core bindings/python_bindings.cpp)
    target_link_libraries(pi_core PRIVATE pi_archiver_core)
endif()

# Информация о сборке
message(STATUS "Pi Archiver Core Configuration:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
if(GMP_LIBRARY)
    message(STATUS "  GMP: ${GMP_LIBRARY}")
else()
    message(STATUS "  GMP: NOT FOUND")
endif()
if(MPFR_LIBRARY)
    message(STATUS "  MPFR: ${MPFR_LIBRARY}")
else()
    message(STATUS "  MPFR: NOT FOUND")
endif()
message(STATUS "  Compiler flags: ${CMAKE_CXX_FLAGS}")
