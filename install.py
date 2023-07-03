
import pkg_resources
import re
import subprocess
import sys
from collections import defaultdict

if len(sys.argv) > 1:
    package_name = sys.argv[1]
else:
    print('Укажите имя пакета в качестве аргумента командной строки')
    sys.exit(1)

def check_installed(dependencies):
    not_installed = []
    version_conflicts = []
    for dependency in dependencies:
        try:
            pkg_resources.require(dependency)
        except pkg_resources.DistributionNotFound:
            not_installed.append(dependency)
        except pkg_resources.VersionConflict as e:
            version_conflicts.append((dependency, str(e)))
    return not_installed, version_conflicts

def install_dependency(dependency):
    dependency_name = re.split('[<>=]', dependency)[0]
    try: 
        with open('opkg_skip.txt', 'r') as f:
            failed_packages = f.read().splitlines()
    except:
        failed_packages = []
    if dependency_name in failed_packages:
        print(f'Пропуск установки модуля {dependency} с помощью opkg, так как он уже был помечен как неудачный')
        return False
    try:
        subprocess.check_output(['opkg', 'install', f'python3-{dependency_name}'])
        try:
            pkg_resources.require(dependency)
            print(f'Модуль {dependency} успешно установлен с помощью opkg')
            return True
        except pkg_resources.VersionConflict as e:
            print(f'Установленная версия модуля {dependency} не соответствует требованиям: {e}')
            remove_dependency(dependency)
            with open('opkg_skip.txt', 'a') as f:
                f.write(f'{dependency_name}\n')
            return False
    except subprocess.CalledProcessError:
        print(f'Не удалось установить модуль {dependency} с помощью opkg')
        with open('opkg_skip.txt', 'a') as f:
            f.write(f'{dependency_name}\n')
        return False

def get_dependencies_recursive(package_name, dependency_tree=None):
    if dependency_tree is None:
        dependency_tree = defaultdict(set)
    try:
        package = pkg_resources.working_set.by_key[package_name]
    except KeyError:
        return dependency_tree
    for requirement in package.requires():
        dependency_tree[package_name].add(str(requirement))
        get_dependencies_recursive(requirement.project_name, dependency_tree)
    return dependency_tree

def check_dependencies(package_name, dependency_tree):
    not_installed = []
    version_conflicts = []
    for dependency in dependency_tree[package_name]:
        ni, vc = check_dependencies(dependency, dependency_tree)
        not_installed.extend(ni)
        version_conflicts.extend(vc)
    ni, vc = check_installed([package_name])
    not_installed.extend(ni)
    version_conflicts.extend(vc)
    return not_installed, version_conflicts

def remove_dependency(dependency):
    dependency_name = re.split('[<>=]', dependency)[0]
    try:
        subprocess.check_output(['opkg', 'remove', f'python3-{dependency_name}'])
        print(f'Модуль {dependency} успешно удален с помощью opkg')
        return True
    except subprocess.CalledProcessError:
        print(f'Не удалось удалить модуль {dependency} с помощью opkg')
        try:
            subprocess.check_output(['pip', 'uninstall', '-y', dependency])
            print(f'Модуль {dependency} успешно удален с помощью pip')
            return True
        except subprocess.CalledProcessError:
            print(f'Не удалось удалить модуль {dependency} с помощью pip')
            return False

def install_dependencies(package_name, dependency_tree):
    failed_dependencies = []
    for dependency in dependency_tree[package_name]:
        failed_dependencies.extend(install_dependencies(dependency, dependency_tree))
    if not install_dependency(package_name):
        failed_dependencies.append(package_name)
    return failed_dependencies

def remove_conflicting_dependencies(version_conflicts):
    removed_dependencies = []
    for conflict in version_conflicts:
        user_input = input(f'Удалить конфликтующую зависимость {conflict[0]}? (Д/н) ')
        if user_input.lower() == 'д':
            if remove_dependency(conflict[0]):
                removed_dependencies.append(conflict[0])
        else:
            with open('opkg_skip.txt', 'a') as f:
                f.write(f'{conflict[0]}\n')
    
    if removed_dependencies:
        print(f'Удалены следующие зависимости с конфликтующими версиями:')
        for dependency in sorted(removed_dependencies):
            print(f'- {dependency}')
    
    return removed_dependencies

