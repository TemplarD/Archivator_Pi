#!/bin/bash

# Системный установщик Pi-Archiver Ultra для Ubuntu 24.04
# Устанавливает программу в систему для глобального доступа

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Константы установки
INSTALL_DIR="/opt/pi-archiver"
CONFIG_DIR="/etc/pi-archiver"
DATA_DIR="/var/lib/pi-archiver"
LOG_DIR="/var/log/pi-archiver"
BIN_DIR="/usr/local/bin"
LIB_DIR="/usr/local/lib/pi-archiver"

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

# Проверка прав
check_sudo() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Этот скрипт требует прав суперпользователя"
        print_info "Используйте: sudo ./install_system.sh"
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
    
    apt update
    apt upgrade -y
    
    print_success "Система обновлена"
}

# Установка системных зависимостей
install_system_deps() {
    print_info "Установка системных зависимостей..."
    
    # Базовые пакеты
    apt install -y \
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
    apt install -y \
        libgmp-dev \
        libmpfr-dev \
        libmpc-dev
    
    # OpenCL
    apt install -y \
        opencl-headers \
        ocl-icd-opencl-dev \
        clinfo
    
    print_success "Системные зависимости установлены"
}

# Создание директорий
create_directories() {
    print_info "Создание системных директорий..."
    
    mkdir -p $INSTALL_DIR
    mkdir -p $CONFIG_DIR
    mkdir -p $DATA_DIR/pi_storage
    mkdir -p $DATA_DIR/indexes
    mkdir -p $LOG_DIR
    mkdir -p $LIB_DIR
    
    # Установка прав
    chmod 755 $INSTALL_DIR
    chmod 755 $CONFIG_DIR
    chmod 755 $DATA_DIR
    chmod 755 $LOG_DIR
    chmod 755 $LIB_DIR
    
    # Права для данных
    chown -R root:root $INSTALL_DIR
    chown -R root:root $CONFIG_DIR
    chown -R root:root $LIB_DIR
    chown -R pi-archiver:pi-archiver $DATA_DIR 2>/dev/null || chown -R $SUDO_USER:$SUDO_USER $DATA_DIR
    chown -R pi-archiver:pi-archiver $LOG_DIR 2>/dev/null || chown -R $SUDO_USER:$SUDO_USER $LOG_DIR
    
    print_success "Системные директории созданы"
}

# Создание пользователя pi-archiver
create_user() {
    print_info "Создание пользователя pi-archiver..."
    
    if ! id "pi-archiver" &>/dev/null; then
        useradd -r -s /bin/false -d $DATA_DIR pi-archiver
        print_success "Пользователь pi-archiver создан"
    else
        print_warning "Пользователь pi-archiver уже существует"
    fi
}

# Установка Python окружения
setup_python_env() {
    print_info "Настройка Python окружения..."
    
    # Создаем виртуальное окружение в системной директории
    python3 -m venv $INSTALL_DIR/venv
    
    # Активируем и устанавливаем зависимости
    source $INSTALL_DIR/venv/bin/activate
    pip install --upgrade pip setuptools wheel
    
    # Копируем requirements и устанавливаем
    cp requirements.txt $INSTALL_DIR/
    pip install -r $INSTALL_DIR/requirements.txt
    
    print_success "Python окружение настроено"
}

# Настройка переменных окружения
setup_environment() {
    print_info "Настройка переменных окружения..."
    
    # Создаем файл окружения
    cat > .env << EOF
# Pi-Archiver Ultra Environment Variables
export PI_ARCHIVER_HOME=/opt/pi-archiver
export PI_CACHE_DIR=/var/lib/pi-archiver/pi_storage
export PI_INDEX_DIR=/var/lib/pi-archiver/indexes
export PI_LOG_DIR=/var/log/pi-archiver
export PI_DEFAULT_OUTPUT_DIR=\$HOME/pi-archives
export OMP_NUM_THREADS=$(nproc)
EOF
    
    # Создаем директорию по умолчанию для архивов
    mkdir -p $HOME/pi-archives
    
    # Добавляем в bashrc (опционально)
    echo "source /opt/pi-archiver/.env" > /opt/pi-archiver/setup_env.sh
    chmod +x /opt/pi-archiver/setup_env.sh
    
    print_success "Переменные окружения настроены"
    print_info "Директория по умолчанию: $HOME/pi-archives"
    print_info "Для активации окружения выполните: source /opt/pi-archiver/setup_env.sh"
}

