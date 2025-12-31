#include <iostream>
#include <chrono>
#include <iomanip>
#include <fstream>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🚀 ВЫЧИСЛЕНИЕ 1,000,000 ЦИФР π" << std::endl;
    std::cout << "==================================" << std::endl;
    
    int precision = 1000000;  // 1 миллион цифр
    int num_threads = 39;     // Лучшая производительность по тестам
    
    std::cout << "📊 Параметры:" << std::endl;
    std::cout << "   Точность: " << precision << " цифр" << std::endl;
    std::cout << "   Потоки: " << num_threads << std::endl;
    std::cout << "   Метод: Auto (оптимальный выбор)" << std::endl;
    std::cout << std::endl;
    
    // Создаем калькулятор
    std::cout << "🔧 Инициализация калькулятора..." << std::endl;
    pi_archiver::ChudnovskyCalculator calc(precision);
    
    // Начинаем вычисление
    std::cout << "⚡ Запуск вычисления..." << std::endl;
    std::cout << "Это займет несколько минут. Пожалуйста, подождите..." << std::endl;
    std::cout << std::endl;
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Вычисляем π с использованием оптимального метода
    std::string pi = calc.compute_pi_auto(num_threads);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();
    
    std::cout << std::endl;
    std::cout << "✅ Вычисление завершено!" << std::endl;
    std::cout << "⏱️  Время выполнения: " << duration << " мс (" << duration/1000.0 << " сек)" << std::endl;
    std::cout << "📏 Получено цифр: " << pi.length() << std::endl;
    
    // Проверка корректности
    std::string expected_start = "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679";
    std::string actual_start = pi.substr(0, std::min(expected_start.length(), pi.length()));
    bool is_correct = (expected_start == actual_start);
    
    std::cout << "🔍 Корректность: " << (is_correct ? "✅ ВЕРНО" : "❌ НЕВЕРНО") << std::endl;
    
    if (!is_correct) {
        std::cout << "⚠️  Ожидалось: " << expected_start.substr(0, 50) << "..." << std::endl;
        std::cout << "⚠️  Получено:  " << actual_start.substr(0, 50) << "..." << std::endl;
    }
    
    // Сохранение в файл
    std::cout << std::endl;
    std::cout << "💾 Сохранение в файл..." << std::endl;
    
    std::ofstream file("pi_1M_digits.txt");
    if (file.is_open()) {
        file << pi;
        file.close();
        
        // Проверка файла
        std::ifstream check_file("pi_1M_digits.txt");
        if (check_file.is_open()) {
            check_file.seekg(0, std::ios::end);
            size_t file_size = check_file.tellg();
            check_file.close();
            
            std::cout << "✅ Файл создан: pi_1M_digits.txt" << std::endl;
            std::cout << "📏 Размер файла: " << file_size << " байт" << std::endl;
            std::cout << "📊 Длина π: " << pi.length() << " символов" << std::endl;
            
            if (file_size == pi.length()) {
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
    
    // Вывод первых 100 цифр для проверки
    std::cout << std::endl;
    std::cout << "🔢 Первые 100 цифр π:" << std::endl;
    std::cout << pi.substr(0, 100) << std::endl;
    
    // Сравнение с Python
    std::cout << std::endl;
    std::cout << "🐍 СРАВНЕНИЕ С PYTHON:" << std::endl;
    std::cout << "   Python (оценка): ~1,000,000 мс (1000 сек) для 1,000,000 цифр" << std::endl;
    std::cout << "   C++ (результат): " << duration << " мс (" << duration/1000.0 << " сек)" << std::endl;
    
    double python_speedup = 1000000.0 / duration;
    std::cout << "   Ускорение vs Python: " << std::fixed << std::setprecision(1) 
              << python_speedup << "x" << std::endl;
    
    std::cout << std::endl;
    std::cout << "🎉 ВЫЧИСЛЕНИЕ 1,000,000 ЦИФР π ЗАВЕРШЕНО!" << std::endl;
    
    return 0;
}
