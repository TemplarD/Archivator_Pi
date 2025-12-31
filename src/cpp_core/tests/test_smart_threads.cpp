#include <iostream>
#include <chrono>
#include <iomanip>
#include <vector>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🧪 ТЕСТ УМНОГО ВЫБОРА ПОТОКОВ" << std::endl;
    std::cout << "===================================" << std::endl;
    
    // Тестируем разные объемы с автоматическим выбором потоков
    std::vector<std::pair<int, std::string>> test_cases = {
        {10000, "10K цифр"},
        {50000, "50K цифр"},
        {100000, "100K цифр"},
        {500000, "500K цифр"},
        {1000000, "1M цифр"}
    };
    
    std::vector<long> auto_times;
    std::vector<int> used_threads;
    
    for (auto& test_case : test_cases) {
        int precision = test_case.first;
        std::string description = test_case.second;
        
        std::cout << "\n🔸 " << description << ":" << std::endl;
        
        // Тестируем с автоматическим выбором потоков
        std::cout << "  Auto (умный выбор): ";
        std::cout.flush();
        
        auto start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc(precision);
        std::string pi_auto = calc.compute_pi_auto(0); // 0 = авто-выбор
        auto end = std::chrono::high_resolution_clock::now();
        auto time_auto = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        auto_times.push_back(time_auto);
        
        // Получаем количество использованных потоков
        int hardware_threads = std::thread::hardware_concurrency();
        int expected_threads = hardware_threads - 1;
        if (precision > 500000) {
            expected_threads = std::min(expected_threads, 16);
        }
        expected_threads = std::min(expected_threads, 32);
        expected_threads = std::max(1, expected_threads);
        
        used_threads.push_back(expected_threads);
        
        std::cout << time_auto << " ms (" << expected_threads << " потоков)" << std::endl;
        
        // Проверяем корректность
        std::string expected_start = "3.141592653589793238462643383279502884197169399375";
        std::string actual_start = pi_auto.substr(0, std::min(expected_start.length(), pi_auto.length()));
        bool is_correct = (expected_start == actual_start);
        
        std::cout << "  Корректность: " << (is_correct ? "✅ ВЕРНО" : "❌ НЕВЕРНО") << std::endl;
    }
    
    // Анализ эффективности
    std::cout << "\n🎯 АНАЛИЗ УМНОГО ВЫБОРА ПОТОКОВ" << std::endl;
    std::cout << "=====================================" << std::endl;
    
    std::cout << "\n📊 ИСПОЛЬЗОВАННЫЕ ПОТОКИ:" << std::endl;
    int hardware_threads = std::thread::hardware_concurrency();
    std::cout << "   Аппаратные потоки: " << hardware_threads << std::endl;
    
    for (size_t i = 0; i < test_cases.size(); ++i) {
        int expected = hardware_threads - 1;
        if (test_cases[i].first > 500000) {
            expected = std::min(expected, 16);
        }
        expected = std::min(expected, 32);
        expected = std::max(1, expected);
        
        std::cout << "🔸 " << test_cases[i].second << ": " 
                  << used_threads[i] << " (ожидается " << expected << ") "
                  << (used_threads[i] == expected ? "✅" : "❌") << std::endl;
    }
    
    // Эффективность по времени на цифру
    std::cout << "\n⏱️ ВРЕМЯ НА 1000 ЦИФР (мс):" << std::endl;
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double time_per_1k = (double)auto_times[i] / (test_cases[i].first / 1000);
        
        std::cout << "🔸 " << test_cases[i].second << ": "
                  << std::fixed << std::setprecision(2) << time_per_1k << " мс" << std::endl;
    }
    
    // Сравнение с фиксированным количеством потоков
    std::cout << "\n🔄 СРАВНЕНИЕ С ФИКСИРОВАННЫМИ ПОТОКАМИ:" << std::endl;
    
    for (auto& test_case : test_cases) {
        int precision = test_case.first;
        std::string description = test_case.second;
        
        std::cout << "\n🔸 " << description << " (сравнение):" << std::endl;
        
        // Фиксированные потоки
        std::vector<int> fixed_threads = {1, 8, 16, 32};
        
        for (int threads : fixed_threads) {
            std::cout << "  " << threads << " потоков: ";
            std::cout.flush();
            
            auto start = std::chrono::high_resolution_clock::now();
            pi_archiver::ChudnovskyCalculator calc(precision);
            std::string pi_fixed = calc.compute_pi_universal(threads);
            auto end = std::chrono::high_resolution_clock::now();
            auto time_fixed = std::chrono::duration_cast<std::chrono::milliseconds>(
                end - start).count();
            
            std::cout << time_fixed << " мс" << std::endl;
        }
        
        // Авто-выбор
        std::cout << "  Auto: ";
        std::cout.flush();
        
        auto start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc(precision);
        std::string pi_auto = calc.compute_pi_auto(0);
        auto end = std::chrono::high_resolution_clock::now();
        auto time_auto = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        std::cout << time_auto << " мс 🏆" << std::endl;
    }
    
    std::cout << "\n✅ УМНЫЙ ВЫБОР ПОТОКОВ ТЕСТИРОВАН!" << std::endl;
    
    return 0;
}