dependency_tree = get_dependencies_recursive(package_name)

not_installed, version_conflicts = check_dependencies(package_name, dependency_tree)

if not_installed or version_conflicts:
    if not_installed:
        print(f'Недостающие зависимости для пакета {package_name}:')
        for dependency in sorted(not_installed):
            print(f'- {dependency}')
    
    if version_conflicts:
        print(f'Конфликты версий для пакета {package_name}:')
        for conflict in sorted(version_conflicts):
            print(f'- {conflict[0]}: {conflict[1]}')
    
    if version_conflicts:
        removed_dependencies = remove_conflicting_dependencies(version_conflicts)
        
        if not removed_dependencies:
            sys.exit(1)
    
    failed_dependencies = install_dependencies(package_name, dependency_tree)
    
    if failed_dependencies:
        print(f'Не удалось установить следующие зависимости с помощью opkg:')
        for dependency in sorted(failed_dependencies):
            print(f'- {dependency}')
        
        print(f'Попытка установки недостающих зависимостей с помощью pip:')
        
        for dependency in failed_dependencies:
            try: 
                with open('pip_skip.txt', 'r') as f:
                    installed_packages = f.read().splitlines()
            except:
                installed_packages = []
            if dependency in installed_packages:
                print(f'Пропуск установки модуля {dependency} с помощью pip, так как он уже был установлен')
                continue
            try:
                subprocess.check_output(['pip', 'install', dependency])
                pkg_resources.require(dependency)
                print(f'Модуль {dependency} успешно установлен с помощью pip')
                with open('pip_skip.txt', 'a') as f:
                    f.write(f'{dependency}\n')
            except (subprocess.CalledProcessError, pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                print(f'Не удалось установить модуль {dependency} с помощью pip')

# Проверка недостающих зависимостей после установки
dependency_tree = get_dependencies_recursive(package_name)
not_installed, version_conflicts = check_dependencies(package_name, dependency_tree)

if not_installed:
    print(f'Недостающие зависимости для пакета {package_name}:')
    for dependency in sorted(not_installed):
        print(f'- {dependency}')

def pip_check_and_install():
    try:
        output = subprocess.check_output(['pip', 'check'], stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    missing_dependencies = re.findall(r'([\w-]+) \S+ requires ([\w-]+), which is not installed', output)
    incompatible_dependencies = re.findall(r'([\w-]+) \S+ has requirement ([\w-]+)', output)
    for package, dependency in missing_dependencies:
        print(f'Установка недостающей зависимости {dependency} для пакета {package}')
        if not install_dependency(dependency):
            try: 
                with open('pip_skip.txt', 'r') as f:
                    installed_packages = f.read().splitlines()
            except:
                installed_packages = []
            if dependency in installed_packages:
                print(f'Пропуск установки модуля {dependency} с помощью pip, так как он уже был установлен')
                continue
            try:
                print(f'Установка {dependency} с помощью pip')
                subprocess.check_output(['pip', 'install', '--upgrade', dependency])
                print(f'Модуль {dependency} успешно установлен с помощью pip')
                with open('pip_skip.txt', 'a') as f:
                    f.write(f'{dependency}\n')
                dependency_name = re.split('[<>=]', dependency)[0]
                with open('opkg_skip.txt', 'a') as f:
                    f.write(f'{dependency_name}\n')
            except subprocess.CalledProcessError:
                print(f'Не удалось установить модуль {dependency} с помощью pip')
    if incompatible_dependencies:
        print('Несовместимые зависимости:')
        for package, dependency in incompatible_dependencies:
            print(f'- {package} требует {dependency}')

pip_check_and_install()
