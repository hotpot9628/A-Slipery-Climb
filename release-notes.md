# A SLIPERY CLIMB 1.3

A small, slippery climbing game about a Santa who has to get up a very big
mountain to deliver presents. There is no walk button: you move by throwing
candy and letting the explosions push you around.

Available for **Windows, macOS and Linux**.

## What's new in 1.3

This is the biggest update so far.

- **Climb progress bar.** A Santa marker on the left edge shows how many metres
  you have climbed.
- **Achievements rewritten.** Every achievement now has five ranks
  (Iron → Bronze → Gold → Platinum → Diamond), each rank has its own page,
  every achievement has an icon whose background colour matches the rank, and
  locked entries are dimmed but still show their condition. A separate red
  **Hidden** page shows `???` until you unlock those surprises.
  - 6 normal achievements: Cloud Walker (height), Summit Legend (clears),
    Candy Storm (throws), Aerial Ace (air throws), Sky Dweller (air time),
    Trailblazer (different platforms)
  - a handful of hidden achievements to discover — their names and
    conditions stay secret until you unlock them
  - Ranks and hidden unlocks are saved permanently; popups only appear for new
    personal records.
- **Jingle Bells at the summit.** Reach the peak near the cabin: the main theme
  fades out and a slow music-box Jingle Bells fades in. It returns to the normal
  theme when you go back to the menu or start a new run.
- **Longer victory cutscene (20 s, unskippable).** Snow, the Santa walking to
  the cabin, presents, fireworks, five lines of text and a "highest point" recap.
  The intro cutscene can still be skipped.
- **Tutorials stay on screen.** The yellow lines in the level no longer hide
  themselves after being read, and there is a new **Tutorial** menu page with
  five illustrated pages (aiming, throw strength, recoil movement, progress bar,
  cursor).
- **Falling retry tip.** Fall three times at the same spot and a short 5-second
  tip appears when you get back up there.
- **No pointer while playing.** The aim arc and the force meter under the
  character show everything; hold **Alt** to bring the pointer back. Menus,
  cutscenes and the victory screen always show the cursor. macOS no longer
  leaves a stuck OS cursor.
- **Bundled fonts.** The game now ships its own CJK font subsets, so Chinese,
  Japanese and Korean are readable even on systems with no fonts installed.
- **Saves are safer.** Atomic writes, corrupt saves no longer crash the game,
  the game saves when the window is closed, loaded saves reset run state, and
  the player's momentum is saved with the position.
- **Long falls no longer clip through platforms** (fall speed cap + landing
  check).
- **Summit polish:** less sticky summit ground, clearer "take the presents to
  the cabin" text, no leftover debug text.
- **Delete a save asks first.**
- **Localised menu title** for all 9 languages (each keeps a deliberate typo,
  just like SLIPERY).
- Packages now include the licence, art/audio notice and third-party notices,
  plus a `SHA256SUMS.txt` file. Windows/macOS builds carry proper version info.

## Download

| OS | File | Notes |
|---|---|---|
| 🪟 **Windows** | `ASliperyClimb_Windows.zip` | unpack and run `A Slipery Climb.exe` |
| 🍎 **macOS** | `ASliperyClimb_macOS.zip` | unpack and open `A Slipery Climb.app` (Apple Silicon) |
| 🐧 **Linux** | `ASliperyClimb_Linux.tar.gz` | unpack, then run `A Slipery Climb/A Slipery Climb` |
| 🐧 **Debian / Ubuntu / Astra** | `ASliperyClimb_Linux_amd64.deb` | `sudo apt install ./ASliperyClimb_Linux_amd64.deb` |
| 🐧 **Fedora / RHEL / openSUSE / ALT** | `ASliperyClimb_Linux_x86_64.rpm` | `sudo dnf install ./ASliperyClimb_Linux_x86_64.rpm` |

No installation of Python or pygame is needed — every build is self-contained.
`SHA256SUMS.txt` lets you verify the downloads.

### First launch

- **Windows**: *"Windows protected your PC"* → **More info → Run anyway**
  (the exe is not code-signed).
- **macOS**: if macOS says it cannot verify the app, open
  **System Settings → Privacy & Security**, scroll to *Security* and click
  **Open Anyway** (macOS 15+), or run
  `xattr -dr com.apple.quarantine "A Slipery Climb.app"` once in Terminal
  (the app is not notarized). The current build is Apple Silicon only.
- **Linux**: `chmod +x "A Slipery Climb/A Slipery Climb"` if needed.

## What's in the game

