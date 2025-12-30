#pragma once
#include "chudnovsky_calculator.h"
#include "progress_bar.h"
#include <vector>
#include <thread>
#include <atomic>

namespace pi_archiver {

class OptimizedChudnovskyCalculator {
private:
    int precision_;
    mpfr_t pi_;
    mpfr_t sqrt_10005_;
    mpfr_t c3_over_24_;  // 640320^3/24
    
    // Копируем нужные методы из базового класса
    int calculate_iterations(int precision) {
        return (precision + 14) / 14 + 1;
    }
    
public:
    OptimizedChudnovskyCalculator(int precision) : precision_(precision) {
        mpfr_init2(pi_, precision + 100);
        mpfr_init2(sqrt_10005_, precision + 100);
        mpfr_init2(c3_over_24_, precision + 100);
        
        mpfr_sqrt_ui(sqrt_10005_, 10005, MPFR_RNDN);
        
        // Вычисляем 640320^3/24
        mpfr_t temp;
        mpfr_init2(temp, precision + 100);
        mpfr_set_ui(temp, 640320, MPFR_RNDN);
        mpfr_pow_ui(temp, temp, 3, MPFR_RNDN);
        mpfr_div_ui(c3_over_24_, temp, 24, MPFR_RNDN);
        mpfr_clear(temp);
    }
    
    ~OptimizedChudnovskyCalculator() {
        mpfr_clear(pi_);
        mpfr_clear(sqrt_10005_);
        mpfr_clear(c3_over_24_);
    }
    
