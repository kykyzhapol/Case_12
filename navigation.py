import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
import utils  # Импорт функций архитектора



def get_current_drive() -> str:
    """Получение текущего диска Windows"""
    # TODO: Вернуть текущий диск (например: "C:")
    # Использовать os.path.splitdrive()

    # Возвращает полный путь до файла
    path = os.path.abspath(__file__)
    # Разделяет весь путь на диск до двоеточия включительно и оставшуюся часть
    drive, rest = os.path.splitdrive(path)
    return drive

def list_available_drives() -> List[str]:
    """Получение списка доступных дисков Windows"""
    # TODO: Вернуть список доступных дисков (['C:', 'D:', ...])
    # Использовать os.listdir('/') не подойдет для Windows!
    # Исследовать: использовать win32api или другие методы
    # Возвращает список доступных дисков
    return os.listdrives()

def list_directory(path: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """Отображение содержимого каталога в Windows"""
    # TODO: Используя utils.safe_windows_listdir(), получить содержимое
    # Для каждого элемента вернуть словарь с информацией:
    # {'name': 'file.txt', 'type': 'file', 'size': 1024, 'modified': '2024-01-15', 'hidden': False}
    # Использовать utils.is_hidden_windows_file() для проверки скрытых файлов
    # Вернуть (True, данные) при успехе, (False, []) при ошибке

    try:
        # Создание списка из путей до каждого объекта в каталоге
        list_path = utils.safe_windows_listdir(path)
        list_info = []
        for path in list_path:
            # получение название файла с расширением из пути к объекту
            name = os.path.basename(path)
            # получение отдельно имени и отдельно расширения файла из его названия
            name_file, type_file = os.path.splitext(name)
            # получение размера из пути к объекту
            size_file = os.path.getsize(path)
            # получение даты последней редакции файла в секундах с начала эпохи и последующий перевод в дату из пути к объекту
            modified = datetime.date(datetime.fromtimestamp(os.path.getmtime(path)))
            # Проверяет является ли объект секретным
            hidden = utils.is_hidden_windows_file(path)

            info = {'name': name_file,
                    'type': type_file,
                    'size': size_file,
                    'modified': modified,
                    'hidden': hidden}
            list_info.append(info)

        return True, list_info
    except:
        return False, []


def format_directory_output(items: List[Dict[str, Any]]) -> None:
    """Форматированный вывод содержимого каталога для Windows"""
    # TODO: Красиво отформатировать вывод используя данные из list_directory()
    # Учесть что в Windows есть системные и скрытые файлы
    # Показать диски если находимся в корне
    pass

def move_up(current_path: str) -> str:
    """Переход в родительский каталог в Windows"""
    # TODO: Использовать utils.get_parent_path() для получения родителя
    # Проверить валидность нового пути через utils.validate_windows_path()
    # Учесть переход между дисками
    path = utils.get_parent_path(current_path)
    bools = utils.validate_windows_path(path)[0]
    if bools:
        return path


def move_down(current_path: str, target_dir: str) -> Tuple[bool, str]:
    """Переход в указанный подкаталог в Windows"""
    # TODO: Проверить что target_dir существует через utils.safe_windows_listdir()
    # Сформировать новый путь и проверить через utils.validate_windows_path()
    # Вернуть (True, новый_путь) при успехе, (False, текущий_путь) при ошибке
    path = current_path + '\\' + target_dir
    if path in utils.safe_windows_listdir(current_path):
        return True, path
    else:
        return False, current_path


def get_windows_special_folders() -> Dict[str, str]:
    """Получение путей к специальным папкам Windows"""
    # TODO: Вернуть словарь с путями к папкам:
    # {'Desktop': 'C:\\Users\\...', 'Documents': '...', 'Downloads': '...'}
    # Использовать os.environ для получения USERPROFILE и других переменных
    special_folders = {}
    user = os.environ.get('USERPROFILE')
    list1 = list_directory(user)
    for path_1 in list1[1]:
        special_folders[path_1['name']] = os.path.join(user, path_1['name'])

    return special_folders