- Hand-made level in the spirit of *Getting Over It*: stairs, steep ladders,
  drop jumps, ferries, elevators, curved moving platforms and a windy ridge
- Candy-bomb movement: throw backwards to slide forwards, blast-jump, ride
  platforms; a dotted trajectory preview while aiming
- 9 languages: English, Русский, 中文, 日本語, 한국어, Deutsch, Français,
  Italiano, Español (fonts included)
- Intro / victory cutscenes, idle chatter, a tutorial page, 5-rank achievements
  with on-screen popups, 5 save slots
- Clearing the mountain deletes that save slot

## Controls

| Input | Action |
|---|---|
| Mouse | aim and throw candy |
| Alt (hold) | show the cursor while playing |
| Esc | save and return to the menu |
| Space / Enter | skip the intro cutscene |

## Notes

Settings, achievements and saves are stored in:

- Windows: `%APPDATA%\A Slipery Climb`
- macOS: `~/Library/Application Support/A Slipery Climb`
- Linux: `~/.local/share/A Slipery Climb`

---

# A SLIPERY CLIMB 1.3 — 中文

一个关于圣诞老人的小游戏：他要爬上很高的山，把礼物送到山顶的小屋。没有“走”键，
只能靠扔糖果、借爆炸反冲往上爬。

提供 **Windows、macOS 和 Linux** 版本。

## 1.3 更新内容

这是目前最大的一次更新。

- **攀爬进度条**：左侧圣诞老人标记显示你已经爬了多少米。
- **成就系统重做**：每个成就 5 个段位（黑铁→青铜→黄金→铂金→钻石），每个段位
  单独一页；每个成就有自己的图标，图标底色随段位变化；未解锁变暗但仍显示条件。
  另有一栏红色**隐藏成就**，解锁前名字和条件都显示 `???`，自己去发现吧。
  - 常规 6 个：云端行者（高度）、山顶传奇（通关次数）、糖果风暴（扔糖数）、
    空中王牌（空中扔糖）、天空居民（滞空时间）、踏遍群山（站上不同平台）
  - 段位和解锁永久保存；只有刷新个人纪录才会弹提示。
- **山顶《Jingle Bells》**：爬上山顶小屋附近，主音乐淡出、八音盒版 Jingle Bells
  缓慢淡入；回菜单或开新局自动恢复普通音乐。
- **更长的通关动画（20 秒，不可跳过）**：飘雪、圣诞老人走向小屋、礼物、烟花、
  五句台词和“最高点”回顾。片头动画仍可跳过。
- **教学常驻**：关卡里的黄色教学文字不再消失；菜单新增**教程**页，5 页图文
  （瞄准、力度、后坐力移动、进度条、光标）。
- **老摔点提示**：同一个地方掉下去 3 次，再爬回来会显示 5 秒小提示。
- **游玩时隐藏鼠标**：抛物线和角色脚下的力度条足够瞄准；按住 **Alt** 可唤出光标，
  菜单/动画/胜利界面则一直显示。macOS 不再残留系统光标。
- **内置字体**：自带中日韩字体子集，系统没装字体也能正常显示；俄语改用系统默认
  字体（Ж 不再显示成方块）。
- **存档更安全**：原子写入、坏档不崩溃、关窗自动保存、读档重置本局状态，
  坐标和速度一起保存。
- **高处坠落不再穿平台**（限速 + 落地检测）。
- **山顶打磨**：地面不再那么黏、“把礼物送到小屋”文案更清楚、去掉调试文字。
- **删除存档会先确认**。
- **菜单标题本地化**：9 种语言各有自己的“故意笔误”，对应英文的 SLIPERY。
- 安装包附带许可证、美术/音频声明、第三方声明和 `SHA256SUMS.txt`；
  Windows/macOS 包内写入正确版本号。

**下载**：按系统选对应文件——Windows 用 `ASliperyClimb_Windows.zip`；macOS 用
`ASliperyClimb_macOS.zip`；Linux 用 `ASliperyClimb_Linux.tar.gz`，或安装
`ASliperyClimb_Linux_amd64.deb` / `ASliperyClimb_Linux_x86_64.rpm`。不需要安装
Python 或 pygame。

**首次启动**：Windows 若提示“Windows 已保护你的电脑”→ 更多信息 → 仍要运行；
macOS 若无法验证 → 系统设置 → 隐私与安全性 → 仍要打开（或
`xattr -dr com.apple.quarantine "A Slipery Climb.app"`）；当前 macOS 版为 Apple
Silicon 专用。

