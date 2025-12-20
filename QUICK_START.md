# Быстрый старт установки Pi-Archiver Ultra

## Установка на Ubuntu 24.04

### Вариант 1: Системная установка (рекомендуется)
Устанавливает программу в систему для глобального доступа.

```bash
# Скачайте проект
git clone <repository-url>
cd Archivator_Pi

# Системная установка
sudo ./install_system.sh

# Без systemd сервиса
sudo ./install_system.sh --no-service

# Удаление
sudo ./install_system.sh --uninstall
```

### Вариант 2: Локальная установка
Устанавливает только в папку проекта.

```bash
# Локальная установка
./install_ubuntu24.sh

# Без GPU поддержки
./install_ubuntu24.sh --no-gpu
```

## Начало работы (после системной установки)

### 1. Использование из любой директории
```bash
# Архивация файла
pi-archiver archive document.txt

# Извлечение архива
pi-archiver extract archive.piarc

# Информация об архиве
pi-archiver info archive.piarc

# Список архивов
pi-archiver list

# Запуск бенчмарка
pi-benchmark

# Генерация π
pi-generator --digits 1000000
```

### 2. Доступные команды
- `pi-archiver` - основной архиватор
- `pi-benchmark` - тесты производительности  
- `pi-generator` - генератор числа π

### 3. Системные директории
- `/opt/pi-archiver/` - программа и исходники
- `/var/lib/pi-archiver/` - данные и индексы
- `/etc/pi-archiver/` - конфигурация
- `/var/log/pi-archiver/` - логи

## Что делает скрипт установки?

- ✅ Обновляет систему
- ✅ Устанавливает все зависимости
- ✅ Создает виртуальное окружение Python
- ✅ Компилирует C++ компоненты
- ✅ Настраивает переменные окружения
- ✅ Создает ярлыки для запуска
- ✅ Проверяет работоспособность

## Проверка установки

После установки выполните:
```bash
source setup_env.sh
python3 -c "from src.pi_generator.pi_generator import PiGenerator; print('✓ Все работает!')"
```

## Возможные проблемы

**Ошибка прав доступа:**
```bash
chmod +x install_ubuntu24.sh
```

**Проблемы с GMP:**
```bash
sudo apt install --reinstall libgmp-dev libgmpxx-dev
```

**OpenCL не работает:**
```bash
./install_ubuntu24.sh --no-gpu
```

## Следующие шаги

1. Прочтите `README.md` для обзора
2. Изучите `INSTALL.md` для детальной настройки
3. Запустите тесты производительности
4. Попробуйте сжать свои файлы
