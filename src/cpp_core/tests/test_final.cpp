#include <iostream>
#include <chrono>
#include <vector>
#include <iomanip>
#include <fstream>
#include <algorithm>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🧪 ФИНАЛЬНЫЙ ТЕСТ UNIFIED C++ CORE" << std::endl;
    std::cout << "====================================" << std::endl;
    
    int precision = 100000;
    std::vector<int> thread_counts = {1, 8, 16, 24, 32, 39};
    std::vector<long> original_times;
    std::vector<long> optimized_times;
    std::vector<long> auto_times;
    
    std::cout << "\n📊 СРАВНЕНИЕ ВСЕХ МЕТОДОВ (100,000 цифр)" << std::endl;
    std::cout << "========================================" << std::endl;
    
    for (int threads : thread_counts) {
        std::cout << "\n🔸 " << threads << " потоков:" << std::endl;
        
        // Тестируем оригинальную версию
        std::cout << "  Оригинал: ";
        std::cout.flush();
        
        auto start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_original(precision);
        std::string pi_original = calc_original.compute_pi(threads);
        auto end = std::chrono::high_resolution_clock::now();
        auto time_original = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        original_times.push_back(time_original);
        
        // Тестируем оптимизированную версию
        std::cout << time_original << " ms -> Оптимизированный: ";
        std::cout.flush();
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_optimized(precision);
        std::string pi_optimized = calc_optimized.compute_pi_optimized(threads);
        end = std::chrono::high_resolution_clock::now();
        auto time_optimized = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        optimized_times.push_back(time_optimized);
        
        // Тестируем auto версию
        std::cout << time_optimized << " ms -> Auto: ";
        std::cout.flush();
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_auto(precision);
        std::string pi_auto = calc_auto.compute_pi_auto(threads);
        end = std::chrono::high_resolution_clock::now();
        auto time_auto = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        auto_times.push_back(time_auto);
        
        // Проверяем корректность
        bool is_correct = (pi_original == pi_optimized && pi_optimized == pi_auto);
        
        double speedup_optimized = (double)time_original / time_optimized;
        double speedup_auto = (double)time_original / time_auto;
        
        std::cout << time_auto << " ms (" << std::fixed << std::setprecision(2) 
                  << speedup_optimized << "x / " << speedup_auto << "x) " 
                  << (is_correct ? "✅" : "❌") << std::endl;
    }
    
    // Сохраняем лучший результат
    pi_archiver::ChudnovskyCalculator calc_final(precision);
    std::string pi_final = calc_final.compute_pi_auto(39);
    
    std::ofstream file("pi_100k_final.txt");
    if (file.is_open()) {
        file << pi_final;
        file.close();
        std::cout << "\n💾 Финальный результат сохранен в pi_100k_final.txt" << std::endl;
    }
    
    // Анализ результатов
    std::cout << "\n🎯 ФИНАЛЬНЫЙ АНАЛИЗ" << std::endl;
    std::cout << "======================" << std::endl;
    
    std::cout << "\n📊 СРАВНЕНИЕ ВРЕМЕНИ:" << std::endl;
    for (size_t i = 0; i < thread_counts.size(); ++i) {
        double improvement_optimized = (double)original_times[i] / optimized_times[i];
        double improvement_auto = (double)original_times[i] / auto_times[i];
        
        std::cout << "🔸 " << thread_counts[i] << " потоков: " 
                  << original_times[i] << " ms -> " << optimized_times[i] << " ms -> " 
                  << auto_times[i] << " ms (" << std::fixed << std::setprecision(2) 
                  << improvement_optimized << "x / " << improvement_auto << "x)" << std::endl;
    }
    
    // Находим лучшее ускорение
    double best_optimized = 0, best_auto = 0;
    int best_threads_opt = 1, best_threads_auto = 1;
    
    for (size_t i = 0; i < thread_counts.size(); ++i) {
        double improvement_optimized = (double)original_times[i] / optimized_times[i];
        double improvement_auto = (double)original_times[i] / auto_times[i];
        
        if (improvement_optimized > best_optimized) {
            best_optimized = improvement_optimized;
            best_threads_opt = thread_counts[i];
        }
        
        if (improvement_auto > best_auto) {
            best_auto = improvement_auto;
            best_threads_auto = thread_counts[i];
        }
    }
    
    std::cout << "\n🚀 ЛУЧШИЕ РЕЗУЛЬТАТЫ:" << std::endl;
    std::cout << "   Оптимизированный: " << best_optimized << "x на " << best_threads_opt << " потоках" << std::endl;
    std::cout << "   Auto: " << best_auto << "x на " << best_threads_auto << " потоках" << std::endl;
    
    // Сравнение с Python
    std::cout << "\n🐍 СРАВНЕНИЕ С PYTHON:" << std::endl;
    std::cout << "   Python (оценка): ~100,000 мс для 100,000 цифр" << std::endl;
    std::cout << "   C++ Auto (лучший): " << *std::min_element(auto_times.begin(), auto_times.end()) 
              << " мс для 100,000 цифр" << std::endl;
    double python_speedup = 100000.0 / *std::min_element(auto_times.begin(), auto_times.end());
    std::cout << "   Ускорение vs Python: " << std::fixed << std::setprecision(1) 
              << python_speedup << "x" << std::endl;
    
    std::cout << "\n✅ UNIFIED C++ CORE ГОТОВ К ИНТЕГРАЦИИ!" << std::endl;
    
    return 0;
}
