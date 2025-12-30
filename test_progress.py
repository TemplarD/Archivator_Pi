#!/usr/bin/env python3
"""
Простой тест прогресс-бара
"""

import time
import sys

def test_progress_bar():
    """Тестирует прогресс-бар"""
    print("Тест прогресс-бара:")
    
    for i in range(101):
        bar_length = 30
        filled_length = int(bar_length * i / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        sys.stdout.write(f"\r🔄 Тест: |{bar}| {i:3.0f}%")
        sys.stdout.flush()
        time.sleep(0.02)
    
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    test_progress_bar()
