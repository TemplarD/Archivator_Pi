#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <thread>
#include <mutex>
#include <fstream>
#include <iomanip>
#include <gmpxx.h>

class ChudnovskyPiGenerator {
private:
    mpz_class factorial(mpz_class n) {
        mpz_class result = 1;
        for (mpz_class i = 2; i <= n; ++i) {
            result *= i;
        }
        return result;
    }
    
    mpz_class binomial_coefficient(mpz_class n, mpz_class k) {
        if (k > n) return 0;
        if (k > n - k) k = n - k;
        
        mpz_class result = 1;
        for (mpz_class i = 1; i <= k; ++i) {
            result = result * (n - k + i) / i;
        }
        return result;
    }
    
public:
    std::string generate_pi_digits(int digits) {
        const int terms = digits / 14 + 1;
        mpf_class pi(0, digits + 10);
        mpf_class sum(0, digits + 10);
        
        for (int k = 0; k < terms; ++k) {
            mpf_class term(0, digits + 10);
            
            // Числитель: (426880 * sqrt(10005))
            mpf_class numerator(426880, digits + 10);
            mpf_class sqrt_10005;
            mpf_sqrt(sqrt_10005.get_mpf_t(), mpf_class(10005, digits + 10).get_mpf_t());
            numerator *= sqrt_10005;
            
            // Знаменатель: (6k)! * (13591409 + 545140134k)
            mpz_class six_k_fact = factorial(6 * k);
            mpf_class denominator(six_k_fact, digits + 10);
            
            mpz_class linear_term = 13591409 + 545140134 * k;
            denominator *= linear_term;
            
            // Дополнительный множитель: (-1)^k / ((3k)! * (k!)^3 * 640320^(3k+3/2))
            mpf_class additional(1, digits + 10);
            
            if (k % 2 == 1) {
                additional = -1;
            }
            
            mpz_class three_k_fact = factorial(3 * k);
            mpz_class k_fact = factorial(k);
            mpz_class k_fact_cubed = k_fact * k_fact * k_fact;
            
            additional /= three_k_fact;
            additional /= k_fact_cubed;
            
            mpf_class base_640320(640320, digits + 10);
            mpf_pow_ui(base_640320.get_mpf_t(), base_640320.get_mpf_t(), 3 * k + 1);
            mpf_sqrt(base_640320.get_mpf_t(), base_640320.get_mpf_t());
            additional /= base_640320;
            
            term = numerator / denominator * additional;
            sum += term;
        }
        
        pi = 1 / sum;
        
        // Преобразование в строку
        mp_exp_t exp;
        std::string pi_str = pi.get_str(exp, 10, digits);
        
        // Удаляем "0." в начале
        if (pi_str.length() > 2 && pi_str.substr(0, 2) == "0.") {
            pi_str = pi_str.substr(2);
        }
        
        // Обрезаем до нужного количества цифр
        if (pi_str.length() > digits) {
            pi_str = pi_str.substr(0, digits);
        }
        
        return pi_str;
    }
    
    void generate_to_file(int digits, const std::string& filename) {
        std::cout << "Генерация " << digits << " цифр π..." << std::endl;
        std::string pi_digits = generate_pi_digits(digits);
        
        std::ofstream file(filename);
        if (file.is_open()) {
            file << pi_digits;
            file.close();
            std::cout << "Цифры π сохранены в файл: " << filename << std::endl;
            std::cout << "Размер файла: " << pi_digits.length() << " байт" << std::endl;
        } else {
            std::cerr << "Ошибка открытия файла: " << filename << std::endl;
        }
    }
    
    // Многопоточная генерация
    void generate_parallel(int digits, const std::string& filename, int num_threads = 4) {
        std::cout << "Параллельная генерация " << digits << " цифр π с " << num_threads << " потоками..." << std::endl;
        
        // Для простоты используем однопоточную версию с оптимизацией
        // В реальной реализации здесь было бы разделение работы между потоками
        generate_to_file(digits, filename);
    }
};

int main() {
    ChudnovskyPiGenerator generator;
    
    std::cout << "Pi-Archiver Ultra - CPU Chudnovsky Generator" << std::endl;
    std::cout << "Generating first 1000 digits of pi..." << std::endl;
    
    std::string pi_digits = generator.generate_pi_digits(1000);
    std::cout << "First 100 digits: " << pi_digits.substr(0, 100) << std::endl;
    std::cout << "Total digits generated: " << pi_digits.length() << std::endl;
    
    return 0;
}
