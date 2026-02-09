'''
Sergey's task: 2,3,7,8

Gleb's task - rest of them (done)
2, 3, 7 - done

'''

import os
import sys
from random import choice
from typing import NoReturn

from matplotlib.style.core import available

import utils  # Собственный модуль
import navigation  # Модуль инженера навигации
import analysis  # Модуль аналитика
import search  # Модуль эксперта поиска

def check_windows_environment() -> bool:
    """Проверка что программа запущена в Windows"""
    # TODO: Использовать utils.is_windows_os()
    # Если не Windows - вывести сообщение и завершить программу

    if utils.is_windows_os():
        return True
    else:
        print('Не подходящяя операционная система')
        return False


def display_windows_banner() -> None:
    import platform
    """Отображение баннера с информацией о Windows
    Info about platform module:
    https://habr.com/ru/articles/864830/?ysclid=mle71u4olb765257958
    """
    # TODO: Показать информацию о текущем диске, версии и т.д.
    # Использовать navigation.get_current_drive()
    current_d = navigation.get_current_drive()
    available_d = navigation.list_available_drives()
    try:
        win_info = {
            'platform': platform.platform(),
            'version': platform.version(),
            'release': platform.release(),
        }
    except Exception as e:
        print(f'ошибка: {e}')
    print(f'Информация о файлах Эпштейна:'
          f'\nТекущий диск: {current_d}'
          f'Доступные диски: {available_d}'
          f'\nИНФОРМАЦИЯ О СИСТЕМЕ'
          f'Платформа: {win_info['platform']}'
          f'Версия Windows: {win_info['version']}'
          f'Релиз: {win_info['release']}')


def display_main_menu(current_path: str) -> None:
    """Отображение главного меню для Windows"""
    # TODO: Показать текущий путь и доступные команды
    # Использовать navigation.list_available_drives() для показа дисков
    # Интегрировать опции из всех модулей
    available_d = navigation.list_available_drives()
    print(f'Текущий путь: {current_path}'
          f'Доступные диски: {available_d}')
    while search.search_menu_handler(current_path):
        search.search_menu_handler(current_path)
        

def handle_windows_navigation(current_path: str) -> str:
    """Обработка команд навигации в Windows"""
    # TODO: Использовать navigation.move_up() и navigation.move_down()
    # Обрабатывать смену дисков через navigation.list_available_drives()
    command = int(input('1. Перейти к родительскому коталогу\n'
                        '2. Перейти в следующий каталог\n'
                        '3. Сменить диск'))
    match command:
        case 1:
            new_path = navigation.move_up(current_path)
        case 2:
            cataloge = input('Укажите каталог')
            new_path = navigation.move_down(current_path, cataloge)
        case 3:
            print(f'Доступные диски: {navigation.list_directory()}')
            directory = input('Укажите диск')
            match len(directory):
                case 1:
                    new_path = directory + ':'
                case 2:
                    new_path = directory
        case _:
            print('Unexpected mistake')
            return current_path
    return new_path


def handle_windows_analysis(current_path: str) -> None:
    """Обработка команд анализа Windows файловой системы"""
    # TODO: Использовать analysis.show_windows_directory_stats()
    # и другие функции анализа
    analysis.show_windows_directory_stats(current_path)
    

def handle_windows_search(current_path: str) -> None:
    """Обработка команд поиска в Windows"""
    # TODO: Использовать search.search_menu_handler()
    search.search_menu_handler(current_path)
    

def run_windows_command(command: str, current_path: str) -> str:
    """Главный обработчик команд с использованием match case"""
    # TODO: Использовать match case для маршрутизации команд
    # Интегрировать ВСЕ модули:
    # - navigation для команд 1, 5, 6
    # - analysis для команд 2, 4
    # - search для команды 3
    # Вернуть обновленный текущий путь
    print('1 - навигация'
          '2 - анализ'
          '3 - поиск')
    try:
        choice_command = int(input('Что вы хотите сделать?'))
    except ValueError:
        return 'ValueError'
    match choice_command:
        case 1:
            return handle_windows_navigation(current_path)
        case 2:
            handle_windows_analysis(current_path)
            return current_path
        case 3:
            handle_windows_search(current_path)
            return current_path
        case _:
            return 'Unexpected mistake'

def main() -> NoReturn:
    """Главная функция программы для Windows"""
    # TODO:
    # 1. Проверить Windows окружение
    # 2. Показать баннер
    # 3. Основной цикл с использованием ВСЕХ модулей
    # 4. Обработка ошибок и завершение работы
    pass

if __name__ == "__main__":
    main()
