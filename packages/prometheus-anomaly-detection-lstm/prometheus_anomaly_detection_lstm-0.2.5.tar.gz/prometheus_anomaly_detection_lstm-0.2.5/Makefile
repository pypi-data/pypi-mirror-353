# Makefile для управления Python проектом с помощью uv

# --- Переменные ---
# Используем uv для всех операций, связанных с окружением и пакетами
UV = uv
PYTHON_IN_VENV = .venv/bin/python

# Цель по умолчанию - показать справку
.DEFAULT_GOAL := help

# `.PHONY` объявляет цели, которые не являются файлами.
.PHONY: help setup-uv install sync lock update collect preprocess train detect build clean

# --- Команды для разработки ---

help:
	@echo "Makefile для проекта prometheus-anomaly-detection-lstm"
	@echo "--------------------------------------------------------"
	@echo "Доступные команды:"
	@echo "\n  make setup-uv      - Проверяет и устанавливает uv, если он отсутствует."
	@echo "  make install       - (Первичная настройка) Устанавливает uv, создает окружение и ставит зависимости."
	@echo "  make sync          - (Быстрое обновление) Синхронизирует окружение с lock-файлом."
	@echo "  make lock          - Обновляет lock-файл (requirements.lock.txt) на основе pyproject.toml."
	@echo "  make update        - Обновляет lock-файл и сразу синхронизирует окружение."
	@echo "\n--- Команды рабочего процесса ---"
	@echo "  make collect       - Запускает сбор данных из Prometheus."
	@echo "  make preprocess    - Запускает предобработку собранных данных."
	@echo "  make train         - Запускает обучение модели."
	@echo "  make detect        - Запускает real-time детектор аномалий."
	@echo "\n--- Сборка и очистка ---"
	@echo "  make build         - Собирает дистрибутивы пакета (wheel и sdist)."
	@echo "  make clean         - Удаляет артефакты сборки, кэши и виртуальное окружение."

# Проверка и установка uv
setup-uv:
	@echo "⬇️  Проверка и установка uv..."
	@if ! command -v uv &> /dev/null; then \
		echo "uv не найден. Установка..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "‼️  Важно: Перезапустите ваш терминал или выполните 'source $$HOME/.cargo/env', чтобы команда uv стала доступна."; \
	else \
		echo "✅ uv уже установлен."; \
	fi

# Создание окружения, если его нет, и установка зависимостей
install: setup-uv .venv/pyvenv.cfg requirements.lock.txt
	@echo "📦 Установка зависимостей в окружение..."
	$(UV) pip sync requirements.lock.txt
	@echo "✅ Окружение готово и зависимости установлены. Активируйте его: source .venv/bin/activate"

# Явное создание виртуального окружения
# Эта цель используется как зависимость для `install`
.venv/pyvenv.cfg:
	@echo "🐍 Создание виртуального окружения .venv..."
	$(UV) venv

# Быстрая синхронизация с lock-файлом
sync:
	@echo "🔄 Синхронизация окружения с requirements.lock.txt..."
	$(UV) pip sync requirements.lock.txt
	@echo "✅ Синхронизация завершена."

# Обновление lock-файла после изменения pyproject.toml
lock:
	@echo "🔒 Обновление requirements.lock.txt из pyproject.toml..."
	$(UV) pip compile pyproject.toml --extra dev -o requirements.lock.txt
	@echo "✅ Lock-файл обновлен."

# Комбинация `lock` и `sync` для полного обновления
update: lock sync

# --- Команды рабочего процесса (используют cli.py) ---

collect:
	@echo "📊 Запуск сбора данных..."
	$(UV) run python cli.py collect

preprocess:
	@echo "🛠️  Запуск предобработки данных..."
	$(UV) run python cli.py preprocess

train:
	@echo "🎓 Запуск обучения модели..."
	$(UV) run python cli.py train

detect:
	@echo "📡 Запуск real-time детектора..."
	$(UV) run python cli.py detect

# --- Сборка и очистка ---

# Сборка дистрибутивов
build:
	@echo "📦 Сборка пакета..."
	$(UV) run python -m build

# Удаление всех сгенерированных файлов
clean:
	@echo "🧹 Очистка проекта..."
	rm -rf .venv
	rm -rf dist
	rm -rf build
	rm -rf .pytest_cache
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -r {} +
	echo "✅ Очистка завершена."

