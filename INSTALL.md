# Инструкция по установке и использованию Pi-Archiver Ultra

## Системные требования

### Минимальные требования
- **ОС:** Linux (Ubuntu 18.04+, CentOS 7+)
- **Python:** 3.8 или выше
- **Память:** 4GB RAM
- **Диск:** 10GB свободного места
- **CPU:** 2+ ядра

### Рекомендуемые требования
- **ОС:** Linux (Ubuntu 20.04+)
- **Python:** 3.9+
- **Память:** 16GB+ RAM
- **Диск:** 100GB+ SSD для хранения цифр π
- **CPU:** Intel Xeon E5-2666 или аналогичный (20+ потоков)
- **GPU:** AMD Fury X (опционально для ускорения)

## Установка зависимостей

### 1. Системные зависимости

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3-dev python3-pip build-essential
sudo apt install -y libgmp-dev libmpfr-dev libmpc-dev
sudo apt install -y ocl-icd-opencl-dev opencl-headers
```

**CentOS/RHEL:**
```bash
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel python3-pip
sudo yum install -y gmp-devel mpfr-devel libmpc-devel
sudo yum install -y opencl-headers ocl-icd-devel
```

### 2. Python зависимости

```bash
# Создаем виртуальное окружение
python3 -m venv pi_archiver_env
source pi_archiver_env/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Проверка OpenCL (опционально)

```bash
python -c "import pyopencl as cl; print('OpenCL доступен:', len(cl.get_platforms()), 'платформ')"
```

## Сборка C++ компонентов

### 1. Компиляция генератора π

```bash
cd src/pi_generator/

# Компиляция CPU версии
g++ -O3 -std=c++17 -fopenmp cpu_chudnovsky.cpp -lgmp -lgmpxx -o pi_generator_cpu

# Компиляция с оптимизациями для Xeon
g++ -O3 -march=native -std=c++17 -fopenmp cpu_chudnovsky.cpp -lgmp -lgmpxx -o pi_generator_optimized
```

### 2. Проверка компиляции

```bash
./pi_generator_cpu
# Должен вывести первую 1000 цифр π
```

## Настройка окружения

### 1. Создание директорий

```bash
mkdir -p data/pi_storage
mkdir -p data/indexes
mkdir -p logs
```

### 2. Настройка переменных окружения

```bash
# Добавить в ~/.bashrc
export PI_ARCHIVER_HOME=/path/to/Pi-Archiver-Ultra
export PI_CACHE_DIR=$PI_ARCHIVER_HOME/data/pi_storage
export PI_INDEX_DIR=$PI_ARCHIVER_HOME/data/indexes
export OCL_PLATFORM=AMD  # Для AMD GPU
```

### 3. Проверка установки

```bash
python src/main/archiver_main.py --help
```

## Использование

### 1. Базовые операции

**Архивация файла:**
```bash
python src/main/archiver_main.py archive document.txt
```

**Архивация с указанием имени:**
```bash
python src/main/archiver_main.py archive document.txt -o my_archive.piarc
```

**Архивация с GPU ускорением:**
```bash
python src/main/archiver_main.py archive large_file.bin --gpu --precision 10000000
```

**Архивация нескольких файлов:**
```bash
python src/main/archiver_main.py archive file1.txt file2.bin file3.dat -o collection.piarc
```

### 2. Извлечение архивов

**Извлечение в текущую директорию:**
```bash
python src/main/archiver_main.py extract my_archive.piarc
```

**Извлечение в указанную директорию:**
```bash
python src/main/archiver_main.py extract my_archive.piarc -o extracted_files/
```

### 3. Работа с архивами

**Информация об архиве:**
```bash
python src/main/archiver_main.py info my_archive.piarc
```

**Список всех архивов:**
```bash
python src/main/archiver_main.py list
```

### 4. Тестирование производительности

**Запуск бенчмарков:**
```bash
python tests/performance_tests/performance_benchmark.py
```

**Запуск тестов:**
```bash
pytest tests/ -v
```

## Оптимизация производительности

### 1. CPU оптимизации

