#pragma once
#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <atomic>
#include <iomanip>

namespace pi_archiver {

class ProgressBar {
private:
    std::atomic<int>* completed_iterations_;
    int total_iterations_;
    std::thread progress_thread_;
    bool enabled_;
    
public:
    ProgressBar(std::atomic<int>* completed, int total, bool enable = true) 
        : completed_iterations_(completed), total_iterations_(total), enabled_(enable) {
        
        if (enabled_) {
            progress_thread_ = std::thread([this]() {
                int last_progress = -1;
                while (completed_iterations_->load() < total_iterations_) {
                    int progress = (completed_iterations_->load() * 100) / total_iterations_;
                    if (progress != last_progress) {
                        // Строим прогресс-бар
                        int bar_length = 20;
                        int filled_length = int(bar_length * progress / 100);
                        
                        std::string bar = "";
                        for (int i = 0; i < bar_length; ++i) {
                            if (i < filled_length) {
                                bar += "█";
                            } else {
                                bar += "░";
                            }
                        }
                        
                        // Выводим прогресс
                        std::cout << "\rπ: |" << bar << "| " << std::setw(3) << progress << "% (" 
                                  << completed_iterations_->load() << "/" << total_iterations_ << ")";
                        std::cout.flush();
                        
                        last_progress = progress;
                    }
                    std::this_thread::sleep_for(std::chrono::milliseconds(200));
                }
                std::cout << "\rπ: |████████████████████| 100% - Завершено!" << std::endl;
            });
        }
    }
    
    ~ProgressBar() {
        if (enabled_ && progress_thread_.joinable()) {
            progress_thread_.join();
        }
    }
    
    void disable() {
        enabled_ = false;
    }
};

} // namespace pi_archiver