# Копирование файлов проекта
copy_project_files() {
    print_info "Копирование файлов проекта..."
    
    # Копируем исходники
    cp -r src/ $INSTALL_DIR/
    cp -r tests/ $INSTALL_DIR/
    
    # Копируем документацию
    cp README.md $INSTALL_DIR/
    cp INSTALL.md $INSTALL_DIR/
    cp LICENSE $INSTALL_DIR/
    
    # Копируем requirements
    cp requirements.txt $INSTALL_DIR/
    
    # Установка прав
    chown -R root:root $INSTALL_DIR
    chmod -R 755 $INSTALL_DIR
    
    print_success "Файлы проекта скопированы"
}

# Компиляция C++ компонентов
compile_cpp() {
    print_info "Компиляция C++ компонентов..."
    
    cd $INSTALL_DIR/src/pi_generator/
    
    # Компилируем генератор
    g++ -O3 -std=c++17 -fopenmp cpu_chudnovsky.cpp -lgmp -lgmpxx -o pi_generator_cpu
    
    # Копируем в библиотечную директорию
    cp pi_generator_cpu $LIB_DIR/
    chmod +x $LIB_DIR/pi_generator_cpu
    
    cd - > /dev/null
    
    print_success "C++ компоненты скомпилированы"
}

# Создание системных исполняемых файлов
create_executables() {
    print_info "Создание системных исполняемых файлов..."
    
    # Создаем pi-archiver
    cat > $BIN_DIR/pi-archiver << 'EOF'
#!/bin/bash
# Pi-Archiver Ultra System Launcher

# Активируем виртуальное окружение
source /opt/pi-archiver/venv/bin/activate

# Устанавливаем переменные окружения
export PI_ARCHIVER_HOME="/opt/pi-archiver"
export PI_CACHE_DIR="/var/lib/pi-archiver/pi_storage"
export PI_INDEX_DIR="/var/lib/pi-archiver/indexes"
export PI_LOG_DIR="/var/log/pi-archiver"
export OMP_NUM_THREADS=$(nproc)

# Запускаем основной модуль
python3 /opt/pi-archiver/src/main/archiver_main.py "$@"
EOF

    # Создаем pi-benchmark
    cat > $BIN_DIR/pi-benchmark << 'EOF'
#!/bin/bash
# Pi-Archiver Ultra Benchmark Launcher

# Активируем виртуальное окружение
source /opt/pi-archiver/venv/bin/activate

# Устанавливаем переменные окружения
export PI_ARCHIVER_HOME="/opt/pi-archiver"
export PI_CACHE_DIR="/var/lib/pi-archiver/pi_storage"
export PI_INDEX_DIR="/var/lib/pi-archiver/indexes"
export PI_LOG_DIR="/var/log/pi-archiver"
export OMP_NUM_THREADS=$(nproc)

# Запускаем бенчмарк
python3 /opt/pi-archiver/tests/performance_tests/performance_benchmark.py
EOF

    # Создаем pi-generator
    cat > $BIN_DIR/pi-generator << 'EOF'
#!/bin/bash
# Pi-Archiver Ultra Generator

# Активируем виртуальное окружение
source /opt/pi-archiver/venv/bin/activate

# Устанавливаем переменные окружения
export PI_ARCHIVER_HOME="/opt/pi-archiver"
export PI_CACHE_DIR="/var/lib/pi-archiver/pi_storage"
export PI_INDEX_DIR="/var/lib/pi-archiver/indexes"
export PI_LOG_DIR="/var/log/pi-archiver"

# Запускаем генератор
python3 /opt/pi-archiver/src/pi_generator/pi_generator.py "$@"
EOF

    # Делаем исполняемыми
    chmod +x $BIN_DIR/pi-archiver
    chmod +x $BIN_DIR/pi-benchmark
    chmod +x $BIN_DIR/pi-generator
    
    print_success "Системные исполняемые файлы созданы"
}

