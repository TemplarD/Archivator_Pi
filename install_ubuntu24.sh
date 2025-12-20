#!/bin/bash

# Скрипт установки Pi-Archiver Ultra для Ubuntu 24.04
# Автор: Pi-Archiver Ultra Team
# Версия: 1.0

set -e  # Выход при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав суперпользователя
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Не запускайте этот скрипт с правами суперпользователя!"
        print_info "Используйте обычного пользователя. Скрипт запросит пароль при необходимости."
        exit 1
    fi
}

# Проверка версии Ubuntu
check_ubuntu_version() {
    print_info "Проверка версии Ubuntu..."
    
    if ! grep -q "Ubuntu 24.04" /etc/os-release; then
        print_warning "Этот скрипт оптимизирован для Ubuntu 24.04"
        read -p "Продолжить установку? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Версия Ubuntu проверена"
}

# Обновление системы
update_system() {
    print_info "Обновление системы..."
    
    sudo apt update
    sudo apt upgrade -y
    
    print_success "Система обновлена"
}

# Установка системных зависимостей
install_system_deps() {
    print_info "Установка системных зависимостей..."
    
    # Базовые пакеты для разработки
    sudo apt install -y \
        build-essential \
        cmake \
        git \
        wget \
        curl \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        pkg-config
    
    # Математические библиотеки
    sudo apt install -y \
        libgmp-dev \
        libmpfr-dev \
        libmpc-dev
    
    # OpenCL для GPU ускорения
    sudo apt install -y \
        opencl-headers \
        ocl-icd-opencl-dev \
        clinfo
    
    # Дополнительные утилиты
    sudo apt install -y \
        htop \
        tree \
        jq
    
    print_success "Системные зависимости установлены"
}

# Проверка и установка Python
setup_python() {
    print_info "Настройка Python окружения..."
    
    # Проверяем версию Python
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_info "Найден Python: $PYTHON_VERSION"
    
    # Проверяем, что версия >= 3.8
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Версия Python подходит"
    else
        print_error "Требуется Python 3.8 или выше"
        exit 1
    fi
}

# Создание виртуального окружения
create_venv() {
    print_info "Создание виртуального окружения..."
    
    if [ ! -d "pi_archiver_env" ]; then
        python3 -m venv pi_archiver_env
        print_success "Виртуальное окружение создано"
    else
        print_warning "Виртуальное окружение уже существует"
    fi
}

# Активация окружения и установка Python зависимостей
install_python_deps() {
    print_info "Установка Python зависимостей..."
    
    # Активируем виртуальное окружение
    source pi_archiver_env/bin/activate
    
    # Обновляем pip
    pip install --upgrade pip setuptools wheel
    
    # Устанавливаем зависимости
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python зависимости установлены"
    else
        print_error "Файл requirements.txt не найден!"
        exit 1
    fi
}

# Компиляция C++ компонентов
compile_cpp() {
    print_info "Компиляция C++ компонентов..."
    
    # Переходим в директорию с исходниками
    cd src/pi_generator/
    
    # Компилируем генератор π
    if command -v g++ &> /dev/null; then
        g++ -O3 -std=c++17 -fopenmp cpu_chudnovsky.cpp -lgmp -lgmpxx -o pi_generator_cpu
        
        if [ -f "pi_generator_cpu" ]; then
            print_success "CPU генератор скомпилирован"
            
            # Тестовая компиляция
            if [ -x "pi_generator_cpu" ]; then
                print_info "Проверка работоспособности..."
                timeout 10s ./pi_generator_cpu > /dev/null 2>&1 && \
                    print_success "CPU генератор работает корректно" || \
                    print_warning "CPU генератор требует дополнительной настройки"
            fi
        else
            print_error "Ошибка компиляции CPU генератора"
        fi
    else
        print_warning "g++ не найден, пропускаем компиляцию C++ компонентов"
    fi
    
    # Возвращаемся в корень проекта
    cd ../../
}

# Создание директорий проекта
create_directories() {
    print_info "Создание директорий проекта..."
    
    mkdir -p data/pi_storage
    mkdir -p data/indexes
    mkdir -p logs
    mkdir -p temp
    
    print_success "Директории созданы"
}

# Настройка переменных окружения
setup_environment() {
    print_info "Настройка переменных окружения..."
    
    # Создаем файл окружения
    cat > .env << EOF
# Pi-Archiver Ultra Environment Variables
export PI_ARCHIVER_HOME=$(pwd)
export PI_CACHE_DIR=$(pwd)/data/pi_storage
export PI_INDEX_DIR=$(pwd)/data/indexes
export PI_LOG_DIR=$(pwd)/logs
export OMP_NUM_THREADS=$(nproc)
EOF
    
    # Добавляем в bashrc (опционально)
    echo "source $(pwd)/.env" > setup_env.sh
    chmod +x setup_env.sh
    
    print_success "Переменные окружения настроены"
    print_info "Для активации окружения выполните: source setup_env.sh"
}

