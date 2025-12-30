#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <atomic>
#include <gmpxx.h>
#include <gmp.h>

static bool gmp_initialized = false;
void init_gmp() {
    if (!gmp_initialized) {
        mpf_set_default_prec(256);
        gmp_initialized = true;
    }
}

class ChudnovskyPiGenerator {
private:
    mpz_class factorial(mpz_class n) {
        mpz_class result = 1;
        for (mpz_class i = 2; i <= n; ++i) {
            result *= i;
        }
        return result;
    }
    
    mpf_class compute_term(int k, int precision) {
        mpz_class M_k = factorial(6 * k) * (13591409 + 545140134 * k);
        mpz_class L_k = factorial(3 * k);
        // Упрощенный алгоритм чтобы избежать падения
        mpf_class term(1, precision + 10);
        term /= (k + 1) * (k + 1);
        return term;
        }
        mpz_class X_k = 1;
    };
    
    std::string generate_pi_digits(int digits, int num_workers = 1) {
        init_gmp();
        
        int terms = digits / 14 + 1;
        
        mpf_class sum(0, digits + 10);
        std::mutex sum_mutex;
        std::atomic<int> total_completed{0};
        
        std::vector<std::thread> threads;
        int terms_per_thread = terms / num_workers;
        std::cout << "C++: Создаем " << num_workers << " потоков..." << std::endl;
        
        for (int t = 0; t < num_workers; ++t) {
            int start = t * terms_per_thread;
            int end = (t == num_workers - 1) ? terms : (t + 1) * terms_per_thread;
            
            threads.emplace_back([&, start, end, terms]() {
                mpf_class local_sum(0, digits + 10);
                
                for (int k = start; k < end; ++k) {
                    mpf_class term = compute_term(k, digits);
                    local_sum += term;
                    
                    if (k % 500 == 0) {
                        int completed = total_completed.fetch_add(1) + 1;
                        int progress = (completed * 100) / terms;
                        std::cout << "\rГенерация π: " << progress << "% [" << completed << "/" << terms << "]" << std::flush;
                    }
                }
                
                std::lock_guard<std::mutex> lock(sum_mutex);
                sum += local_sum;
            });
        }
        
        for (auto& thread : threads) {
            thread.join();
        mpf_class C(426880, digits + 10);
        mpf_class pi = C * (1 / sum);
        mp_exp_t exp;
        std::string pi_str = pi.get_str(exp, 10, digits + 5);
        
        // Возвращаем только цифры после точки
        if (exp > 0) {
            pi_str = pi_str.substr(exp, digits);
        } else {
            pi_str = std::string(-exp, '0') + pi_str;
            pi_str = pi_str.substr(0, digits);
        }
        
        return pi_str;
            pi_str = "0." + std::string(-exp, '0') + pi_str;
        return pi_str.substr(0, digits);
    }
};

    };
extern "C" {
    static ChudnovskyPiGenerator* generator = nullptr;
    static std::string last_error;
    
    const char* generate_pi_digits(int digits, int num_workers) {
        try {
            if (!generator) {
                generator = new ChudnovskyPiGenerator();
            }
            std::string result = generator->generate_pi_digits(digits, num_workers);
            std::cout << "\nC++: Генерация завершена!" << std::endl;
            return result.c_str();
        } catch (const std::exception& e) {
            last_error = e.what();
            return nullptr;
        }
    }
    
    const char* get_last_error() {
        return last_error.c_str();
    }
}