# Создание конфигурационного файла
create_config() {
    print_info "Создание конфигурационного файла..."
    
    cat > $CONFIG_DIR/config.yaml << 'EOF'
# Pi-Archiver Ultra Configuration File

# Базовые настройки
pi_archiver:
  home_dir: "/opt/pi-archiver"
  cache_dir: "/var/lib/pi-archiver/pi_storage"
  index_dir: "/var/lib/pi-archiver/indexes"
  log_dir: "/var/log/pi-archiver"

# Настройки производительности
performance:
  default_pi_precision: 1000000
  max_workers: $(nproc)
  use_gpu: true
  gpu_memory_limit: "4GB"

# Настройки кэша
cache:
  max_size_gb: 10
  cleanup_interval_hours: 24
  auto_cleanup: true

# Настройки логирования
logging:
  level: "INFO"
  max_file_size_mb: 100
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Безопасность
security:
  max_file_size_mb: 1024
  allowed_extensions: [".txt", ".bin", ".dat", ".doc", ".pdf"]
  scan_for_malware: false
EOF

    chown root:root $CONFIG_DIR/config.yaml
    chmod 644 $CONFIG_DIR/config.yaml
    
    print_success "Конфигурационный файл создан"
}

# Создание systemd сервиса (опционально)
create_service() {
    print_info "Создание systemd сервиса..."
    
    cat > /etc/systemd/system/pi-archiver.service << 'EOF'
[Unit]
Description=Pi-Archiver Ultra Daemon
After=network.target

[Service]
Type=simple
User=pi-archiver
Group=pi-archiver
WorkingDirectory=/opt/pi-archiver
Environment=PI_ARCHIVER_HOME=/opt/pi-archiver
Environment=PI_CACHE_DIR=/var/lib/pi-archiver/pi_storage
Environment=PI_INDEX_DIR=/var/lib/pi-archiver/indexes
Environment=PI_LOG_DIR=/var/log/pi-archiver
ExecStart=/opt/pi-archiver/venv/bin/python /opt/pi-archiver/src/main/archiver_main.py daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable pi-archiver
    
    print_success "Systemd сервис создан и включен"
}

# Создание man страниц
create_man_pages() {
    print_info "Создание man страниц..."
    
    mkdir -p /usr/local/share/man/man1
    
    # Man страница для pi-archiver
    cat > /usr/local/share/man/man1/pi-archiver.1 << 'EOF'
.TH PI-ARCHIVER 1 "2024" "Pi-Archiver Ultra" "User Commands"
.SH NAME
pi-archiver \- архиватор на основе числа \[pi]
.SH SYNOPSIS
.B pi-archiver
[\fIOPTIONS\fR] \fICOMMAND\fR \fIARGS\fR
.SH DESCRIPTION
Pi-Archiver Ultra это высокопроизводительный архиватор, использующий число \[pi] в качестве универсальной базы данных.
.SH COMMANDS
.TP
\fBarchive\fR \fIfile\fR
Архивировать указанный файл
.TP
\fBextract\fR \fIarchive\fR
Извлечь архив
.TP
\fBinfo\fR \fIarchive\fR
Показать информацию об архиве
.TP
\fBlist\fR
Список всех архивов
.SH OPTIONS
.TP
\fB\--gpu\fR
Использовать GPU ускорение
.TP
\fB\--precision\fR \fIN\fR
Количество цифр \[pi] (по умолчанию: 1000000)
.TP
\fB\--workers\fR \fIN\fR
Количество рабочих потоков
.SH EXAMPLES
Архивировать файл:
.RS
.nf
pi-archiver archive document.txt
.fi
.RE
Извлечь архив:
.RS
.nf
pi-archiver extract archive.piarc
.fi
.RE
.SH SEE ALSO
pi-benchmark(1), pi-generator(1)
EOF

    mandb -q
    
    print_success "Man страницы созданы"
}

# Настройка автодополнения
setup_completion() {
    print_info "Настройка автодополнения..."
    
    # Bash completion
    cat > /etc/bash_completion.d/pi-archiver << 'EOF'
_pi_archiver_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    if [[ ${cur} == * ]] ; then
        COMPREPLY=( $(compgen -W "archive extract info list --help --gpu --precision --workers" -- ${cur}) )
        return 0
    fi
}
complete -F _pi_archiver_completion pi-archiver
complete -F _pi_archiver_completion pi-benchmark
complete -F _pi_archiver_completion pi-generator
EOF
    
    print_success "Автодополнение настроено"
}

