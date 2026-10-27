# A SLIPERY CLIMB 1.1

A small, slippery climbing game about a Santa who has to get up a very big
mountain to deliver presents. There is no walk button: you move by throwing
candy and letting the explosions push you around.

Available for **Windows, macOS and Linux**.

## What's new in 1.1

- **Achievements now pop up on screen while you play.** Reach a new height,
  clear the mountain or throw enough candy in one run, and a card slides in at
  the top of the screen: every level of Climb, Total Clears and Candy Master has
  its own popup, in all 9 languages.
- Linux packages got cleaner file names:
  `ASliperyClimb_Linux_amd64.deb` and `ASliperyClimb_Linux_x86_64.rpm`.

## Download

| OS | File | Notes |
|---|---|---|
| 🪟 **Windows** | `ASliperyClimb_Windows.zip` | unpack and run `A Slipery Climb.exe` |
| 🍎 **macOS** | `ASliperyClimb_macOS.zip` | unpack and open `A Slipery Climb.app` |
| 🐧 **Linux** | `ASliperyClimb_Linux.tar.gz` | unpack, then run `A Slipery Climb/A Slipery Climb` |
| 🐧 **Debian / Ubuntu / Astra** | `ASliperyClimb_Linux_amd64.deb` | `sudo apt install ./ASliperyClimb_Linux_amd64.deb` |
| 🐧 **Fedora / RHEL / openSUSE / ALT** | `ASliperyClimb_Linux_x86_64.rpm` | `sudo dnf install ./ASliperyClimb_Linux_x86_64.rpm` |

No installation of Python or pygame is needed — every build is self-contained.

### First launch

- **Windows**: *"Windows protected your PC"* → **More info → Run anyway**
  (the exe is not code-signed).
- **macOS**: if macOS says it cannot verify the app, open
  **System Settings → Privacy & Security**, scroll to *Security* and click
  **Open Anyway** (macOS 15+), or run
  `xattr -dr com.apple.quarantine "A Slipery Climb.app"` once in Terminal
  (the app is not notarized).
- **Linux**: `chmod +x "A Slipery Climb/A Slipery Climb"` if needed.

## What's in the game

- Hand-made level in the spirit of *Getting Over It*: stairs, steep ladders,
  drop jumps, ferries, elevators, curved moving platforms
- Candy-bomb movement: throw backwards to slide forwards, blast-jump, ride
  platforms
- 9 languages: English, русский, 中文, 日本語, 한국어, Deutsch, Français,
  Italiano, Español
- Intro / victory cutscenes (skippable), idle chatter, leveled achievements with
  on-screen popups, 5 save slots
- Clearing the mountain deletes that save slot

## Controls

| Input | Action |
|---|---|
| Mouse | aim and throw candy |
| Esc | save and return to the menu |
| Space / Enter | skip cutscene |

## Notes

Settings, achievements and saves are stored in:

- Windows: `%APPDATA%\A Slipery Climb`
- macOS: `~/Library/Application Support/A Slipery Climb`
- Linux: `~/.local/share/A Slipery Climb`

---

# A SLIPERY CLIMB 1.1 — 中文

一个关于圣诞老人的小游戏：他要爬上很高的山，把礼物送到山顶的小屋。没有“走”键，
只能靠扔糖果、借爆炸反冲往上爬。

提供 **Windows、macOS 和 Linux** 版本。

## 1.1 更新内容

- **获得成就时，屏幕上会弹出提示。** 爬到新高度、通关一次、或一局扔够糖果时，
  屏幕顶部会滑入一张卡片——登高、通关次数、糖果大师的每一级都有提示，9 种语言都支持。
- Linux 安装包文件改名：`ASliperyClimb_Linux_amd64.deb` 和
  `ASliperyClimb_Linux_x86_64.rpm`。

**下载**：按系统选对应文件——Windows 用 `ASliperyClimb_Windows.zip`，macOS 用
`ASliperyClimb_macOS.zip`，Linux 用 `ASliperyClimb_Linux.tar.gz` 或
`ASliperyClimb_Linux_amd64.deb` / `ASliperyClimb_Linux_x86_64.rpm` 安装包。
不需要安装 Python 或 pygame。

- 手工关卡（Getting Over It 风格）：台阶、陡梯、下跳、渡船、电梯、弧线移动平台
- 9 种语言（含中文）、开场/通关过场（可跳过）、带等级和弹窗提示的成就、5 个存档位
- 操作：鼠标扔糖果，Esc 保存并回菜单，空格跳过长场

存档位置：Windows `%APPDATA%\A Slipery Climb`；macOS
`~/Library/Application Support/A Slipery Climb`；Linux `~/.local/share/A Slipery Climb`。

---

# A SLIPERY CLIMB 1.1 — Русский

Небольшой «скользкий» платформер про Санту, которому нужно подняться на большую
гору и доставить подарки. Кнопки «идти» нет: двигаешься только бросками конфет и
взрывами.

Есть сборки для **Windows, macOS и Linux**.

## Что нового в 1.1

- **При получении достижения на экране появляется уведомление.** Дошёл до новой
  высоты, прошёл игру или бросил много конфет за один забег — вверху экрана
  выезжает карточка. Свои уведомления у каждого уровня «Восхождения», «Прохождений»
  и «Мастера конфет», на всех 9 языках.
- Файлы пакетов Linux переименованы: `ASliperyClimb_Linux_amd64.deb` и
  `ASliperyClimb_Linux_x86_64.rpm`.

**Скачать**: Windows — `ASliperyClimb_Windows.zip`, macOS —
`ASliperyClimb_macOS.zip`, Linux — `ASliperyClimb_Linux.tar.gz`,
`ASliperyClimb_Linux_amd64.deb` или `ASliperyClimb_Linux_x86_64.rpm`.
Python и pygame устанавливать не нужно.

- ручной уровень в духе Getting Over It: лестницы, прыжки вниз, паромы, лифты
- 9 языков, включая русский, катсцены (можно пропустить), достижения с уровнями
  и всплывающими уведомлениями, 5 слотов сохранения
- управление: мышь — бросок конфеты, Esc — сохранить и в меню, пробел — пропустить катсцену

Настройки и сохранения: `%APPDATA%\A Slipery Climb` (Windows),
`~/Library/Application Support/A Slipery Climb` (macOS),
`~/.local/share/A Slipery Climb` (Linux).