    std::string compute_pi_optimized(int num_threads) {
        auto start_time = std::chrono::high_resolution_clock::now();
        
        // Вычисляем количество итераций
        int n = calculate_iterations(precision_);
        
        // Для 1 потока используем базовую реализацию
        if (num_threads == 1) {
            return compute_pi_single_thread(n);
        }
        
        // ОПТИМИЗИРОВАННАЯ МНОГОПОТОЧНАЯ ВЕРСИЯ
        std::cout << "Прогресс: |                    |   0%" << std::flush;
        
        // Минимизируем копии данных - используем shared данные
        std::vector<mpfr_t> partial_results(num_threads);
        
        // Атомарный счетчик для прогресс-бара (обновляем реже)
        std::atomic<int> completed_iterations{0};
        
        // Создаем прогресс-бар
        ProgressBar progress_bar(&completed_iterations, n);
        
        // Инициализируем только необходимые данные
        for (int i = 0; i < num_threads; ++i) {
            mpfr_init2(partial_results[i], precision_ + 100);
            mpfr_set_ui(partial_results[i], 0, MPFR_RNDN);
        }
        
        // Динамическое распределение работы
        std::vector<std::thread> threads;
        std::atomic<int> current_iteration{0};
        
        for (int i = 0; i < num_threads; ++i) {
            threads.emplace_back([this, &partial_results, &completed_iterations, &current_iteration, n, i]() {
                worker_function_optimized(partial_results[i], precision_, 
                                       completed_iterations, current_iteration, n, i);
            });
        }
        
        // Ждем завершения всех потоков
        for (auto& thread : threads) {
            if (thread.joinable()) {
                thread.join();
            }
        }
        
        // Параллельная сборка результатов
        mpfr_t final_sum;
        mpfr_init2(final_sum, precision_ + 100);
        combine_results_parallel(partial_results, final_sum, num_threads);
        
        // Вычисляем финальный результат
        mpfr_t numerator;
        mpfr_init2(numerator, precision_ + 100);
        mpfr_mul_ui(numerator, sqrt_10005_, 426880, MPFR_RNDN);
        
        mpfr_set_ui(pi_, 0, MPFR_RNDN);
        mpfr_div(pi_, numerator, final_sum, MPFR_RNDN);
        
        // Очищаем память
        for (int i = 0; i < num_threads; ++i) {
            mpfr_clear(partial_results[i]);
        }
        mpfr_clear(final_sum);
        mpfr_clear(numerator);
        
        // Конвертируем в строку
        char* pi_str = nullptr;
        mpfr_asprintf(&pi_str, "%.1000000Rf", pi_);
        
        std::string result;
        if (pi_str) {
            std::string digits(pi_str);
            if (digits.length() > 1 && digits[0] == '3') {
                result = digits;
            } else {
                result = "3." + digits;
            }
            mpfr_free_str(pi_str);
        }
        
        auto final_time = std::chrono::high_resolution_clock::now();
        auto total_duration = std::chrono::duration_cast<std::chrono::seconds>(final_time - start_time).count();
        
        std::cout << "✅ Оптимизированное вычисление завершено за " << total_duration << " секунд!" << std::endl;
        std::cout << "📏 Получено " << result.length() << " цифр π" << std::endl;
        
        return result;
    }
    
private:
    std::string compute_pi_single_thread(int n) {
        // Быстрая однопоточная реализация (как в оригинале)
        mpfr_set_ui(pi_, 0, MPFR_RNDN);
        
        mpfr_t sum, term, p_k, q_k, temp;
        mpz_t m_j, k_term;
        mpz_t a_local;
        
        mpfr_init2(sum, precision_ + 100);
        mpfr_init2(term, precision_ + 100);
        mpfr_init2(p_k, precision_ + 100);
        mpfr_init2(q_k, precision_ + 100);
        mpfr_init2(temp, precision_ + 100);
        mpz_init(m_j);
        mpz_init(k_term);
        mpz_init(a_local);
        
        mpz_set_ui(a_local, 13591409);
        
        // Вычисляем сумму
        for (int k = 0; k < n; ++k) {
            if (k == 0) {
                mpfr_set_z(term, a_local, MPFR_RNDN);
            } else {
                mpfr_set_ui(p_k, 1, MPFR_RNDN);
                
                for (int j = 1; j <= k; ++j) {
                    unsigned long m_val = (6*j - 5) * (2*j - 1) * (6*j - 1);
                    mpz_set_ui(m_j, m_val);
                    mpfr_set_z(temp, m_j, MPFR_RNDN);
                    mpfr_neg(temp, temp, MPFR_RNDN);
                    mpfr_mul(p_k, p_k, temp, MPFR_RNDN);
                }
                
                mpfr_set_ui(q_k, 1, MPFR_RNDN);
                for (int j = 1; j <= k; ++j) {
                    mpfr_set_ui(temp, j, MPFR_RNDN);
                    mpfr_pow_ui(temp, temp, 3, MPFR_RNDN);
                    mpfr_mul(temp, temp, c3_over_24_, MPFR_RNDN);
                    mpfr_mul(q_k, q_k, temp, MPFR_RNDN);
                }
                
                mpz_set_ui(k_term, k);
                mpz_mul_ui(k_term, k_term, 545140134);
                mpz_add(k_term, k_term, a_local);
                
                mpfr_set_z(temp, k_term, MPFR_RNDN);
                mpfr_mul(term, p_k, temp, MPFR_RNDN);
                mpfr_div(term, term, q_k, MPFR_RNDN);
            }
            
            mpfr_add(sum, sum, term, MPFR_RNDN);
        }
        
        // Вычисляем финальный результат
        mpfr_t numerator;
        mpfr_init2(numerator, precision_ + 100);
        mpfr_mul_ui(numerator, sqrt_10005_, 426880, MPFR_RNDN);
        mpfr_div(pi_, numerator, sum, MPFR_RNDN);
        
        char* pi_str = nullptr;
        mpfr_asprintf(&pi_str, "%.1000000Rf", pi_);
        
        std::string result;
        if (pi_str) {
            std::string digits(pi_str);
            if (digits.length() > 1 && digits[0] == '3') {
                result = digits;
            } else {
                result = "3." + digits;
            }
            mpfr_free_str(pi_str);
        }
        
        mpfr_clear(sum);
        mpfr_clear(term);
        mpfr_clear(p_k);
        mpfr_clear(q_k);
        mpfr_clear(temp);
        mpfr_clear(numerator);
        mpz_clear(m_j);
        mpz_clear(k_term);
        mpz_clear(a_local);
        
        return result;
    }
    
