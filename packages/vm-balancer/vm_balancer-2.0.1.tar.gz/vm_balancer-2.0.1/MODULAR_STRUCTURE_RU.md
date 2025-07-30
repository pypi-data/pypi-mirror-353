# VM Balancer - Modular Structure Guide

## ✅ Завершение реструктуризации

Проект VM Balancer успешно преобразован из монолитного скрипта в модульную Python-библиотеку, следующую лучшим практикам разработки.

## 📦 Финальная структура пакета

```
vm-balancer/
├── src/vm_balancer/          # Основной пакет
│   ├── __init__.py           # Экспорты пакета
│   ├── __main__.py           # Модульный запуск (python -m vm_balancer)
│   ├── main.py               # Функция main() для CLI
│   ├── api/                  # API клиент VMManager
│   │   ├── __init__.py
│   │   └── client.py         # VMManagerAPI
│   ├── core/                 # Основная логика балансировки
│   │   ├── __init__.py
│   │   └── balancer.py       # VMBalancer
│   ├── models/               # Модели данных
│   │   ├── __init__.py
│   │   ├── cluster.py        # ClusterInfo
│   │   ├── node.py           # NodeInfo
│   │   └── vm.py             # VMInfo
│   ├── monitoring/           # Мониторинг узлов
│   │   ├── __init__.py
│   │   └── ssh.py            # SSHMonitor
│   ├── notifications/        # Уведомления
│   │   ├── __init__.py
│   │   └── telegram.py       # TelegramNotifier
│   └── utils/                # Утилиты
│       ├── __init__.py
│       └── env.py            # EnvConfig
├── pyproject.toml            # Современная конфигурация пакета
├── setup.py                  # Совместимость со старыми версиями
├── MANIFEST.in               # Включение дополнительных файлов
├── requirements.txt          # Зависимости продакшена
├── config.env.example        # Пример конфигурации
└── MODULAR_STRUCTURE.md      # Этот файл
```

## 🚀 Способы запуска

### 1. Консольная команда (рекомендуется)
```bash
# Установка пакета
pip install vm-balancer

# Или установка из исходников
pip install .

# Использование
vm-balancer --help
vm-balancer --config .env --dry-run --once
vm-balancer --interval 300 --cluster-ids 1,2,3
```

### 2. Модульный запуск
```bash
python -m vm_balancer --help
python -m vm_balancer --config .env --dry-run --once
```

## 📋 Импорты для разработки

```python
# Основной класс балансировщика
from vm_balancer import VMBalancer

# API клиент
from vm_balancer import VMManagerAPI

# Модели данных
from vm_balancer import ClusterInfo, NodeInfo, VMInfo

# Компоненты
from vm_balancer import TelegramNotifier, SSHMonitor

# Пример использования
balancer = VMBalancer(config_path='.env', dry_run=True)
await balancer.run_once()
```

## 🔧 Конфигурация

Используйте файл `config.env.example` как шаблон для конфигурации:

```bash
# Скопируйте и настройте
cp config.env.example .env
# Отредактируйте настройки подключения
nano .env
```

## ✅ Сохраненная функциональность

Все возможности оригинального монолитного скрипта сохранены:

- ✅ Автоматическая балансировка VM
- ✅ SSH мониторинг узлов
- ✅ Telegram уведомления
- ✅ Dry-run режим
- ✅ Исключение узлов
- ✅ Настройка порогов
- ✅ Ограничения миграций
- ✅ Отслеживание истории
- ✅ Совместимость QEMU

## 🎁 Улучшения

### Модульность
- Четкое разделение ответственности
- Легкое тестирование компонентов
- Возможность импорта в другие проекты

### Удобство разработки
- Типизированная конфигурация
- Консольная команда vm-balancer
- Модульный запуск python -m vm_balancer
- Современные инструменты сборки

### Стандартизация
- Следование PEP 8
- Стандартная структура Python пакета
- Документированные экспорты

## 🔄 Миграция со старого кода

1. **Замените прямые вызовы скрипта:**
   ```bash
   # Старый способ
   python vm_balancer.py --dry-run --once
   
   # Новый способ
   vm-balancer --dry-run --once
   ```

2. **Обновите создание экземпляра:**
   ```python
   # Старый способ
   api = VMManagerAPI(host, user, pass)
   balancer = VMBalancer(api, dry_run=True, ...)
   
   # Новый способ
   balancer = VMBalancer(config_path='.env', dry_run=True)
   ```

## 🧪 Тестирование

```bash
# Проверка импортов
python -c "from vm_balancer import *; print('OK')"

# Проверка CLI
vm-balancer --version

# Проверка модульного запуска  
python -m vm_balancer --version

# Симуляция с конфигом
vm-balancer --config .env --dry-run --once --verbose
```