# Проверка установки
verify_installation() {
    print_info "Проверка установки..."
    
    # Проверяем исполняемые файлы
    if command -v pi-archiver &> /dev/null; then
        print_success "pi-archiver доступен в PATH"
    else
        print_error "pi-archiver не найден в PATH"
    fi
    
    # Проверяем виртуальное окружение
    if [ -d "$INSTALL_DIR/venv" ]; then
        print_success "Виртуальное окружение создано"
    else
        print_error "Виртуальное окружение не найдено"
    fi
    
    # Проверяем конфигурацию
    if [ -f "$CONFIG_DIR/config.yaml" ]; then
        print_success "Конфигурационный файл создан"
    else
        print_error "Конфигурационный файл не найден"
    fi
    
    # Тестовый запуск
    source $INSTALL_DIR/venv/bin/activate
    python3 -c "
import sys
sys.path.append('$INSTALL_DIR/src')
try:
    from pi_generator.pi_generator import PiGenerator
    print('✓ Модуль генератора загружен')
except Exception as e:
    print(f'✗ Ошибка: {e}')
"
    
    print_success "Проверка установки завершена"
}

# Показ справки
show_help() {
    echo "Pi-Archiver Ultra System Installer"
    echo ""
    echo "Использование: sudo $0 [опции]"
    echo ""
    echo "Опции:"
    echo "  -h, --help         Показать эту справку"
    echo "  --no-service        Не создавать systemd сервис"
    echo "  --no-completion     Не настраивать автодополнение"
    echo "  --uninstall         Удалить Pi-Archiver Ultra"
    echo ""
    echo "Примеры:"
    echo "  sudo $0                    # Полная установка"
    echo "  sudo $0 --no-service        # Без systemd сервиса"
    echo "  sudo $0 --uninstall         # Удаление"
}

# Удаление программы
uninstall() {
    print_info "Удаление Pi-Archiver Ultra..."
    
    # Остановка сервиса
    systemctl stop pi-archiver 2>/dev/null || true
    systemctl disable pi-archiver 2>/dev/null || true
    
    # Удаление файлов
    rm -rf $INSTALL_DIR
    rm -rf $CONFIG_DIR
    rm -rf $LIB_DIR
    rm -f $BIN_DIR/pi-archiver
    rm -f $BIN_DIR/pi-benchmark
    rm -f $BIN_DIR/pi-generator
    rm -f /etc/systemd/system/pi-archiver.service
    rm -f /etc/bash_completion.d/pi-archiver
    
    # Удаление пользователя (опционально)
    read -p "Удалить пользователя pi-archiver? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        userdel -r pi-archiver 2>/dev/null || true
    fi
    
    # Обновление systemd
    systemctl daemon-reload
    
    # Удаление man страниц
    rm -f /usr/local/share/man/man1/pi-archiver.1
    mandb -q
    
    print_success "Pi-Archiver Ultra удален"
}

# Парсинг аргументов
CREATE_SERVICE=true
SETUP_COMPLETION=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --no-service)
            CREATE_SERVICE=false
            shift
            ;;
        --no-completion)
            SETUP_COMPLETION=false
            shift
            ;;
        --uninstall)
            uninstall
            exit 0
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
    print_info "Начало системной установки Pi-Archiver Ultra"
    print_info "Время установки: $(date)"
    
    check_sudo
    check_ubuntu_version
    update_system
    install_system_deps
    create_user
    create_directories
    setup_python_env
    copy_project_files
    compile_cpp
    create_executables
    create_config
    
    if [ "$CREATE_SERVICE" = true ]; then
        create_service
    else
        print_warning "Systemd сервис не создан"
    fi
    
    create_man_pages
    
    if [ "$SETUP_COMPLETION" = true ]; then
        setup_completion
    else
        print_warning "Автодополнение не настроено"
    fi
    
    verify_installation
    
    print_success "Системная установка Pi-Archiver Ultra завершена!"
    print_info ""
    print_info "Программа установлена в: $INSTALL_DIR"
    print_info "Конфигурация: $CONFIG_DIR"
    print_info "Данные: $DATA_DIR"
    print_info "Логи: $LOG_DIR"
    print_info ""
    print_info "Использование:"
    print_info "  pi-archiver archive file.txt"
    print_info "  pi-benchmark"
    print_info "  pi-generator --digits 1000000"
    print_info ""
    if [ "$CREATE_SERVICE" = true ]; then
        print_info "Для запуска сервиса: sudo systemctl start pi-archiver"
    fi
}

# Запуск установки
main "$@"
