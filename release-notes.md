# A SLIPERY CLIMB 1.2

A small, slippery climbing game about a Santa who has to get up a very big
mountain to deliver presents. There is no walk button: you move by throwing
candy and letting the explosions push you around.

Available for **Windows, macOS and Linux**.

## What's new in 1.2

- **New wind zone.** On the exposed ridge (89–99 m) a periodic sideways gust
  pushes you off your line. Drifting wind streaks show when it is blowing, and a
  sign on the cliff warns you before you get there.
- **Throw trajectory preview.** While aiming, a dotted arc shows where the candy
  will fly; it stops at the first obstacle and marks the landing spot.
- **macOS fix:** the game now uses a real fullscreen window, so clicks no longer
  fall through to the application behind it.
- **Fixed a crash** when pressing Enter on the main menu.
- Two ridge platforms were moved for smoother jumps.

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
  drop jumps, ferries, elevators, curved moving platforms and a windy ridge
- Candy-bomb movement: throw backwards to slide forwards, blast-jump, ride
  platforms; a dotted trajectory preview while aiming
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

# A SLIPERY CLIMB 1.2 — 中文

一个关于圣诞老人的小游戏：他要爬上很高的山，把礼物送到山顶的小屋。没有“走”键，
只能靠扔糖果、借爆炸反冲往上爬。

提供 **Windows、macOS 和 Linux** 版本。

## 1.2 更新内容

- **新增“山脊风区”**：在 89–99 米的山脊段会有周期性横风把你往侧面推；
  风区里会飘过风线，悬崖边还有一块提示牌提前警告。
- **抛掷轨迹预览**：瞄准时显示糖果的虚线飞行轨迹，碰到第一个障碍就停下，
  并在落点画一个标记。
- **macOS 修复**：改用真正的全屏窗口，点击不会再穿透到后面的应用。
- **修复主菜单按回车崩溃**的问题。
- 山脊段有两块平台做了位置调整，跳跃更顺。

**下载**：按系统选对应文件——Windows 用 `ASliperyClimb_Windows.zip`，macOS 用
`ASliperyClimb_macOS.zip`，Linux 用 `ASliperyClimb_Linux.tar.gz` 或
`ASliperyClimb_Linux_amd64.deb` / `ASliperyClimb_Linux_x86_64.rpm` 安装包。
不需要安装 Python 或 pygame。

- 手工关卡（Getting Over It 风格）：台阶、陡梯、下跳、渡船、电梯、弧线移动平台，
  以及一段有风的山脊
- 9 种语言（含中文）、开场/通关过场（可跳过）、带等级和弹窗提示的成就、5 个存档位
- 操作：鼠标扔糖果，Esc 保存并回菜单，空格跳过长场

存档位置：Windows `%APPDATA%\A Slipery Climb`；macOS
`~/Library/Application Support/A Slipery Climb`；Linux `~/.local/share/A Slipery Climb`。

---

# A SLIPERY CLIMB 1.2 — Русский

Небольшой «скользкий» платформер про Санту, которому нужно подняться на большую
гору и доставить подарки. Кнопки «идти» нет: двигаешься только бросками конфет и
взрывами.

Есть сборки для **Windows, macOS и Linux**.

## Что нового в 1.2

- **Новый ветреный участок.** На открытом гребне (89–99 м) периодические боковые
  порывы сбивают с линии; в зоне ветра пролетают полосы, а у обрыва стоит
  предупреждающая табличка.
- **Показ траектории конфеты.** При прицеливании видно пунктирную дугу полёта —
  она обрывается на первом препятствии и отмечает точку падения.
- **Исправление для macOS:** игра теперь открывается в настоящем полноэкранном
  окне, клики больше не проваливаются в приложение позади.
- **Исправлен вылет** при нажатии Enter в главном меню.
- Две платформы на гребне сдвинуты для более удобных прыжков.

**Скачать**: Windows — `ASliperyClimb_Windows.zip`, macOS —
`ASliperyClimb_macOS.zip`, Linux — `ASliperyClimb_Linux.tar.gz`,
`ASliperyClimb_Linux_amd64.deb` или `ASliperyClimb_Linux_x86_64.rpm`.
Python и pygame устанавливать не нужно.

- ручной уровень в духе Getting Over It: лестницы, прыжки вниз, паромы, лифты,
  изогнутые платформы и ветреный гребень
- 9 языков, включая русский, катсцены (можно пропустить), достижения с уровнями
  и всплывающими уведомлениями, 5 слотов сохранения
- управление: мышь — бросок конфеты, Esc — сохранить и в меню, пробел — пропустить катсцену

Настройки и сохранения: `%APPDATA%\A Slipery Climb` (Windows),
`~/Library/Application Support/A Slipery Climb` (macOS),
`~/.local/share/A Slipery Climb` (Linux).
