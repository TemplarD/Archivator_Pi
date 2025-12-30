#!/usr/bin/env python3
"""
Главный тестовый раннер для многопоточных алгоритмов
Запускает все тесты и создает сводный отчет
"""

import sys
import os
import time
import subprocess
from typing import Dict, List, Any
import json

# Добавляем путь к исходникам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class MultiThreadTestRunner:
    """Главный тестовый раннер"""
    
    def __init__(self):
        self.test_dir = os.path.dirname(__file__)
        self.results = {}
        self.start_time = time.time()
    
    def run_all_tests(self):
        """Запускает все тесты многопоточности"""
        print("🧪 Запуск всех тестов многопоточности")
        print("=" * 60)
        print(f"📁 Папка тестов: {self.test_dir}")
        print()
        
        # Список тестов для запуска
        test_files = [
            ("test_all_algorithms.py", "Базовые тесты алгоритмов"),
            ("test_progress_bars.py", "Тесты прогресс-баров"),
            ("test_performance.py", "Тесты производительности")
        ]
        
        overall_success = True
        
        for test_file, description in test_files:
            test_path = os.path.join(self.test_dir, test_file)
            
            if not os.path.exists(test_path):
                print(f"❌ Файл не найден: {test_file}")
                overall_success = False
                continue
            
            print(f"🔧 Запуск: {description}")
            print(f"📄 Файл: {test_file}")
            print("-" * 40)
            
            try:
                # Запускаем тест
                result = subprocess.run(
                    [sys.executable, test_path],
                    capture_output=True,
                    text=True,
                    cwd=self.test_dir
                )
                
                # Сохраняем результат
                self.results[test_file] = {
                    "description": description,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
                
                if result.returncode == 0:
                    print("✅ Тест пройден")
                else:
                    print("❌ Тест провален")
                    overall_success = False
                    print(f"Ошибка: {result.stderr[:200]}...")
                
                print()
                
            except Exception as e:
                print(f"❌ Ошибка запуска теста: {e}")
                self.results[test_file] = {
                    "description": description,
                    "error": str(e),
                    "success": False
                }
                overall_success = False
                print()
        
        # Создаем сводный отчет
        self._create_summary_report()
        
        return overall_success
    
    def _create_summary_report(self):
        """Создает сводный отчет"""
        print("📊 Сводный отчет по тестам")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r.get("success", False))
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Всего тестов: {total_tests}")
        print(f"✅ Пройдено: {passed_tests}")
        print(f"❌ Провалено: {failed_tests}")
        print(f"📊 Успешность: {passed_tests/total_tests*100:.1f}%")
        print()
        
        # Детальная информация
        for test_file, result in self.results.items():
            status = "✅" if result.get("success", False) else "❌"
            description = result.get("description", "Нет описания")
            print(f"{status} {description} ({test_file})")
        
        # Сохраняем отчет
        self._save_summary_report()
        
        # Показываем время выполнения
        elapsed = time.time() - self.start_time
        print(f"\n⏱️  Общее время выполнения: {elapsed:.2f} сек")
    
    def _save_summary_report(self):
        """Сохраняет сводный отчет в файл"""
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results.values() if r.get("success", False)),
            "failed_tests": sum(1 for r in self.results.values() if not r.get("success", False)),
            "execution_time": time.time() - self.start_time,
            "results": {}
        }
        
        # Добавляем детальные результаты
        for test_file, result in self.results.items():
            report_data["results"][test_file] = {
                "description": result.get("description", ""),
                "success": result.get("success", False),
                "error": result.get("error", ""),
                "return_code": result.get("return_code", -1)
            }
        
        # Сохраняем JSON отчет
        json_file = os.path.join(self.test_dir, "multi_thread_test_summary.json")
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Отчет сохранен: {json_file}")
        
        # Сохраняем текстовый отчет
        self._save_text_report()
    
    def _save_text_report(self):
        """Сохраняет текстовый отчет"""
        report_file = os.path.join(self.test_dir, "multi_thread_test_report.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("🧪 Сводный отчет по тестам многопоточности\n")
            f.write("=" * 60 + "\n")
            f.write(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Время выполнения: {time.time() - self.start_time:.2f} сек\n\n")
            
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results.values() if r.get("success", False))
            failed_tests = total_tests - passed_tests
            
            f.write(f"📈 Статистика:\n")
            f.write(f"  Всего тестов: {total_tests}\n")
            f.write(f"  Пройдено: {passed_tests}\n")
            f.write(f"  Провалено: {failed_tests}\n")
            f.write(f"  Успешность: {passed_tests/total_tests*100:.1f}%\n\n")
            
            f.write("📊 Детальные результаты:\n")
            f.write("-" * 40 + "\n")
            
            for test_file, result in self.results.items():
                status = "✅" if result.get("success", False) else "❌"
                description = result.get("description", "Нет описания")
                f.write(f"{status} {description} ({test_file})\n")
                
                if not result.get("success", False) and "error" in result:
                    f.write(f"   Ошибка: {result['error']}\n")
                
                f.write("\n")
        
        print(f"📄 Текстовый отчет сохранен: {report_file}")
    
    def check_environment(self):
        """Проверяет окружение для тестов"""
        print("🔍 Проверка окружения")
        print("-" * 30)
        
        # Проверяем Python
        print(f"🐍 Python: {sys.version}")
        
        # Проверяем доступные модули
        required_modules = [
            "multiprocessing",
            "concurrent.futures",
            "threading",
            "time",
            "json"
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module} - не найден")
                return False
        
        # Проверяем доступность исходников
        src_path = os.path.join(os.path.dirname(__file__), "..", "src")
        if os.path.exists(src_path):
            print(f"✅ Исходники найдены: {src_path}")
        else:
            print(f"❌ Исходники не найдены: {src_path}")
            return False
        
        # Проверяем CPU
        try:
            import multiprocessing as mp
            print(f"🖥️  CPU ядра: {mp.cpu_count()}")
        except:
            print("❌ Не удалось определить количество ядер")
            return False
        
        print("✅ Окружение готово для тестов\n")
        return True

def main():
    """Основная функция"""
    runner = MultiThreadTestRunner()
    
    # Проверяем окружение
    if not runner.check_environment():
        print("❌ Окружение не готово. Тесты не могут быть выполнены.")
        return False
    
    # Запускаем все тесты
    success = runner.run_all_tests()
    
    # Итоговый результат
    print("\n🎯 Итоговый результат:")
    if success:
        print("✅ Все тесты пройдены успешно!")
    else:
        print("❌ Некоторые тесты провалены. Проверьте отчеты.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
