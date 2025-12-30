#pragma once

#include <string>
#include <vector>
#include <memory>
#include <thread>
#include <future>
#include <mutex>
#include <gmp.h>
#include <mpfr.h>

namespace pi_archiver {

/**
 * @brief Высокопроизводительный калькулятор π по алгоритму Чудновских
 * 
 * Класс реализует многопоточный алгоритм Чудновских с использованием
 * GMP для высокоточных вычислений и std::thread для параллелизма
 */
class ChudnovskyCalculator {
public:
    /**
     * @brief Конструктор
     * @param precision Количество цифр π для вычисления
     */
    explicit ChudnovskyCalculator(int precision);
    
    /**
     * @brief Деструктор
     */
    ~ChudnovskyCalculator();
    
    // Worker функции (для многопоточности)
    void worker_function(int start, int end, mpfr_t result, int precision, 
                     mpz_t a, mpz_t b, mpfr_t c3_over_24, std::atomic<int>* completed_iterations = nullptr);
    
    // Оптимизированная worker функция
    void worker_function_optimized(mpfr_t result, int precision, 
                                  std::atomic<int>& completed_iterations,
                                  std::atomic<int>& current_iteration, 
                                  int total_iterations, int thread_id);
    
    /**
     * @brief Вычислить π с указанным количеством потоков
     * @param num_threads Количество потоков (0 = автоопределение)
     * @return Строка с цифрами π
     */
    std::string compute_pi(int num_threads = 0);
    
    /**
     * @brief Вычислить π с указанным количеством потоков (оптимизированный метод)
     * @param num_threads Количество потоков (0 = автоопределение)
     * @return Строка с цифрами π
     */
    std::string compute_pi_optimized(int num_threads = 0);
    
    /**
     * @brief Вычислить π с указанным количеством потоков (универсальный метод)
     * @param num_threads Количество потоков (0 = автоопределение)
     * @return Строка с цифрами π
     */
    std::string compute_pi_auto(int num_threads = 0);
    
    /**
     * @brief Получить значение π
     * @return Строка с цифрами π
     */
    std::string get_pi() const;
    
    /**
     * @brief Получить рекомендуемое количество потоков
     * @return Оптимальное количество потоков для системы
     */
    static int get_optimal_threads();
    
    /**
     * @brief Установить точность вычислений
     * @param precision Количество цифр
     */
    void set_precision(int precision);
    
    /**
     * @brief Получить текущую точность
     * @return Текущая точность
     */
    int get_precision() const;

private:
    int precision_;
    mpfr_t pi_;
    mpfr_t sqrt_10005_;
    mpfr_t c3_over_24_;
    
    // Константы Чудновских
    mpz_t a_;
    mpz_t b_;
    mpz_t c_;
    
    /**
     * @brief Инициализировать константы
     */
    void initialize_constants();
    
    int calculate_iterations(int precision) {
        return (precision + 14) / 14 + 1;
    }
    
    /**
     * @brief Комбинировать результаты от потоков
     * @param partial_results Частичные результаты
     * @param result Выходной параметр для результата
     */
    void combine_results(const std::vector<mpfr_t>& partial_results, mpfr_t result);
    
    // Мьютекс для потокобезопасности
    mutable std::mutex mutex_;
};

} // namespace pi_archiver
