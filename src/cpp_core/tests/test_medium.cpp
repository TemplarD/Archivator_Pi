#include <iostream>
#include <chrono>
#include <iomanip>
#include <vector>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🧪 ТЕСТ ОПТИМИЗАЦИИ НА СРЕДНИХ НАБОРАХ (30K-200K)" << std::endl;
    std::cout << "=============================================" << std::endl;
    
    // Реалистичные наборы цифр
    std::vector<std::pair<int, std::string>> test_cases = {
        {30000, "30K цифр"},
        {50000, "50K цифр"},
        {100000, "100K цифр"},
        {150000, "150K цифр"},
        {200000, "200K цифр"}
    };
    
    std::vector<long> universal_times;
    std::vector<long> original_times;
    std::vector<long> optimized_times;
    
    for (auto& test_case : test_cases) {
        int precision = test_case.first;
        std::string description = test_case.second;
        
        std::cout << "\n🔸 " << description << ":" << std::endl;
        
        // Тестируем оригинал
        std::cout << "  Оригинал: ";
        std::cout.flush();
        
        auto start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_original(precision);
        std::string pi_original = calc_original.compute_pi(16);
        auto end = std::chrono::high_resolution_clock::now();
        auto time_original = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        original_times.push_back(time_original);
        
        // Тестируем оптимизированную версию
        std::cout << time_original << " ms -> Оптимизированный: ";
        std::cout.flush();
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_optimized(precision);
        std::string pi_optimized = calc_optimized.compute_pi_optimized(16);
        end = std::chrono::high_resolution_clock::now();
        auto time_optimized = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        optimized_times.push_back(time_optimized);
        
        // Тестируем универсальную версию
        std::cout << time_optimized << " ms -> Universal: ";
        std::cout.flush();
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_universal(precision);
        std::string pi_universal = calc_universal.compute_pi_universal(16);
        end = std::chrono::high_resolution_clock::now();
        auto time_universal = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        universal_times.push_back(time_universal);
        
        // Проверяем корректность
        bool is_correct = (pi_original == pi_optimized && pi_optimized == pi_universal);
        
        double speedup_optimized = (double)time_original / time_optimized;
        double speedup_universal = (double)time_original / time_universal;
        
        std::cout << time_universal << " ms (" << std::fixed << std::setprecision(2) 
                  << speedup_optimized << "x / " << speedup_universal << "x) " 
                  << (is_correct ? "✅" : "❌") << std::endl;
        
        // Показываем стратегию
        std::cout << "  Стратегия Universal: ";
        if (precision <= 100000) {
            std::cout << "Оптимизированная версия";
        } else if (precision <= 1000000) {
            std::cout << "Смешанная стратегия";
        } else {
            std::cout << "Стратегия для больших объемов";
        }
        std::cout << std::endl;
    }
    
    // Детальный анализ
    std::cout << "\n🎯 ДЕТАЛЬНЫЙ АНАЛИЗ ОПТИМИЗАЦИИ" << std::endl;
    std::cout << "=================================" << std::endl;
    
    std::cout << "\n📊 СРАВНЕНИЕ ВСЕХ МЕТОДОВ:" << std::endl;
    std::cout << "Цифр  | Оригинал | Оптимиз. | Universal | Ускорение Opt/Uni" << std::endl;
    std::cout << "------|----------|----------|-----------|------------------" << std::endl;
    
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double speedup_optimized = (double)original_times[i] / optimized_times[i];
        double speedup_universal = (double)original_times[i] / universal_times[i];
        
        std::cout << std::setw(5) << test_cases[i].second.substr(0, 4) << " | "
                  << std::setw(8) << original_times[i] << " | "
                  << std::setw(8) << optimized_times[i] << " | "
                  << std::setw(9) << universal_times[i] << " | "
                  << std::setw(7) << std::fixed << std::setprecision(2) << speedup_optimized 
                  << "x/" << std::setw(4) << speedup_universal << "x" << std::endl;
    }
    
    // Находим лучшие результаты
    double best_optimized = 0, best_universal = 0;
    std::string best_opt_case = "", best_uni_case = "";
    
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double speedup_optimized = (double)original_times[i] / optimized_times[i];
        double speedup_universal = (double)original_times[i] / universal_times[i];
        
        if (speedup_optimized > best_optimized) {
            best_optimized = speedup_optimized;
            best_opt_case = test_cases[i].second;
        }
        
        if (speedup_universal > best_universal) {
            best_universal = speedup_universal;
            best_uni_case = test_cases[i].second;
        }
    }
    
    std::cout << "\n🚀 ЛУЧШИЕ РЕЗУЛЬТАТЫ:" << std::endl;
    std::cout << "   Оптимизированный: " << best_optimized << "x на " << best_opt_case << std::endl;
    std::cout << "   Universal: " << best_universal << "x на " << best_uni_case << std::endl;
    
    // Анализ масштабируемости
    std::cout << "\n📈 МАСШТАБИРУЕМОСТЬ (относительно 30K):" << std::endl;
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double scaling_opt = (double)optimized_times[i] / optimized_times[0];
        double scaling_uni = (double)universal_times[i] / universal_times[0];
        double scaling_orig = (double)original_times[i] / original_times[0];
        
        std::cout << "🔸 " << test_cases[i].second << ": "
                  << "Оригинал " << std::fixed << std::setprecision(1) << scaling_orig << "x, "
                  << "Оптимиз. " << scaling_opt << "x, "
                  << "Universal " << scaling_uni << "x" << std::endl;
    }
    
    // Эффективность по времени на цифру
    std::cout << "\n⏱️ ВРЕМЯ НА 1000 ЦИФР (мс):" << std::endl;
    for (size_t i = 0; i < test_cases.size(); ++i) {
        double time_per_1k_original = (double)original_times[i] / (test_cases[i].first / 1000);
        double time_per_1k_optimized = (double)optimized_times[i] / (test_cases[i].first / 1000);
        double time_per_1k_universal = (double)universal_times[i] / (test_cases[i].first / 1000);
        
        std::cout << "🔸 " << test_cases[i].second << ": "
                  << "Оригинал " << std::fixed << std::setprecision(2) << time_per_1k_original << "мс, "
                  << "Оптимиз. " << time_per_1k_optimized << "мс, "
                  << "Universal " << time_per_1k_universal << "мс" << std::endl;
    }
    
    std::cout << "\n✅ ТЕСТИРОВАНИЕ СРЕДНИХ НАБОРОВ ЗАВЕРШЕНО!" << std::endl;
    
    return 0;
}