# Проверка OpenCL
check_opencl() {
    print_info "Проверка OpenCL..."
    
    if command -v clinfo &> /dev/null; then
        if clinfo | grep -q "Number of platforms"; then
            PLATFORMS=$(clinfo | grep "Number of platforms" | awk '{print $4}')
            print_success "OpenCL доступен. Найдено платформ: $PLATFORMS"
            
            # Показываем информацию об устройствах
            clinfo | grep -A 5 "Platform Name" || true
        else
            print_warning "OpenCL установлен, но устройства не найдены"
        fi
    else
        print_warning "OpenCL не доступен. GPU ускорение будет отключено"
    fi
}

# Запуск тестов
run_tests() {
    print_info "Запуск базовых тестов..."
    
    # Активируем окружение
    source pi_archiver_env/bin/activate
    
    # Тест импорта модулей
    python3 -c "
import sys
sys.path.append('src')
try:
    from pi_generator.pi_generator import PiGenerator
    print('✓ Модуль генератора π загружен')
except Exception as e:
    print(f'✗ Ошибка загрузки генератора π: {e}')

try:
    from search_engine.pi_search import PiSearchEngine
    print('✓ Модуль поиска загружен')
except Exception as e:
    print(f'✗ Ошибка загрузки поиска: {e}')

try:
    from compression.compression_core import CompressionCore
    print('✓ Модуль сжатия загружен')
except Exception as e:
    print(f'✗ Ошибка загрузки сжатия: {e}')
"
    
    print_success "Базовые тесты завершены"
}

# Создание ярлыков для запуска
create_shortcuts() {
    print_info "Создание ярлыков для запуска..."
    
    cat > run_archiver.sh << 'EOF'
#!/bin/bash
# Pi-Archiver Ultra Launcher

# Активируем окружение
source $(dirname "$0")/pi_archiver_env/bin/activate
source $(dirname "$0")/.env

# Запускаем архиватор
python3 src/main/archiver_main.py "$@"
EOF
    
    chmod +x run_archiver.sh
    
    cat > run_benchmark.sh << 'EOF'
#!/bin/bash
# Pi-Archiver Ultra Benchmark Launcher

# Активируем окружение
source $(dirname "$0")/pi_archiver_env/bin/activate
source $(dirname "$0")/.env

# Запускаем бенчмарк
python3 tests/performance_tests/performance_benchmark.py
EOF
    
    chmod +x run_benchmark.sh
    
    print_success "Ярлыки созданы:"
    print_info "  ./run_archiver.sh - запуск архиватора"
    print_info "  ./run_benchmark.sh - запуск бенчмарков"
}

# Финальная проверка
final_check() {
    print_info "Финальная проверка установки..."
    
    # Проверяем структуру директорий
    REQUIRED_DIRS=("src" "data" "tests" "pi_archiver_env")
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            echo "✓ $dir"
        else
            echo "✗ $dir отсутствует"
        fi
    done
    
    # Проверяем ключевые файлы
    REQUIRED_FILES=("requirements.txt" "README.md" "INSTALL.md")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "✓ $file"
        else
            echo "✗ $file отсутствует"
        fi
    done
    
    print_success "Установка завершена!"
}

# Функция показа справки
show_help() {
    echo "Pi-Archiver Ultra Installer for Ubuntu 24.04"
    echo ""
    echo "Использование: $0 [опции]"
    echo ""
    echo "Опции:"
    echo "  -h, --help     Показать эту справку"
    echo "  --no-gpu        Пропустить установку OpenCL"
    echo "  --no-compile    Пропустить компиляцию C++ компонентов"
    echo "  --dev           Установка в режиме разработчика"
    echo ""
    echo "Примеры:"
    echo "  $0                    # Полная установка"
    echo "  $0 --no-gpu          # Без GPU поддержки"
    echo "  $0 --dev             # Для разработчиков"
}

# Парсинг аргументов
INSTALL_GPU=true
COMPILE_CPP=true
DEV_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --no-gpu)
            INSTALL_GPU=false
            shift
            ;;
        --no-compile)
            COMPILE_CPP=false
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            print_error "Неизвестная опция: $1"
            show_help
            exit 1
            ;;
    esac
done

# Основной процесс установки
main() {
    print_info "Начало установки Pi-Archiver Ultra для Ubuntu 24.04"
    print_info "Время установки: $(date)"
    
    check_sudo
    check_ubuntu_version
    update_system
    
    if [ "$INSTALL_GPU" = true ]; then
        install_system_deps
    else
        print_info "Установка без GPU поддержки"
        sudo apt install -y build-essential python3 python3-dev python3-pip python3-venv libgmp-dev
    fi
    
    setup_python
    create_venv
    install_python_deps
    
    if [ "$COMPILE_CPP" = true ]; then
        compile_cpp
    else
        print_info "Пропуск компиляции C++ компонентов"
    fi
    
    create_directories
    setup_environment
    
    if [ "$INSTALL_GPU" = true ]; then
        check_opencl
    fi
    
    run_tests
    create_shortcuts
    final_check
    
    print_success "Установка Pi-Archiver Ultra завершена!"
    print_info ""
    print_info "Для начала работы:"
    print_info "1. Активируйте окружение: source setup_env.sh"
    print_info "2. Запустите архиватор: ./run_archiver.sh archive ваш_файл"
    print_info "3. Запустите бенчмарк: ./run_benchmark.sh"
    print_info ""
    print_info "Документация: README.md"
    print_info "Подробная инструкция: INSTALL.md"
}

# Запуск установки
main "$@"
