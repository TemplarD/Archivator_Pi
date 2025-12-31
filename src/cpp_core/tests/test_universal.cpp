#include <iostream>
#include <chrono>
#include <iomanip>
#include <vector>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🧪 ТЕСТ УНИВЕРСАЛЬНОЙ ОПТИМИЗАЦИИ" << std::endl;
    std::cout << "==================================" << std::endl;
    
    // Тестируем разные объемы
    std::vector<std::pair<int, std::string>> test_cases = {
        {10000, "10K цифр"},
        {100000, "100K цифр"},
        {1000000, "1M цифр"}
    };
    
    std::vector<long> universal_times;
    std::vector<long> original_times;
    
    for (auto& test_case : test_cases) {
        int precision = test_case.first;
        std::string description = test_case.second;
        
        std::cout << "\n🔸 " << description << ":" << std::endl;
        
        // Тестируем универсальную оптимизацию
        std::cout << "  Universal: ";
        std::cout.flush();
        
        auto start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_universal(precision);
        std::string pi_universal = calc_universal.compute_pi_universal(39);
        auto end = std::chrono::high_resolution_clock::now();
        auto time_universal = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        universal_times.push_back(time_universal);
        
        // Тестируем оригинал для сравнения
        std::cout << time_universal << " ms -> Оригинал: ";
        std::cout.flush();
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_original(precision);
        std::string pi_original = calc_original.compute_pi(39);
        end = std::chrono::high_resolution_clock::now();
        auto time_original = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        original_times.push_back(time_original);
        
        // Проверяем корректность
        bool is_correct = (pi_universal == pi_original);
        
        double speedup = (double)time_original / time_universal;
        
        std::cout << time_original << " ms (" << std::fixed << std::setprecision(2) 
                  << speedup << "x) " << (is_correct ? "✅" : "❌") << std::endl;
        
        // Выводим стратегию
        std::cout << "  Стратегия: ";
        if (precision <= 100000) {
            std::cout << "Оптимизированная версия";
        } else if (precision <= 1000000) {
            std::cout << "Смешанная стратегия";
        } else {
            std::cout << "Стратегия для больших объемов";
        }
        std::cout << std::endl;
    }
    
    // Анализ результатов
    std::cout << "\n🎯 АНАЛИЗ УНИВЕРСАЛЬНОЙ ОПТИМИЗАЦИИ" << std::endl;
    std::cout << "=====================================" << std::endl;
    
    std::cout << "\n📊 СРАВНЕНИЕ ВРЕМЕНИ:" << std::endl;
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double improvement = (double)original_times[i] / universal_times[i];
        
        std::cout << "🔸 " << test_cases[i].second << ": " 
                  << original_times[i] << " ms -> " << universal_times[i] << " ms (" 
                  << std::fixed << std::setprecision(2) << improvement << "x)" << std::endl;
    }
    
    // Находим лучшее ускорение
    double best_improvement = 0;
    std::string best_case = "";
    
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double improvement = (double)original_times[i] / universal_times[i];
        
        if (improvement > best_improvement) {
            best_improvement = improvement;
            best_case = test_cases[i].second;
        }
    }
    
    std::cout << "\n🚀 ЛУЧШИЙ РЕЗУЛЬТАТ: " << best_improvement << "x на " << best_case << std::endl;
    
    // Проверяем масштабируемость
    std::cout << "\n📈 МАСШТАБИРУЕМОСТЬ:" << std::endl;
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double scaling = (double)universal_times[i] / universal_times[0];
        std::cout << "🔸 " << test_cases[i].second << ": " << std::fixed << std::setprecision(1) 
                  << scaling << "x медленнее 10K" << std::endl;
    }
    
    std::cout << "\n✅ УНИВЕРСАЛЬНАЯ ОПТИМИЗАЦИЯ ТЕСТИРОВАНА!" << std::endl;
    
    return 0;
}