    void worker_function_optimized(mpfr_t result, int precision, 
                                  std::atomic<int>& completed_iterations,
                                  std::atomic<int>& current_iteration, 
                                  int total_iterations, int thread_id) {
        mpfr_set_ui(result, 0, MPFR_RNDN);
        
        // Временные переменные (переиспользуем)
        mpfr_t term, p_k, q_k, temp;
        mpz_t m_j, k_term;
        
        mpfr_init2(term, precision + 100);
        mpfr_init2(p_k, precision + 100);
        mpfr_init2(q_k, precision + 100);
        mpfr_init2(temp, precision + 100);
        mpz_init(m_j);
        mpz_init(k_term);
        
        // Динамическая работа - берем задачи по мере их выполнения
        while (true) {
            int k = current_iteration.fetch_add(1);
            if (k >= total_iterations) break;
            
            // Вычисляем член ряда
            compute_series_term(k, term, p_k, q_k, temp, m_j, k_term);
            mpfr_add(result, result, term, MPFR_RNDN);
            
            // Обновляем прогресс реже (каждые 100 итераций)
            if (k % 100 == 0) {
                completed_iterations.fetch_add(100);
            }
        }
        
        // Добавляем оставшиеся итерации
        int remaining = total_iterations % 100;
        if (remaining > 0) {
            completed_iterations.fetch_add(remaining);
        }
        
        // Очищаем память
        mpfr_clear(term);
        mpfr_clear(p_k);
        mpfr_clear(q_k);
        mpfr_clear(temp);
        mpz_clear(m_j);
        mpz_clear(k_term);
    }
    
    void compute_series_term(int k, mpfr_t term, mpfr_t p_k, mpfr_t q_k, 
                            mpfr_t temp, mpz_t m_j, mpz_t k_term) {
        if (k == 0) {
            // Первый член ряда: a = 13591409
            mpz_set_ui(m_j, 13591409);
            mpfr_set_z(term, m_j, MPFR_RNDN);
        } else {
            // Вычисляем p_k = product_{j=1..k} -(6j-5)(2j-1)(6j-1)
            mpfr_set_ui(p_k, 1, MPFR_RNDN);
            
            for (int j = 1; j <= k; ++j) {
                unsigned long m_val = (6*j - 5) * (2*j - 1) * (6*j - 1);
                mpz_set_ui(m_j, m_val);
                mpfr_set_z(temp, m_j, MPFR_RNDN);
                mpfr_neg(temp, temp, MPFR_RNDN);
                mpfr_mul(p_k, p_k, temp, MPFR_RNDN);
            }
            
            // Вычисляем q_k = product_{j=1..k} j^3 * (640320^3/24)
            mpfr_set_ui(q_k, 1, MPFR_RNDN);
            for (int j = 1; j <= k; ++j) {
                mpfr_set_ui(temp, j, MPFR_RNDN);
                mpfr_pow_ui(temp, temp, 3, MPFR_RNDN);
                mpfr_mul(temp, temp, c3_over_24_, MPFR_RNDN);
                mpfr_mul(q_k, q_k, temp, MPFR_RNDN);
            }
            
            // Вычисляем числитель: k * 545140134 + 13591409
            mpz_set_ui(k_term, k);
            mpz_mul_ui(k_term, k_term, 545140134);
            mpz_add_ui(k_term, k_term, 13591409);
            
            // term = p_k * (k * 545140134 + 13591409) / q_k
            mpfr_set_z(temp, k_term, MPFR_RNDN);
            mpfr_mul(term, p_k, temp, MPFR_RNDN);
            mpfr_div(term, term, q_k, MPFR_RNDN);
        }
    }
    
    void combine_results_parallel(const std::vector<mpfr_t>& partial_results, 
                                mpfr_t final_sum, int num_threads) {
        // Параллельная редукция - tree reduction
        mpfr_set_ui(final_sum, 0, MPFR_RNDN);
        
        // Простое последовательное сложение для начала
        for (int i = 0; i < num_threads; ++i) {
            mpfr_add(final_sum, final_sum, partial_results[i], MPFR_RNDN);
        }
    }
};

} // namespace pi_archiver