**操作**：鼠标瞄准并扔糖果；按住 Alt 显示光标；Esc 保存并回菜单；空格/回车跳过
片头动画。

存档位置：Windows `%APPDATA%\A Slipery Climb`；macOS
`~/Library/Application Support/A Slipery Climb`；Linux `~/.local/share/A Slipery Climb`。

---

# A SLIPERY CLIMB 1.3 — Русский

Небольшой скользкий платформер про Санту, которому нужно подняться на очень
высокую гору и доставить подарки. Кнопки «идти» нет: двигаешься, бросая конфеты
и используя взрывы как реактивную тягу.

Есть сборки для **Windows, macOS и Linux**.

## Что нового в 1.3

- **Полоса восхождения:** слева Санта-маркер показывает, сколько метров пройдено.
- **Достижения переделаны:** у каждого достижения пять рангов
  (Железо → Бронза → Золото → Платина → Алмаз), для каждого ранга отдельная
  страница; у каждого достижения свой значок, цвет фона зависит от ранга;
  закрытые записи затемнены, но условие видно. Отдельная красная страница
  **Скрытые** показывает `???` до разблокировки.
  - 6 обычных: Идущий по облакам, Легенда вершины, Конфетный шторм,
    Воздушный ас, Небесный житель, Первопроходец
  - несколько скрытых достижений: их имена и условия остаются тайной до
    разблокировки
  - Ранги и скрытые достижения сохраняются навсегда; уведомления — только за
    новые личные рекорды.
- **Jingle Bells на вершине:** у хижины основная музыка затихает и медленно
  вступает музыкальная шкатулка с Jingle Bells; при возврате в меню или новой
  игре включается обычная тема.
- **Более длинная финальная кат-сцена (20 с, без пропуска):** снег, Санта идёт
  к хижине, подарки, фейерверки, пять реплик и итог «высшая точка». Вступление
  по-прежнему можно пропустить.
- **Обучение остаётся на экране:** жёлтые подсказки уровня больше не исчезают,
  а в меню появилась страница **Обучение** из пяти иллюстрированных страниц.
- **Подсказка после падений:** упал три раза в одном месте — вернувшись, увидишь
  подсказку на 5 секунд.
- **Курсор скрыт во время игры:** дуга броска и полоска силы у персонажа
  показывают всё; удерживай **Alt**, чтобы вернуть курсор. В меню, кат-сценах и
  на экране победы он виден всегда. macOS больше не оставляет системный курсор.
- **Встроенные шрифты:** игра несёт собственные подмножества CJK-шрифтов, поэтому
  китайский, японский и корейский читаются даже без установленных шрифтов;
  русский использует системный шрифт (Ж больше не квадратик).
- **Сохранения надёжнее:** атомарная запись, битые файлы не роняют игру,
  сохранение при закрытии окна, при загрузке состояние забега сбрасывается,
  координаты и скорость сохраняются вместе.
- **Падения с высоты больше не проваливаются сквозь платформы.**
- **Полировка вершины:** менее липкий пол, понятный текст про хижину, убран
  отладочный текст.
- **Удаление сохранения спрашивает подтверждение.**
- **Локализованное название в меню** для 9 языков (в каждом — намеренная опечатка,
  как SLIPERY в английском).
- В пакеты добавлены лицензия, уведомление об арте/аудио, сторонние уведомления и
  `SHA256SUMS.txt`; у сборок Windows/macOS правильные номера версий.

**Скачать:** Windows — `ASliperyClimb_Windows.zip`, macOS —
`ASliperyClimb_macOS.zip`, Linux — `ASliperyClimb_Linux.tar.gz` или пакеты
`ASliperyClimb_Linux_amd64.deb` / `ASliperyClimb_Linux_x86_64.rpm`.
Python и pygame устанавливать не нужно.

**Первый запуск:** Windows — «Windows защитила ваш компьютер» → Подробнее →
Выполнить всё равно; macOS — Системные настройки → Конфиденциальность и
безопасность → Всё равно открыть (или
`xattr -dr com.apple.quarantine "A Slipery Climb.app"`); сборка macOS только для
Apple Silicon.

**Управление:** мышь — прицел и бросок; Alt — показать курсор; Esc — сохранить и
выйти в меню; пробел/Enter — пропустить вступление.

Сохранения: Windows `%APPDATA%\A Slipery Climb`; macOS
`~/Library/Application Support/A Slipery Climb`; Linux `~/.local/share/A Slipery Climb`.
