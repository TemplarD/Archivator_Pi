def compression_progress_callback(progress, current, total, remaining_time=None):
    """Callback для отображения прогресса сжатия"""
    bar_length = 50
    filled_length = int(bar_length * progress / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    if remaining_time is not None:
        # Форматируем оставшееся время
        if remaining_time > 3600:
            time_str = f"{remaining_time/3600:.1f} ч"
        elif remaining_time > 60:
            time_str = f"{remaining_time/60:.1f} мин"
        else:
            time_str = f"{remaining_time:.0f} сек"
            
        print(f"\rСжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков) Осталось: {time_str}", end='')
    else:
        print(f"\rСжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков)", end='')
    
    if progress >= 100:
        print()  # Переход на новую строку после завершения
