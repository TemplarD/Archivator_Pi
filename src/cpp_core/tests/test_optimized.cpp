#include <iostream>
#include <chrono>
#include <vector>
#include <iomanip>
#include <fstream>
#include "optimized_calculator.h"

int main() {
    std::cout << "🧪 ТЕСТ ОПТИМИЗИРОВАННОГО C++ CORE" << std::endl;
    std::cout << "===================================" << std::endl;
    
    int precision = 100000;
    std::vector<int> thread_counts = {1, 8, 16, 24, 32, 39};
    std::vector<long> optimized_times;
    std::vector<long> original_times;
    
    std::cout << "\n📊 СРАВНЕНИЕ ОРИГИНАЛА VS ОПТИМИЗАЦИИ (100,000 цифр)" << std::endl;
    std::cout << "=================================================" << std::endl;
    
    for (int threads : thread_counts) {
        // Тестируем оригинальную версию
        std::cout << "\n🔸 " << threads << " потоков (оригинал): ";
        std::cout.flush();
        
        auto start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_original(precision);
        std::string pi_original = calc_original.compute_pi(threads);
        auto end = std::chrono::high_resolution_clock::now();
        auto time_original = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        original_times.push_back(time_original);
        
        // Тестируем оптимизированную версию
        std::cout << time_original << " ms -> ";
        std::cout.flush();
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::OptimizedChudnovskyCalculator calc_optimized(precision);
        std::string pi_optimized = calc_optimized.compute_pi_optimized(threads);
        end = std::chrono::high_resolution_clock::now();
        auto time_optimized = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        optimized_times.push_back(time_optimized);
        
        // Проверяем корректность
        bool is_correct = (pi_original == pi_optimized);
        
        double speedup = (double)time_original / time_optimized;
        std::cout << time_optimized << " ms (" << std::fixed << std::setprecision(2) 
                  << speedup << "x ускорение) " << (is_correct ? "✅" : "❌") << std::endl;
    }
    
    // Сохраняем результат
    pi_archiver::OptimizedChudnovskyCalculator calc_final(precision);
    std::string pi_final = calc_final.compute_pi_optimized(39);
    
    std::ofstream file("pi_100k_optimized.txt");
    if (file.is_open()) {
        file << pi_final;
        file.close();
        std::cout << "\n💾 Оптимизированный результат сохранен в pi_100k_optimized.txt" << std::endl;
    }
    
    // Анализ результатов
    std::cout << "\n🎯 АНАЛИЗ ОПТИМИЗАЦИИ" << std::endl;
    std::cout << "========================" << std::endl;
    
    std::cout << "\n📊 СРАВНЕНИЕ ВРЕМЕНИ:" << std::endl;
    for (size_t i = 0; i < thread_counts.size(); ++i) {
        double improvement = (double)original_times[i] / optimized_times[i];
        std::cout << "🔸 " << thread_counts[i] << " потоков: " 
                  << original_times[i] << " ms -> " << optimized_times[i] << " ms ("
                  << std::fixed << std::setprecision(2) << improvement << "x)" << std::endl;
    }
    
    // Находим лучшее улучшение
    double best_improvement = 0;
    int best_threads = 1;
    for (size_t i = 0; i < thread_counts.size(); ++i) {
        double improvement = (double)original_times[i] / optimized_times[i];
        if (improvement > best_improvement) {
            best_improvement = improvement;
            best_threads = thread_counts[i];
        }
    }
    
    std::cout << "\n🚀 ЛУЧШЕЕ УЛУЧШЕНИЕ: " << best_improvement << "x на " << best_threads << " потоках" << std::endl;
    
    std::cout << "\n✅ ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!" << std::endl;
    
    return 0;
}
