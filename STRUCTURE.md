# 📁 Структура проекта Archivator_Pi

## 🎯 Обзор архитектуры

```
Archivator_Pi/
├── 📚 Документация
│   ├── README.md                    # Основное описание проекта
│   ├── PROJECT_SPEC.md              # Технические требования
│   ├── DEVELOPMENT_LOG.md           # Журнал разработки
│   ├── INSTALL.md                   # Инструкция по установке
│   ├── DEBUG.md                     # Отладочная информация
│   └── 📄 STRUCTURE.md              # Этот файл
│
├── 🔧 Система сборки и настройки
│   ├── requirements.txt             # Зависимости Python
│   ├── install_system.sh            # Системная установка
│   ├── install_ubuntu24.sh         # Установка для Ubuntu 24.04
│   ├── uninstall.sh                 # Удаление проекта
│   ├── pi_config.yaml              # Конфигурация проекта
│   ├── thread_info.py               # Информация о потоках
│   └── .gitignore                   # Игнорируемые файлы Git
│
├── 🧪 Тестирование
│   ├── tests/                       # Модульные тесты
│   │   ├── compression_tests/       # Тесты сжатия
│   │   │   └── test_compression_core.py
│   │   ├── performance_tests/       # Тесты производительности
│   │   │   └── performance_benchmark.py
│   │   └── chudnovsky/              # Тесты Chudnovsky алгоритма
│   │       ├── test_correctness.py
│   │       ├── test_multithreading_10000.py
│   │       ├── test_optimal_threading.py
│   │       ├── test_real_multithreading.py
│   │       ├── test_threading_simple.py
│   │       ├── analyze_threading.py
│   │       ├── final_threading_test.py
│   │       ├── run_all_tests.py
│   │       └── cpu_intensive_worker.py
│   ├── test_adaptive_compression.py  # Тест адаптивного сжатия
│   ├── test_1M_pi_cache.py          # Тест на 1M цифр π из кеша
│   └── test_final_optimization.py   # Финальные тесты оптимизации
│
├── 💾 Данные и кэш
│   ├── data/                        # Входные данные для сжатия
│   ├── extracted/                   # Распакованные данные
│   ├── logs/                        # Логи сжатия (JSON + TXT)
│   └── pi_storage/                  # Хранилище цифр π
│       └── pi_1000000_digits.txt    # 1М цифр π (кэш)
│
├── 🚀 C++ Core (Высокопроизводительное ядро)
│   └── src/cpp_core/
│       ├── 📋 Документация
│       │   ├── README.md            # Описание C++ core
│       │   └── CMakeLists.txt       # Система сборки CMake
│       │
│       ├── 🔧 Система сборки
│       │   ├── build.sh             # Скрипт сборки
│       │   └── build/               # Директория сборки
│       │
│       ├── 📦 Заголовочные файлы
│       │   └── include/
│       │       ├── chudnovsky_calculator.h    # Основной калькулятор
│       │       ├── optimized_calculator.h     # Оптимизированная версия
│       │       └── progress_bar.h             # Переиспользуемый прогресс-бар
│       │
│       ├── 🔨 Исходный код
│       │   └── src/
│       │       └── chudnovsky_calculator.cpp  # Реализация калькулятора
│       │
│       ├── 🧪 Тесты C++
│       │   └── tests/
│       │       ├── CMakeLists.txt               # Сборка тестов
│       │       ├── test_chudnovsky.cpp         # Базовый тест
│       │       ├── test_optimized.cpp          # Тест оптимизации
│       │       ├── test_final.cpp              # Финальный unified тест
│       │       ├── test_1M.cpp                 # Тест 1М цифр
│       │       ├── test_universal.cpp          # Тест универсальной оптимизации
│       │       ├── test_medium.cpp             # Тест средних объемов (30K-200K)
│       │       ├── test_smart_threads.cpp       # Тест умного выбора потоков
│       │       └── test_adaptive.cpp          # Тест адаптивной системы
│       │
│       ├── 🐍 Python биндинги
│       │   └── bindings/
│       │       └── python_bindings.cpp         # PyBind11 биндинги
│       │
│       └── 📊 Примеры
│           └── test_1M.cpp                     # Пример вычисления 1М цифр
│
└── 📦 Исходный код
    └── src/
        ├── 🎯 Основные компоненты
        │   ├── pi_generator.py              # Основной класс генератора π
        │   ├── universal_generator.py        # Универсальный генератор
        │   └── __init__.py                   # Экспорт всех компонентов
        │
        ├── ⚙️ Алгоритмы генерации π
        │   └── algorithms/
        │       ├── __init__.py              # Базовые импорты алгоритмов
        │       │
        │       ├── 🧮 Chudnovsky алгоритмы
        │       │   └── chudnovsky/
        │       │       ├── __init__.py      # Экспорт Chudnovsky
        │       │       │
        │       │       ├── 📍 Однопоточные
        │       │       │   ├── __init__.py
        │       │       │   └── chudnovsky_single_thread.py
        │       │       │       └── ChudnovskySingleThread
        │       │       │
        │       │       ├── 🚀 Многопоточные
        │       │       │   ├── __init__.py
        │       │       │   ├── chudnovsky_binary_splitting.py
        │       │       │   │   └── ChudnovskyBinarySplitting (с умной логикой)
        │       │       │   ├── chudnovsky_block_parallel.py
        │       │       │   │   └── ChudnovskyBlockParallel (блочный параллелизм)
        │       │       │   ├── bbp_parallel.py
        │       │       │   │   └── BBPParallel (параллельный BBP)
        │       │       │   └── simple_parallel.py
        │       │       │       └── SimpleParallelChudnovsky (простой параллелизм)
        │       │       │
        │       │       └── 🎮 GPU ускоренные
        │       │           ├── __init__.py
        │       │           ├── chudnovsky_numpy_optimized.py
        │       │           │   └── NumpyOptimizedChudnovsky
        │       │           ├── opencl_chudnovsky.py
        │       │           │   └── OpenCLChudnovsky
        │       │           ├── cuda_chudnovsky.py
        │       │           │   └── CudaChudnovsky
        │       │           ├── gpu_chudnovsky.py
        │       │           │   └── GPUChudnovskyGenerator (старый OpenCL)
        │       │           ├── gpu_pi_generator_amd.py
        │       │           │   └── GPUChudnovskyGenerator (AMD Fury X)
        │       │           └── gpu_chudnovsky.cl
        │       │               └── OpenCL kernel для GPU
        │       │
        │       ├── 💻 Нативные реализации (C/C++)
        │       │   └── native/
        │       │       ├── __init__.py
        │       │       ├── c_pi_wrapper.py
        │       │       │   └── CPiGenerator (обертка для C++)
        │       │       ├── cpu_chudnovsky.cpp
        │       │       │   └── C++ реализация с GMP
        │       │       └── cpu_chudnovsky.so
        │       │           └── Скомпилированная библиотека
        │       │
        │       └── 🎲 Другие алгоритмы
        │           └── other/
        │               ├── __init__.py
        │               └── bbp_generator.py
        │                   └── BBPPiGenerator (Bailey–Borwein–Plouffe)
        │
        ├── 🗜️ Система сжатия (Python + C++)
        │   └── src/compression/
        │       ├── compression_core.py        # Основное ядро сжатия (C++ интеграция)
        │       ├── compression_logger.py      # Детальное логирование процесса
        │       ├── adaptive_search.py         # Адаптивный поиск с уменьшением блоков
        │       ├── multithreaded_search.py    # Оптимизированный многопоточный поиск
        │       ├── multithreaded_pi_search.py # Многопоточный поиск с 100% CPU
        │       └── multithreaded_compression.py # Многопоточное сжатие
        │
        ├── 🔍 Поисковый движок
        │   └── src/search_engine/
        │       ├── pi_search.py               # Поиск последовательностей в π
        │       ├── search_algorithms.py       # Алгоритмы поиска (Рабин-Карп)
        │       ├── bloom_filter.py            # Bloom фильтр оптимизации
        │       └── search_optimizer.py        # Оптимизация поиска
        │
        ├── 📊 Управление индексами
        │   └── index_manager/
        │       ├── __init__.py
        │       └── index_manager.py
        │           └── IndexManager (управление индексами)
        │
        ├── 🎛️ Утилиты и инструменты
        │   └── src/utils/
        │       ├── pi_generator.py           # Генератор π (fallback)
        │       ├── file_utils.py              # Работа с файлами
        │       ├── compression_utils.py      # Утилиты сжатия
        │       ├── performance_monitor.py     # Мониторинг производительности
        │       └── benchmark_tools.py        # Инструменты бенчмаркинга
        │       │   └── Продвинутый прогресс-бар
        │       ├── simple_progress.py
        │       │   └── Простой прогресс-бар
        │       └── system_info.py
        │           └── Информация о системе
        │
        └── 🎯 Основные модули
            └── main/
                ├── archive_operations/     # Операции архивации
                ├── extract_operations/     # Операции извлечения
                ├── progress_indicators/    # Индикаторы прогресса
                ├── archiver form.py         # Формы архиватора
                ├── archiver_enhanced.py    # Улучшенный архиватор
                ├── archiver_main.py         # Основной архиватор
                └── [другие файлы GUI]
                │
            └── dsp_module/                 # DSP модуль для обработки
```

