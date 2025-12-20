#!/bin/bash

# Скрипт удаления Pi-Archiver Ultra
# Полное удаление программы и всех компонентов

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
        print_info "Используйте: sudo ./uninstall.sh"
        exit 1
    fi
}

# Остановка сервисов
stop_services() {
    print_info "Остановка сервисов..."
    
    # Останавливаем systemd сервис
    systemctl stop pi-archiver 2>/dev/null || true
    systemctl disable pi-archiver 2>/dev/null || true
    
    print_success "Сервисы остановлены"
}

# Удаление файлов программы
remove_program_files() {
    print_info "Удаление файлов программы..."
    
    # Удаляем основную директорию
    if [ -d "/opt/pi-archiver" ]; then
        rm -rf /opt/pi-archiver
        print_success "Программа удалена из /opt/pi-archiver"
    else
        print_warning "Программа не найдена в /opt/pi-archiver"
    fi
    
    # Удаляем исполняемые файлы
    rm -f /usr/local/bin/pi-archiver
    rm -f /usr/local/bin/pi-benchmark
    rm -f /usr/local/bin/pi-generator
    
    print_success "Исполняемые файлы удалены"
}

# Удаление конфигурации
remove_config() {
    print_info "Удаление конфигурации..."
    
    # Удаляем конфигурационную директорию
    if [ -d "/etc/pi-archiver" ]; then
        rm -rf /etc/pi-archiver
        print_success "Конфигурация удалена"
    fi
    
    # Удаляем systemd сервис
    rm -f /etc/systemd/system/pi-archiver.service
    systemctl daemon-reload
    
    print_success "Системные сервисы удалены"
}

# Удаление данных (с подтверждением)
remove_data() {
    print_info "Удаление данных..."
    
    # Спрашиваем про данные
    read -p "Удалить все архивы и данные? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Удаляем директорию данных
        if [ -d "/var/lib/pi-archiver" ]; then
            rm -rf /var/lib/pi-archiver
            print_success "Данные удалены"
        fi
        
        # Удаляем директорию по умолчанию
        if [ -d "$HOME/pi-archives" ]; then
            rm -rf "$HOME/pi-archives"
            print_success "Директория по умолчанию удалена"
        fi
        
        # Удаляем логи
        if [ -d "/var/log/pi-archiver" ]; then
            rm -rf /var/log/pi-archiver
            print_success "Логи удалены"
        fi
    else
        print_warning "Данные сохранены"
        print_info "Данные находятся в:"
        print_info "  /var/lib/pi-archiver"
        print_info "  $HOME/pi-archives"
        print_info "  /var/log/pi-archiver"
    fi
}

# Удаление пользователя
remove_user() {
    print_info "Удаление пользователя pi-archiver..."
    
    read -p "Удалить пользователя pi-archiver? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if id "pi-archiver" &>/dev/null; then
            userdel -r pi-archiver 2>/dev/null || true
            print_success "Пользователь pi-archiver удален"
        else
            print_warning "Пользователь pi-archiver не найден"
        fi
    else
        print_warning "Пользователь pi-archiver сохранен"
    fi
}

# Удаление автодополнения
remove_completion() {
    print_info "Удаление автодополнения..."
    
    rm -f /etc/bash_completion.d/pi-archiver
    
    print_success "Автодополнение удалено"
}

# Удаление man страниц
remove_man_pages() {
    print_info "Удаление man страниц..."
    
    rm -f /usr/local/share/man/man1/pi-archiver.1
    
    print_success "Man страницы удалены"
}

# Удаление системных зависимостей (опционально)
remove_dependencies() {
    print_info "Удаление системных зависимостей..."
    
    read -p "Удалить системные зависимости? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apt remove --purge -y \
            build-essential \
            cmake \
            python3-dev \
            python3-pip \
            python3-venv \
            pkg-config \
            libgmp-dev \
            libmpfr-dev \
            libmpc-dev \
            opencl-headers \
            ocl-icd-opencl-dev \
            clinfo
        
        apt autoremove -y
        apt autoclean
        
        print_success "Системные зависимости удалены"
    else
        print_warning "Системные зависимости сохранены"
    fi
}

# Очистка окружения
cleanup_environment() {
    print_info "Очистка окружения..."
    
    # Удаляем из bashrc если добавлено
    if grep -q "pi-archiver" ~/.bashrc; then
        sed -i '/pi-archiver/d' ~/.bashrc
        print_success "Окружение очищено"
    fi
}

# Проверка полного удаления
verify_removal() {
    print_info "Проверка удаления..."
    
    remaining_items=()
    
    # Проверяем основные директории
    [ -d "/opt/pi-archiver" ] && remaining_items+=("/opt/pi-archiver")
    [ -d "/etc/pi-archiver" ] && remaining_items+=("/etc/pi-archiver")
    [ -f "/usr/local/bin/pi-archiver" ] && remaining_items+=("/usr/local/bin/pi-archiver")
    
    if [ ${#remaining_items[@]} -eq 0 ]; then
        print_success "Pi-Archiver Ultra полностью удален"
    else
        print_warning "Найдены оставшиеся компоненты:"
        for item in "${remaining_items[@]}"; do
            echo "  $item"
        done
    fi
}

# Показ справки
show_help() {
    echo "Pi-Archiver Ultra Uninstaller"
    echo ""
    echo "Использование: sudo ./uninstall.sh [опции]"
    echo ""
    echo "Опции:"
    echo "  -h, --help         Показать эту справку"
    echo "  --keep-data         Сохранить данные и архивы"
    echo "  --keep-deps        Сохранить системные зависимости"
    echo "  --full             Полное удаление со всем"
    echo ""
    echo "Примеры:"
    echo "  sudo ./uninstall.sh              # Интерактивное удаление"
    echo "  sudo ./uninstall.sh --keep-data    # Удалить программу, сохранить данные"
    echo "  sudo ./uninstall.sh --full         # Полное удаление без вопросов"
}

# Парсинг аргументов
KEEP_DATA=false
KEEP_DEPS=false
FULL_REMOVAL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --keep-data)
            KEEP_DATA=true
            shift
            ;;
        --keep-deps)
            KEEP_DEPS=true
            shift
            ;;
        --full)
            FULL_REMOVAL=true
            shift
            ;;
        *)
            print_error "Неизвестная опция: $1"
            show_help
            exit 1
            ;;
    esac
done

# Основной процесс удаления
main() {
    print_info "Начало удаления Pi-Archiver Ultra"
    print_info "Время удаления: $(date)"
    
    check_sudo
    stop_services
    remove_program_files
    remove_config
    remove_completion
    remove_man_pages
    cleanup_environment
    
    if [ "$FULL_REMOVAL" = true ]; then
        print_info "Полное удаление без вопросов..."
        remove_data <<< "y"
        remove_user <<< "y"
        remove_dependencies <<< "y"
    else
        if [ "$KEEP_DATA" = false ]; then
            remove_data
        fi
        if [ "$KEEP_DEPS" = false ]; then
            remove_dependencies
        fi
        remove_user
    fi
    
    verify_removal
    
    print_success "Удаление Pi-Archiver Ultra завершено!"
    print_info ""
    print_info "Спасибо за использование Pi-Archiver Ultra!"
}

# Запуск удаления
main "$@"
