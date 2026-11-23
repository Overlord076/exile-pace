# ExilePace — PoE 1 (Heist # ExilePace — PoE 1 PoE Heist & Path of Exile 2 Tracker PoE 2 Activity Tracker Blight) # ExilePace — PoE 1 PoE Heist & Path of Exile 2 Tracker PoE 2 Activity Tracker Path of Exile 2 Activity Tracker

Легкий кроссплатформенный трекер забегов для **Path of Exile 1** (Кража / Heist) и **Path of Exile 2** (Испытания Сехем, Хаоса, Пинакл-боссы, Карты). Работает путем чтения локального лог-файла игры `Client.txt` без вмешательства в процесс игры.

---

## 🇷🇺 Руководство на русском языке

### Возможности
* **Path of Exile 1 (Кража):** подсчет одиночных контрактов и чертежей (Grand Heist) с разбивкой по крыльям, локациям и рекордам скорости.
* **Path of Exile 2:** подсчет забегов и этажей в Испытание Сехем (Sekhemas), Испытание Хаоса (Chaos), заходов на пинакл-боссов и карт.
* **Темп фарма:** расчет скорости в забегах/час, чистого времени в забегах и времени простоя в Гавани/Хабе.
* **Оверлей поверх игры:** полупрозрачный перетаскиваемый виджет (требуется режим «Оконный на весь экран» в настройках графики игры).

### Установка и запуск
* **Linux (через Python):**
  1. Убедитесь, что установлен модуль интерфейса: `sudo apt install python3-tk` (или `tk` в Arch / `python3-tkinter` в Fedora).
  2. Запуск оверлея PoE 1: `./start_overlay.sh` или `python3 heist_stats.py today --overlay`
  3. Запуск оверлея PoE 2: `./start_poe2_overlay.sh` или `python3 heist_stats.py --poe2 today --overlay`
* **Linux (автономный бинарник без Python):**
  * Запустите файл `./dist/poe-tracker today --overlay`
* **Windows:**
  * Запустите **`install_windows.bat`** — скрипт сам установит Python (если его нет) и создаст ярлыки оверлеев на Рабочем столе.

### Аргументы командной строки
* `today` — статистика только за текущий день
* `league` (или `--league`) — статистика с начала текущей лиги (по умолчанию с 13.11.2026 для PoE 1)
* `30.10.2026` или `2026-10-30` — статистика начиная с указанной даты
* `--poe2` (или `-2`) — переключение на анализ логов Path of Exile 2
* `--overlay` (или `-o`) — запуск в виде полупрозрачного окна поверх игры
* `--blight` (или `-b`) — режим трекинга Скверны (карты, Кассия, масла)
* `--bg` — запуск оверлея в фоновом режиме (не зависит от окна терминала)
* `--debug` (или `-d`) — запись подробного лога отладки в `tracker.log`
* `--update` (или `-u`) — проверка и установка обновлений с GitHub
* `--live` (или `-l`) — режим автообновления прямо в терминале

### Ручная настройка пути к `Client.txt`
При первом запуске скрипт сам ищет `Client.txt` и сохраняет путь в файл **`config.json`**. Если игра установлена в нестандартную папку, создайте или отредактируйте `config.json` рядом со скриптом:
```json
{
  "log_path_poe1": "D:/Games/Path of Exile/logs/Client.txt",
  "log_path_poe2": "D:/Games/Path of Exile 2/logs/Client.txt"
}
```

---
## 🇬🇧 English Documentation

### Features
* **Path of Exile 1 (Heist):** Tracks solo contracts and Grand Heist blueprints (including wing counts, zone breakdown, average clear time, and personal speed records).
* **Path of Exile 2:** Tracks Trial of the Sekhemas (runs & floors), Trial of Chaos (runs & rooms), Pinnacle bosses, Citadels, and Atlas maps.
* **Farm Pace Analytics:** Calculates real runs/hour, active run time vs. hideout/harbour downtime, and average pit-stop duration.
* **In-Game Overlay:** Borderless, semi-transparent, draggable overlay widget (requires **Windowed Fullscreen** mode in game graphics settings).

### Installation & Usage
* **Linux (Python):**
  1. Ensure `tkinter` is installed: `sudo apt install python3-tk` (Ubuntu/Debian), `sudo pacman -S tk` (Arch), or `sudo dnf install python3-tkinter` (Fedora).
  2. PoE 1 Overlay: `./start_overlay.sh` or `python3 heist_stats.py today --overlay`
  3. PoE 2 Overlay: `./start_poe2_overlay.sh` or `python3 heist_stats.py --poe2 today --overlay`
* **Linux (Standalone Binary):**
  * Run `./dist/poe-tracker today --overlay` (no Python installation required).
* **Windows:**
  * Run **`install_windows.bat`** to automatically install Python (via `winget` if missing) and create Desktop shortcuts for both PoE 1 and PoE 2 overlays.

### CLI Arguments
* `today` — filter runs for the current day only
* `YYYY-MM-DD` or `DD.MM.YYYY` — filter runs starting from a specific date
* `--poe2` (or `-2`) — switch to Path of Exile 2 log parsing
* `--overlay` (or `-o`) — launch the always-on-top GUI overlay
* `--live` (or `-l`) — live auto-refreshing mode in the terminal

### Custom `Client.txt` Path
On first launch, the tracker automatically detects `Client.txt` and saves it to **`config.json`**. For custom game directories, edit `config.json` in the script folder:
```json
{
  "log_path_poe1": "D:/Games/Path of Exile/logs/Client.txt",
  "log_path_poe2": "D:/Games/Path of Exile 2/logs/Client.txt"
}
```

---

### Авторство и дисклеймер / Author & Disclaimer

* **Автор / Author:** MuonSuzuki
* **Дисклеймер (RU):** Данный проект и его исходный код созданы с использованием инструментов искусственного интеллекта (ИИ). Утилита распространяется «как есть» (as-is) и взаимодействует исключительно с локальным текстовым файлом журнала `Client.txt`, не нарушая правила использования Path of Exile.
* **Disclaimer (EN):** This project and its source code were created with the assistance of Artificial Intelligence (AI). Provided "as-is"; the tool only reads the local `Client.txt` log file and does not interact with or modify the game client.
