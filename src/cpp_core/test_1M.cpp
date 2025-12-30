#include <iostream>
#include <chrono>
#include <fstream>
#include "chudnovsky_calculator.h"

int main() {
    std::cout << "🧪 ПРОВЕРКА 1,000,000 ЦИФР π" << std::endl;
    std::cout << "================================" << std::endl;
    
    int precision = 1000000;
    int threads = 39;
    
    std::cout << "Запускаем вычисление " << precision << " цифр на " << threads << " потоках..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    pi_archiver::ChudnovskyCalculator calc(precision);
    std::string pi = calc.compute_pi(threads);
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start).count();
    
    std::cout << "✅ Вычисление завершено за " << duration << " секунд" << std::endl;
    std::cout << "📏 Длина результата: " << pi.length() << " символов" << std::endl;
    
    // Проверяем первые 50 цифр
    std::string expected = "3.141592653589793238462643383279502884197169399375";
    std::string actual = pi.substr(0, 50);
    
    std::cout << "🔍 Первые 50 цифр: " << actual << std::endl;
    std::cout << "✅ Корректность: " << (expected == actual ? "ВЕРНО" : "НЕВЕРНО") << std::endl;
    
    // Сохраняем в файл
    std::ofstream file("pi_1M_test.txt");
    if (file.is_open()) {
        file << pi;
        file.close();
        std::cout << "💾 Результат сохранен в pi_1M_test.txt" << std::endl;
    }
    
    return 0;
}
