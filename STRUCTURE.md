# 📁 Структура проекта Pi-Archiver Ultra

## 🎯 Обзор архитектуры

```
Pi-Archiver Ultra/
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
│   │   └── performance_tests/       # Тесты производительности
│   │       └── performance_benchmark.py
│   └── test_final_optimization.py  # Финальные тесты оптимизации
│
├── 💾 Данные и кэш
│   ├── data/                        # Входные данные для сжатия
│   ├── extracted/                   # Распакованные данные
│   └── pi_storage/                  # Хранилище цифр π
│       └── pi_1000000_digits.txt    # 1М цифр π (кэш)
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
        ├── 🗜️ Сжатие данных
        │   └── compression/
        │       ├── __init__.py
        │       ├── compression_core.py
        │       │   └── CompressionCore (основной класс сжатия)
        │       ├── compression_types.py
        │       │   └── Типы данных для сжатия
        │       └── compression_types_alt.py
        │           └── Альтернативные типы сжатия
        │
        ├── 📊 Управление индексами
        │   └── index_manager/
        │       ├── __init__.py
        │       └── index_manager.py
        │           └── IndexManager (управление индексами)
        │
        ├── 🎛️ Утилиты и прогресс-бары
        │   └── utils/
        │       ├── __init__.py
        │       ├── working_progress.py
        │       │   └── Универсальный анимированный прогресс-бар
        │       ├── math_utils.py
        │       │   └── Математические утилиты
        │       ├── file_utils.py
        │       │   └── Работа с файлами
        │       └── performance_monitor.py
        │           └── Мониторинг производительности
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
- **test_final_optimization.py** - комплексные тесты оптимизации

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

## 🎮 **Ключевые особенности архитектуры**

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

---

**🎯 Pi-Archiver Ultra** - модульная высокопроизводительная система генерации и сжатия данных с использованием цифр π.
