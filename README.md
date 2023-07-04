# OpenWrt Python Dependency Installer

Смотрите далее на русском.

Script for automatically installing Python package dependencies in OpenWrt through `opkg` and `pip`.

This script is designed to automate the routine work of installing Python dependencies in OpenWrt. It checks whether all dependencies for the specified package are installed, and if not, tries to install them using the package manager, first `opkg`, then `pip`. If version conflicts are detected, the script tries to remove conflicting dependencies and install them again.

## Usage

To use this script, run it with the package name specified as a command line argument:

```
python install_dependencies.py package_name
```

where `package_name` is the name of the package for which you want to install dependencies.

The script will check if all dependencies for the specified package are installed, and if not, try to install them using `opkg` or `pip`. If version conflicts are detected, the script will ask the user for confirmation before removing conflicting dependencies.

## Limitations

Please note that not all packages can be installed using `opkg` or `pip`. In this case, the script will output an error message and continue to work. You can install missing packages manually or use another installation method.

## License

This script is distributed under the MIT license. See the LICENSE file for more information.

---

# OpenWrt Python Dependency Installer

Скрипт для автоматической установки зависимостей пакета Python в OpenWrt через `opkg` и `pip`.

Этот скрипт предназначен для автоматизации рутинной работы по установке зависимостей Python в OpenWrt. Он проверяет, установлены ли все зависимости для указанного пакета, и если нет, то пытается их установить с помощью менеджера пакетов, сначала `opkg`, а затем `pip`. Если обнаружены конфликты версий, скрипт пытается удалить конфликтующие зависимости и установить их заново.

## Использование

Чтобы использовать этот скрипт, запустите его с указанием имени пакета в качестве аргумента командной строки:

```
python install_dependencies.py package_name
```

где `package_name` - это имя пакета, для которого необходимо установить зависимости.

Скрипт проверит, установлены ли все зависимости для указанного пакета, и если нет, то попытается их установить с помощью `opkg` или `pip`. Если обнаружены конфликты версий, скрипт запросит у пользователя подтверждение перед удалением конфликтующих зависимостей.

## Ограничения
Обратите внимание, что не все пакеты могут быть установлены с помощью `opkg` или `pip`. В этом случае скрипт выведет сообщение об ошибке и продолжит работу. Вы можете установить недостающие пакеты вручную или использовать другой способ установки.

## Лицензия

Этот скрипт распространяется под лицензией MIT. См. файл LICENSE для получения дополнительной информации.
