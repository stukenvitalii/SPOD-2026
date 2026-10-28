# Системы параллельной обработки данных

Материалы курса и практические работы на C++17 и MPI.

Исходники первой работы используют стандартный MPI и подходят для Windows, macOS и Linux. Для macOS добавлены Bash-скрипты; [установка и запуск на Mac](practical-01/README.md#macos).

- `lectures/` — конспекты четырёх лекций.
- `practical-01/` — первая практическая: обмен рангами с нулевым процессом.
- `scripts/setup.ps1` — подготовка MPI для Windows.
- `.tools/` — локальные заголовки и библиотека MPI; не включаются в Git.

## Быстрый запуск

В PowerShell из корня проекта:

```powershell
.\practical-01\build.ps1
.\practical-01\run.ps1 -Mode unordered -Processes 8
.\practical-01\run.ps1 -Mode ordered -Processes 8
```

На этом компьютере уже установлен GCC из MSYS2 UCRT64 (`C:\msys64\ucrt64\bin\g++.exe`). При подготовке проекта установлен Microsoft MPI Runtime, а заголовки и import-библиотека для GCC размещены в `.tools/msmpi/ucrt64`.

## Подготовка после клонирования

Требуются Windows 10/11 x64, PowerShell, GCC UCRT64, Windows `tar` и Microsoft MPI. Установка Runtime может запросить права администратора.

Если GCC отсутствует, установить [MSYS2](https://www.msys2.org/), затем в терминале **MSYS2 UCRT64** выполнить:

```bash
pacman -Syu
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

Если обновление просит закрыть терминал, выполнить это и повторить обновление после открытия терминала. Не смешивать компиляторы UCRT64 и MINGW64.

Затем в PowerShell из корня проекта:

```powershell
.\scripts\setup.ps1
.\practical-01\build.ps1
.\practical-01\check.ps1
```

`setup.ps1` устанавливает Runtime через `winget`, скачивает фиксированную версию пакета MPI для GCC, проверяет SHA-256 и распаковывает её внутри проекта. Существующий MSYS2 не обновляет. Отдельный Microsoft SDK для Visual Studio здесь не требуется.

Если выполнение `.ps1` запрещено политикой PowerShell, отдельный запуск можно выполнить так:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\practical-01\build.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\practical-01\run.ps1 -Mode ordered -Processes 8
```

Постоянно менять системную политику для этого не нужно. При другом расположении компилятора передайте `-Compiler` в `setup.ps1` и `build.ps1`; каталог с его DLL должен быть доступен через `PATH` при запуске.

## Git

Основная ветка — `main`. Репозиторий: [SPOD-2026](https://github.com/stukenvitalii/SPOD-2026). Сборки, скачанные зависимости, временные замеры и материалы проверки в Git не включаются. Первичные данные, использованные в отчёте, сохранены отдельно в `practical-01/report/measurements.csv`.

## Документация

- [Запуск и замеры первой работы](practical-01/README.md).
- [Отчёт и данные эксперимента](practical-01/report/README.md).
- [Требования преподавателя к отчёту](practical-01/requirements.md).

Источники зависимостей: [Microsoft MPI](https://www.microsoft.com/en-us/download/details.aspx?id=105289), [пакет MSYS2 UCRT64](https://packages.msys2.org/packages/mingw-w64-ucrt-x86_64-msmpi?repo=ucrt64).
