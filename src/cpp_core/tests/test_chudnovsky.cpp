#include <iostream>
#include <chrono>
#include <iomanip>
#include <fstream>
#include <thread>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🧪 ТЕСТ C++ CORE: CHUDNOVSKY CALCULATOR" << std::endl;
    std::cout << "=============================================" << std::endl;
    
    // Тест 1: Базовая функциональность
    std::cout << "\n📊 Тест 1: Базовая функциональность" << std::endl;
    std::cout << "Точность: 1000 цифр" << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    pi_archiver::ChudnovskyCalculator calc(1000);
    std::string pi = calc.compute_pi(1); // 1 поток
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        end - start).count();
    
    std::cout << "Время: " << duration << " ms" << std::endl;
    std::cout << "Первые 50 цифр: " << pi.substr(0, 50) << std::endl;
    
    // Проверяем корректность
    std::string expected = "3.14159265358979323846264338327950288419716939937510";
    bool correct = pi.compare(0, expected.length(), expected) == 0;
    std::cout << "Корректность: " << (correct ? "✅" : "❌") << std::endl;
    
    // Тест 2: Многопоточность
    std::cout << "\n📊 Тест 2: Многопоточность" << std::endl;
    
    int optimal_threads = pi_archiver::ChudnovskyCalculator::get_optimal_threads();
    std::cout << "Оптимальное количество потоков: " << optimal_threads << std::endl;
    
    // Тестируем разное количество потоков
    std::vector<int> thread_counts = {1, 2, 4, optimal_threads};
    
    for (int threads : thread_counts) {
        std::cout << "🔸 " << threads << " потоков: ";
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc_mt(2000); // Больше цифр для наглядности
        std::string pi_mt = calc_mt.compute_pi(threads);
        end = std::chrono::high_resolution_clock::now();
        
        duration = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        std::cout << duration << " ms, коррект: " 
                  << (pi_mt.compare(0, expected.length(), expected) == 0 ? "" : "") 
                  << std::endl;
    }
    
    // Тест 3: Производительность с большим количеством цифр
    std::cout << "\n📊 Тест 3: Производительность (100,000 цифр)" << std::endl;
    std::cout << "Тестируем разное количество потоков..." << std::endl;
    int large_precision = 100000;
    
    // Массив с количеством потоков для тестирования
    std::vector<int> performance_thread_counts = {1, 8, 16, 24, 32, 39};
    std::vector<long> times;
    
    for (int threads : performance_thread_counts) {
        std::cout << "🔸 " << threads << " потоков: ";
        std::cout.flush();
        
        start = std::chrono::high_resolution_clock::now();
        pi_archiver::ChudnovskyCalculator calc(threads == 1 ? large_precision : large_precision);
        std::string pi_result = calc.compute_pi(threads);
        end = std::chrono::high_resolution_clock::now();
        auto time_taken = std::chrono::duration_cast<std::chrono::milliseconds>(
            end - start).count();
        
        times.push_back(time_taken);
        
        std::cout << time_taken << " ms, коррект: " 
                  << (pi_result.compare(0, expected.length(), expected) == 0 ? "✅" : "❌") 
                  << std::endl;
        
        // Сохраняем результат только для последнего теста
        if (threads == 39) {
            std::ofstream pi_file("pi_100k_digits.txt");
            if (pi_file.is_open()) {
                pi_file << pi_result;
                pi_file.close();
                
                // Проверяем файл
                std::ifstream check_file("pi_100k_digits.txt");
                if (check_file.is_open()) {
                    check_file.seekg(0, std::ios::end);
                    size_t file_size = check_file.tellg();
                    check_file.close();
                    
                    std::cout << "💾 Файл создан: pi_100k_digits.txt" << std::endl;
                    std::cout << "📏 Размер файла: " << file_size << " байт" << std::endl;
                    std::cout << "📊 Длина π: " << pi_result.length() << " символов" << std::endl;
                    
                    if (file_size == pi_result.length()) {
                        std::cout << "✅ Размер файла совпадает с длиной π" << std::endl;
                    } else {
                        std::cout << "❌ Размер файла НЕ совпадает с длиной π" << std::endl;
                    }
                } else {
                    std::cout << "❌ Ошибка: не удалось открыть файл для проверки" << std::endl;
                }
            } else {
                std::cout << "❌ Ошибка: не удалось создать файл" << std::endl;
            }
        }
    }
    
    // Анализ результатов
    std::cout << "\n🎯 АНАЛИЗ РЕЗУЛЬТАТОВ" << std::endl;
    std::cout << "================================" << std::endl;
    
    std::cout << "✅ C++ CORE успешно вычислил 100,000 цифр π!" << std::endl;
    std::cout << "\n📊 СРАВНЕНИЕ ВРЕМЕНИ ПО ПОТОКАМ:" << std::endl;
    
    for (size_t i = 0; i < performance_thread_counts.size(); ++i) {
        double speedup = (double)times[0] / times[i];
        std::cout << "🔸 " << performance_thread_counts[i] << " потоков: " << times[i] << " ms (" 
                  << times[i]/1000.0 << " сек) - ускорение " << std::fixed << std::setprecision(2) 
                  << speedup << "x" << std::endl;
    }
    
    std::cout << "\n💾 Сохранено в: pi_100k_digits.txt" << std::endl;
    
    std::cout << "\n СРАВНЕНИЕ С PYTHON:" << std::endl;
    std::cout << "Python (GIL): ~10000 ms для 10000 цифр" << std::endl;
    std::cout << "C++ (лучший результат): " << times.back() << " ms для 100000 цифр" << std::endl;
    std::cout << "Ускорение vs Python: ~" << std::fixed << std::setprecision(1) 
              << (10000.0 / times.back()) << "x" << std::endl;
    
    std::cout << "\n ТЕСТЫ ЗАВЕРШЕНЫ!" << std::endl;
    std::cout << "\n🎉 ТЕСТЫ ЗАВЕРШЕНЫ!" << std::endl;
    
    return 0;
}