**Для Intel Xeon E5-2666:**
```bash
# Использование всех ядер
export OMP_NUM_THREADS=20

# Настройка NUMA
numactl --interleave=all python src/main/archiver_main.py archive large_file.bin
```

### 2. GPU оптимизации

**Для AMD Fury X:**
```bash
# Установка переменных для AMD GPU
export GPU_MAX_ALLOC_PERCENT=100
export GPU_USE_SYNC_OBJECTS=1

# Запуск с GPU
python src/main/archiver_main.py archive file.bin --gpu --workers 4096
```

### 3. Память и кэш

**Настройка кэша π:**
```bash
# Предварительная генерация π
python src/pi_generator/pi_generator.py --digits 100000000 --cache

# Настройка размера кэша
export PI_CACHE_SIZE_MB=4096  # Для Fury X HBM
```

## Мониторинг и отладка

### 1. Логирование

```bash
# Включение детального логирования
export PI_LOG_LEVEL=DEBUG
export PI_LOG_FILE=logs/pi_archiver.log
```

### 2. Мониторинг ресурсов

```bash
# Мониторинг в реальном времени
watch -n 1 'ps aux | grep archiver'

# Мониторинг GPU (если доступно)
watch -n 1 'rocm-smi'
```

### 3. Профилирование

```bash
# Профилирование CPU
python -m cProfile -o profile.stats src/main/archiver_main.py archive test_file.txt

# Анализ результатов
python -c "import pstats; p=pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

## Решение проблем

### 1. Общие ошибки

**Ошибка импорта GMP:**
```bash
# Переустановка GMP
sudo apt install --reinstall libgmp-dev libgmpxx-dev
pip uninstall gmpy2
pip install gmpy2
```

**Ошибка OpenCL:**
```bash
# Проверка драйверов
lspci | grep -i vga
clinfo

# Переустановка OpenCL
sudo apt install --reinstall opencl-headers ocl-icd-opencl-dev
```

### 2. Проблемы с памятью

**Недостаточно памяти для π:**
```bash
# Увеличение swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. Проблемы с производительностью

**Медленная генерация π:**
```bash
# Использование меньшей точности для тестов
python src/main/archiver_main.py archive test.txt --precision 100000
```

**Медленный поиск:**
```bash
# Увеличение количества потоков
export OMP_NUM_THREADS=20
python src/main/archiver_main.py archive file.bin --workers 20
```

## Продвинутое использование

### 1. Распределенная генерация π

```bash
# На нескольких машинах
# Машина 1:
python src/pi_generator/distributed_generator.py --node 1 --total-nodes 4 --digits 1000000000

# Машина 2:
python src/pi_generator/distributed_generator.py --node 2 --total-nodes 4 --digits 1000000000
# и т.д.
```

### 2. Кастомные алгоритмы

```bash
# Использование BWT+FM-Index
python src/main/archiver_main.py archive file.txt --algorithm bwt_fm

# Квантово-подобное сжатие
python src/main/archiver_main.py archive file.txt --quantum
```

### 3. Интеграция с другими системами

**API сервер:**
```bash
python src/api/server.py --port 8080
```

**Библиотека Python:**
```python
from pi_archiver import PiArchiverUltra

archiver = PiArchiverUltra()
archiver.archive_file("data.txt", "archive.piarc")
```

## Обновление и обслуживание

### 1. Обновление

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 2. Очистка кэша

```bash
python src/pi_generator/pi_generator.py --cleanup
```

### 3. Проверка целостности

```bash
python src/main/archiver_main.py verify my_archive.piarc
```

## Поддержка и разработка

### 1. Внесение изменений

```bash
# Создание ветки
git checkout -b feature/new-algorithm

# Тестирование
pytest tests/

# Коммит
git commit -m "Add new compression algorithm"
git push origin feature/new-algorithm
```

### 2. Отчеты о проблемах

Создайте issue в репозитории с:
- Версией системы
- Версией Python
- Логами ошибок
- Примером воспроизведения

### 3. Контрибьюторы

Для участия в разработке:
1. Fork репозитория
2. Создайте feature branch
3. Добавьте тесты
4. Отправьте Pull Request
