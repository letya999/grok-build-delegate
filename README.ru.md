<p align="center">
  <a href="README.md">English</a> · <strong>Русский</strong>
</p>

<p align="center">
  <h1 align="center">Grok Build Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/grok-build-delegate"><img src="https://img.shields.io/badge/статус-активен-brightgreen" alt="статус"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue" alt="Лицензия: MIT"></a>
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/skills.sh-доступен-black" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-grok-purple" alt="CLI: grok">
</p>

Скилл-делегат для неинтерактивного запуска Grok Build CLI (`grok`) от [Артема Летюшева](https://github.com/letya999).

Основная команда — `scripts/delegate_grok.py`. Главный потребитель — управляющий агент или оркестратор: каждый запуск выполняет Grok Build в ограниченном подпроцессе (`grok -p`) и возвращает структурированный JSON-конверт.

---

## Одна цель, изолированный подпроцесс, нулевое доверие

Скрипт-обёртка служит детерминированным барьером безопасности между управляющим агентом и Grok Build CLI:

- **Строго неинтерактивный запуск:** Вызывает `grok -p` напрямую через `subprocess.run(..., shell=False)` без диалогового перехвата.
- **Ограничение каталога:** Задаёт целевую рабочую директорию проекта через `--cwd <path>`.
- **Стабильность скриптов:** Передаёт `--no-auto-update` и `--no-alt-screen`, исключая фоновые проверки обновлений и искажение вывода.
- **Поддержка структурированного вывода:** Поддерживает флаг `--json-schema` для получения валидированного JSON-ответа.
- **Верификация результатов:** Ответ считается непроверенным до независимой инспекции через diff и тесты.
- **Изоляция секретов:** Не считывает, не печатает и не передаёт `XAI_API_KEY`, файлы `~/.grok` или файлы `.env`.

## Матрица возможностей

| Параметр / Возможность | Спецификация | Поведение и гарантии |
|---|---|---|
| **Команда запуска** | `grok -p "<task>"` | Неинтерактивное выполнение в режиме print |
| **Ограничение каталога** | `--cwd <cwd>` | Ограничивает Grok Build рамками рабочей папки |
| **Формат вывода** | `--output-format json` | Единый JSON-объект в финале выполнения |
| **Структурированный вывод** | `--json-schema <schema>` | Фиксирует формат ответа по схеме JSON Schema |
| **Гигиена выполнения** | `--no-auto-update --no-alt-screen` | Отключает фоновые апдейты и полноэкранный терминал |
| **Лимит шагов** | `--max-turns <int>` | Ограничивает число итераций агента |
| **Автономные правки** | `--always-approve` / `--trust` | Разрешает автоматическое применение правок |
| **Возобновление сессий** | `--session-id <id>` | Продолжает существующую сессию диалога |
| **Переопределение бинарника** | Переменная `GROK_BIN` | Приоритетный путь до вызова из PATH |
| **Коды возврата** | `0, 2, 65, 124, 126, 127` | Стандартизированная маршрутизация ошибок |

## Установка

Через `npx skills`:

```bash
npx skills add letya999/grok-build-delegate
```

Или клонированием в каталог скиллов:

```bash
git clone https://github.com/letya999/grok-build-delegate.git .agents/skills/grok-build-delegate
```

## Быстрый старт

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_grok.py \
  --cwd "$PWD" \
  --task "Проанализируй репозиторий и выдели самую критичную проблему." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_grok.py `
  --cwd (Get-Location).Path `
  --task "Проанализируй репозиторий и выдели самую критичную проблему." `
  --timeout 45m
```

---

<details>
<summary>Схема JSON-манифеста и интеграция с агентом</summary>

Обёртка записывает `stdout.json`, `stderr.log` и `result.json` во временный каталог:

```json
{
  "tool": "grok",
  "cwd": "C:\\work\\repo",
  "exit_code": 0,
  "output_dir": "C:\\Temp\\grok-build-delegate-xyz",
  "stdout": "C:\\Temp\\grok-build-delegate-xyz\\stdout.json",
  "stderr": "C:\\Temp\\grok-build-delegate-xyz\\stderr.log",
  "response": {
    "issue": "High risk vulnerability in auth handler",
    "severity": "critical"
  },
  "raw": {
    "text": "...",
    "structuredOutput": { "..." }
  }
}
```

Если Grok завершился с кодом 0, но вернул пустой ответ или некорректный JSON, обёртка завершается с кодом `65`.

</details>

<details>
<summary>Флаги CLI и параметры запуска</summary>

| Флаг | Тип | Описание |
|---|---|---|
| `--cwd` | Путь (обязательный) | Рабочий каталог проекта. Код `2`, если каталог не существует. |
| `--task` | Строка (обязательный) | Текст задачи / поручения для передачи Grok. |
| `--timeout` | Время (по умолчанию: `45m`) | Таймаут: `90s`, `45m`, `2h` или число секунд. |
| `--model` | Строка | Модель Grok для выполнения запроса. |
| `--json-schema` | Строка | Строка JSON Schema для получения типизированного ответа. |
| `--max-turns` | Число | Максимальное число шагов диалога. |
| `--always-approve` | Флаг | Передаёт `--always-approve` для автоматического одобрения вызова инструментов. |
| `--trust` | Флаг | Передаёт `--trust` для доверенного доступа к каталогу. |
| `--session-id` | Строка | Идентификатор сессии для возобновления. |
| `--output-dir` | Путь | Каталог для сохранения логов и манифеста. |

</details>

<details>
<summary>Правила безопасности и изоляция секретов</summary>

- **Защита секретов:** Никогда не считывает и не логирует `XAI_API_KEY`, OAuth токены и файлы в каталоге `~/.grok`.
- **Ограниченное исполнение:** Никаких постоянных фоновых демонов и неконтролируемых циклов опроса.
- **Защита от циклов:** Делегированный Grok не должен запускать новые подпроцессы через обёртки.

</details>

<details>
<summary>Протокол независимой верификации</summary>

Ответы делегата не считаются окончательным доказательством. При изменении файлов:

1. Проверьте diff: `git diff --stat` и `git diff`.
2. Запустите тесты независимо: `pytest`, `npm test`, `cargo test`.
3. Проверьте добавленные файлы и импорты.

</details>

<details>
<summary>Набор тестов</summary>

Запуск тестов через стандартную библиотеку `unittest`:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Точки входа скилла</summary>

- [SKILL.md](SKILL.md) — Спецификация инструкций для кодинг-агентов.
- [QUICKSTART.md](QUICKSTART.md) — Краткое руководство.
- [references/runtime-setup.md](references/runtime-setup.md) — Проверка окружения перед запуском.
- [references/headless-reference.md](references/headless-reference.md) — Справочник флагов Grok Build CLI.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Индекс для каталога skills.sh.
- [dist/grok-build-delegate.zip](dist/grok-build-delegate.zip) — Архив скилла.

</details>

<details>
<summary>Лицензия</summary>

MIT License. См. полный текст в [LICENSE](LICENSE). Copyright (c) 2026 Artem Letyushev.

</details>