## 🏗️ Описание компонентов

### 📚 **Документация**
- **README.md** - основное описание проекта и возможности
- **PROJECT_SPEC.md** - технические требования и спецификации
- **DEVELOPMENT_LOG.md** - журнал разработки и изменения
- **INSTALL.md** - пошаговая инструкция по установке
- **DEBUG.md** - отладочная информация и решение проблем

### 🔧 **Система сборки**
- **requirements.txt** - Python зависимости для проекта
- **install_system.sh** - скрипт системной установки
- **install_ubuntu24.sh** - установка для Ubuntu 24.04
- **uninstall.sh** - полное удаление проекта
- **pi_config.yaml** - основная конфигурация проекта
- **thread_info.py** - информация о доступных потоках CPU

### 🧪 **Тестирование**
- **tests/compression_tests/** - модульные тесты алгоритмов сжатия
- **tests/performance_tests/** - бенчмарки производительности
- **tests/chudnovsky/** - комплексные тесты Chudnovsky алгоритма
- **test_final_optimization.py** - комплексные тесты оптимизации

### 🚀 **C++ Core (Высокопроизводительное ядро)**

#### 📋 **Документация и сборка**
- **README.md** - описание C++ core и API
- **CMakeLists.txt** - система сборки CMake
- **build.sh** - скрипт сборки

#### 📦 **Заголовочные файлы**
- **chudnovsky_calculator.h** - основной калькулятор с unified интерфейсом
- **optimized_calculator.h** - оптимизированная версия калькулятора
- **progress_bar.h** - переиспользуемый потокобезопасный прогресс-бар

#### 🔨 **Исходный код**
- **chudnovsky_calculator.cpp** - полная реализация с умной адаптивной системой

#### 🧪 **Тесты C++**
- **test_chudnovsky.cpp** - базовый тест корректности
- **test_optimized.cpp** - тест оптимизированной версии
- **test_final.cpp** - финальный unified тест всех методов
- **test_1M.cpp** - тест вычисления 1 миллиона цифр
- **test_universal.cpp** - тест универсальной оптимизации
- **test_medium.cpp** - тест средних объемов (30K-200K)
- **test_smart_threads.cpp** - тест умного выбора потоков
- **test_adaptive.cpp** - тест адаптивной системы

#### 🐍 **Python биндинги**
- **python_bindings.cpp** - PyBind11 обертка для Python

#### 📊 **Примеры**
- **test_1M.cpp** - пример вычисления и сохранения 1М цифр

### 💾 **Данные и хранилище**
- **data/** - входные файлы для тестирования сжатия
- **extracted/** - распакованные данные
- **pi_storage/** - кэш сгенерированных цифр π
- **pi_1000000_digits.txt** - 1 миллион цифр π для быстрого доступа

### 🎯 **Основные компоненты**
- **pi_generator.py** - главный класс генерации π
- **universal_generator.py** - универсальный генератор с автоматическим выбором
- **__init__.py** - экспорт всех компонентов проекта

### ⚙️ **Алгоритмы генерации π**

#### 🧮 **Chudnovsky алгоритмы**
**Однопоточные:**
- `chudnovsky_single_thread.py` - базовая реализация с кэшированием факториалов

**Многопоточные:**
- `chudnovsky_binary_splitting.py` - binary splitting с умной логикой переключения режимов
- `chudnovsky_block_parallel.py` - блочный параллелизм для больших объемов
- `bbp_parallel.py` - параллельная реализация BBP алгоритма
- `simple_parallel.py` - простая многопоточная реализация

**GPU ускоренные:**
- `chudnovsky_numpy_optimized.py` - NumPy векторизация для CPU
- `opencl_chudnovsky.py` - OpenCL реализация для GPU
- `cuda_chudnovsky.py` - CUDA реализация для NVIDIA GPU
- `gpu_chudnovsky.py` - старая OpenCL реализация
- `gpu_pi_generator_amd.py` - оптимизация для AMD Fury X
- `gpu_chudnovsky.cl` - OpenCL kernel для GPU вычислений

#### 💻 **Нативные реализации**
- `c_pi_wrapper.py` - Python обертка для C++ библиотеки
- `cpu_chudnovsky.cpp` - C++ реализация с GMP библиотекой
- `cpu_chudnovsky.so` - скомпилированная библиотека

#### 🎲 **Другие алгоритмы**
- `bbp_generator.py` - Bailey–Borwein–Plouffe алгоритм для вычисления отдельных цифр

### 🗜️ **Сжатие данных**
- **compression_core.py** - основной класс сжатия (XOR + поиск в π + арифметическое кодирование)
- **compression_types.py** - типы данных для сжатия
- **compression_types_alt.py** - альтернативные реализации

### 📊 **Управление индексами**
- **index_manager.py** - управление индексными файлами и кэшем

### 🎛️ **Утилиты**
- **working_progress.py** - универсальный анимированный прогресс-бар
- **math_utils.py** - математические функции и утилиты
- **file_utils.py** - операции с файлами
- **performance_monitor.py** - мониторинг производительности
- **ascii_progress.py** - ASCII прогресс-бар
- **cpu_monitor.py** - мониторинг загрузки CPU
- **progress_bar.py** - продвинутый прогресс-бар
- **simple_progress.py** - простой прогресс-бар
- **system_info.py** - информация о системе

### 🎯 **Основные модули**
- **archive_operations/** - операции архивации данных
- **extract_operations/** - операции извлечения данных
- **progress_indicators/** - индикаторы прогресса операций
- **archiver_*.py** - различные реализации архиватора
- **dsp_module/** - DSP модуль для обработки сигналов

## 🔄 **Потоки данных в проекте**

### 📥 **Процесс сжатия:**
```
Входные данные → XOR-декорреляция → Адаптивное разбиение → Поиск в π → 
Арифметическое кодирование → Индексный файл
```

### 📤 **Процесс распаковки:**
```
Индексный файл → Декодирование позиций → Извлечение из π → 
XOR-обратная декорреляция → Восстановленные данные
```

### 🎯 **Генерация π:**
```
Запрос → Выбор алгоритма → Проверка кэша → Вычисление → 
Сохранение в кэш → Возврат результата
```

### 🚀 **C++ Core обработка:**
```
Запрос → Умный выбор потоков → Адаптивная стратегия → 
Оптимизированное вычисление → Сохранение результата
```

## 🎮 **Ключевые особенности архитектуры**

### 🚀 **C++ Core**
- **6.4x ускорение vs Python** для 100K цифр
- **Умная адаптивная система** потоков (39/40 ядер)
- **100% загрузка CPU** вместо 30%
- **Универсальная оптимизация** для любого объема
- **Автоматический выбор** оптимальной стратегии

### 🧮 **Алгоритмы π**
- **15+ реализаций** от однопоточных до GPU
- **Автоматический выбор** оптимального алгоритма
- **Кэширование результатов** для ускорения
- **Поддержка различных точностей** вычислений

### 🗜️ **Сжатие**
- **5.2x коэффициент** сжатия (лучше LZMA)
- **Адаптивные блоки** 4-16 байт
- **Многопоточный поиск** в π
- **Арифметическое кодирование** позиций

### 🎯 **Модульность**
- **Четкое разделение** по функциям
- **Унифицированные интерфейсы** алгоритмов
- **Простое расширение** новыми реализациями
- **Обратная совместимость** API

## 📊 **Производительность C++ Core**

### ⚡ **Умная адаптивная система:**
```
Цифр  | Потоки | Время     | Стратегия                    | Загрузка CPU
-------|--------|-----------|------------------------------|-------------
10K    | 40     | 200 мс    | Малый объем - все потоки     | 100%
50K    | 40     | 1,983 мс  | Малый объем - все потоки     | 100%
100K   | 39     | 15,518 мс | Средний объем - N-1 поток    | 100%
200K   | 39     | 122,506 мс| Средний объем - N-1 поток    | 100%
```

### 🎯 **Умные стратегии:**
- **≤50K цифр:** Все потоки (40/40) - максимальная скорость
- **100K-200K цифр:** N-1 потоков (39/40) - оставляем 1 для системы
- **>500K цифр:** Ограничение до 39 потоков для избежания contention
- **1 ядро:** 1 поток (используем его полностью)

---

**🎯 Archivator_Pi** - модульная высокопроизводительная система генерации и сжатия данных с использованием цифр π с умной адаптивной C++ ядром.
