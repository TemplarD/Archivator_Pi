#include <iostream>
#include <chrono>
#include <iomanip>
#include <vector>
#include <thread>
#include <atomic>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🧪 ТЕСТ УМНОЙ АДАПТИВНОЙ СИСТЕМЫ ПОТОКОВ" << std::endl;
    std::cout << "=============================================" << std::endl;
    
    // Ограничиваем до 200K цифр для тестов
    std::vector<std::pair<int, std::string>> test_cases = {
        {10000, "10K цифр"},
        {50000, "50K цифр"},
        {100000, "100K цифр"},
        {200000, "200K цифр"}
    };
    
    for (auto& test_case : test_cases) {
        int precision = test_case.first;
        std::string description = test_case.second;
        
        std::cout << "\n🔸 " << description << ":" << std::endl;
        
        // Тестируем умную адаптивную систему
        std::cout << "  Адаптивная система: ";
        std::cout.flush();
        
        auto start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc(precision);
        std::string pi_adaptive = calc.compute_pi_adaptive(0); // 0 = умный выбор
        auto end = std::chrono::high_resolution_clock::now();
        auto time_adaptive = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        std::cout << time_adaptive << " мс" << std::endl;
        
        // Показываем выбранную стратегию
        std::cout << "  Выбрано потоков: " << calc.get_used_threads() << std::endl;
        std::cout << "  Стратегия: " << calc.get_strategy() << std::endl;
        
        // Проверяем корректность
        std::string expected_start = "3.141592653589793238462643383279502884197169399375";
        std::string actual_start = pi_adaptive.substr(0, std::min(expected_start.length(), pi_adaptive.length()));
        bool is_correct = (expected_start == actual_start);
        
        std::cout << "  Корректность: " << (is_correct ? "✅ ВЕРНО" : "❌ НЕВЕРНО") << std::endl;
    }
    
    std::cout << "\n✅ АДАПТИВНАЯ СИСТЕМА ПОТОКОВ ТЕСТИРОВАНА!" << std::endl;
    
    return 0;
}
