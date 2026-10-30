# A SLIPERY CLIMB 1.4

A small, slippery climbing game about a Santa who has to get up a very big
mountain to deliver presents. There is no walk button: you move by throwing
candy and letting the explosions push you around.

Available for **Windows, macOS and Linux**.

## What's new in 1.4

- **Easy mode with 8 checkpoints.** When you create a new save the game asks how
  you want to climb. In **Easy** mode every checkpoint platform carries a flag:
  touch it and it turns from red to green with a little sparkle and a "ding",
  and the save remembers that checkpoint. If you fall, the screen fades and you
  are back at the last checkpoint you touched. **Normal** mode has no
  checkpoints and plays exactly like before.
- **Checkpoints on the climb progress bar.** Reached checkpoints are green
  diamonds on the left edge, the ones ahead are red, and a pulsing arrow points
  at the next one when you get close. The Easy HUD also shows `Checkpoint n/8`.
- **Fullscreen / window mode.** Settings now has a **Fullscreen** switch:
  on = borderless fullscreen, off = a normal window. It takes effect after a
  game restart (the menu tells you), and every screen and menu scales to the
  window.
- **Voices in 9 languages.** Santa's idle chatter and the two taunts he says
  after a big fall are now spoken out loud in all nine languages. Settings has
  a new **Voice** slider next to Sound and Music, with its own volume.
- **Alt now toggles the cursor** instead of requiring you to hold it.
- **Moving platforms feel right.** Landing on a ferry or elevator now hands your
  momentum over to the platform properly (no more platform speed stacking onto
  your own, and no sudden stop), leaving one gives the platform's momentum back,
  and the camera rides along with the platform.
- **Windy ridge reworked.** The wind pushes in three fixed bands with diagonal
  snow streaks and a smooth fade in/out, so it is clear where it starts and ends.
- **Smaller things:** updated tutorial text for the new cursor behaviour, save
  slots show whether a run is Easy or Normal, and the Windows/macOS builds
  report version 1.4.0.

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
- **Easy mode with 8 checkpoints** (chosen when you create a new save)
- **Full voice-over in 9 languages** for idle chatter and fall taunts, with
  separate sound, music and voice volume sliders
- **Fullscreen or window mode**
- 9 languages: English, Русский, 中文, 日本語, 한국어, Deutsch, Français,
  Italiano, Español (fonts included)
- Intro / victory cutscenes, idle chatter, a tutorial page, 5-rank achievements
  with on-screen popups, 5 save slots
- Clearing the mountain deletes that save slot

## Controls

| Input | Action |
|---|---|
| Mouse | aim and throw candy |
| Alt | toggle the cursor while playing |
| Esc | save and return to the menu |
| Space / Enter | skip the intro cutscene |

## Notes

Settings, achievements and saves are stored in:

- Windows: `%APPDATA%\A Slipery Climb`
- macOS: `~/Library/Application Support/A Slipery Climb`
- Linux: `~/.local/share/A Slipery Climb`

---

# A SLIPERY CLIMB 1.4 — 中文

一个关于圣诞老人的小游戏：他要爬上很高的山，把礼物送到山顶的小屋。没有“走”键，
只能靠扔糖果、借爆炸反冲往上爬。

提供 **Windows、macOS 和 Linux** 版本。

## 1.4 更新内容

- **简单模式 + 8 个检查点**：新建存档时会先问你用哪种方式爬。选**简单**，每个
  检查点平台上都会插一面旗子：碰到它，旗子会从红色变成绿色，带一点金光和“叮”
  的一声，存档也会记住这个检查点。掉下去会淡出、回到你最后碰到的检查点。
  **常规**模式没有检查点，和以前完全一样。
- **进度条上的检查点标记**：已到达的检查点是左边缘的绿色菱形，还没到的是红色；
  快接近下一个检查点时会有跳动的箭头指向它。简单模式顶部还会显示
  `检查点 n/8`。
- **全屏 / 窗口模式**：设置里新增**全屏**开关——开 = 无边框全屏，关 = 普通窗口。
  重启游戏后生效（菜单里有提示），所有界面都会按窗口大小自适应。
- **9 种语言配音**：圣诞老人的闲聊，以及大摔之后头顶的两句嘲讽，现在都会用九种
  语言念出来。设置里新增**语音**音量条，和音效、音乐分开调。
- **Alt 改成切换光标**（不用再按住）。
- **移动平台手感修正**：落在渡台/电梯上时，动量会正确地交给平台（不再把平台速度
  叠到你身上，也不会突然急停）；离开平台会把平台动量还给你，镜头也会跟着平台走。
- **风口山脊重做**：风分成三段固定方向，配上斜向雪线，进风和出风都有淡入淡出，
  能看清哪里开始刮风。
- **其它小改动**：光标相关的教程文字更新；存档列表会标出这一局是简单还是常规；
  Windows/macOS 包内版本号更新为 1.4.0。

**下载**：按系统选对应文件——Windows 用 `ASliperyClimb_Windows.zip`；macOS 用
`ASliperyClimb_macOS.zip`；Linux 用 `ASliperyClimb_Linux.tar.gz`，或安装
`ASliperyClimb_Linux_amd64.deb` / `ASliperyClimb_Linux_x86_64.rpm`。不需要安装
Python 或 pygame。

**首次启动**：Windows 若提示“Windows 已保护你的电脑”→ 更多信息 → 仍要运行；
macOS 若无法验证 → 系统设置 → 隐私与安全性 → 仍要打开（或
`xattr -dr com.apple.quarantine "A Slipery Climb.app"`）；当前 macOS 版为 Apple
Silicon 专用。

**操作**：鼠标瞄准并扔糖果；**Alt 切换光标**；Esc 保存并回菜单；空格/回车跳过
片头动画。

存档位置：Windows `%APPDATA%\A Slipery Climb`；macOS
`~/Library/Application Support/A Slipery Climb`；Linux `~/.local/share/A Slipery Climb`。

---

# A SLIPERY CLIMB 1.4 — Русский

Небольшой скользкий платформер про Санту, которому нужно подняться на очень
высокую гору и доставить подарки. Кнопки «идти» нет: двигаешься, бросая конфеты
и используя взрывы как реактивную тягу.

Есть сборки для **Windows, macOS и Linux**.

## Что нового в 1.4

- **Лёгкий режим с 8 контрольными точками.** При создании нового сохранения игра
  спрашивает, как хочешь подниматься. В **лёгком** режиме на каждой платформе-
  контрольной точке стоит флаг: коснись его — он сменит красный цвет на зелёный
  со вспышкой и «дзынь», и сохранение запомнит эту точку. Упал — экран затемняется,
  и ты возвращаешься к последней точке. В **обычном** режиме контрольных точек
  нет, всё как раньше.
- **Контрольные точки на полосе восхождения.** Достигнутые — зелёные ромбы у левого
  края, ещё не достигнутые — красные; рядом со следующей появляется пульсирующая
  стрелка. В лёгком режиме сверху видно `Точка n/8`.
- **Полный экран / окно.** В настройках появился переключатель **Полный экран**:
  включён — безрамочный полный экран, выключен — обычное окно. Применяется после
  перезапуска игры (меню об этом пишет), все экраны подстраиваются под окно.
- **Голоса на 9 языках.** Бормотание Санты и две реплики-подколки после сильного
  падения теперь озвучены на всех девяти языках. В настройках появился ползунок
  **Голос** рядом со звуком и музыкой — своя громкость.
- **Alt теперь переключает курсор** (держать не нужно).
- **Движущиеся платформы стали правильными.** При приземлении на паром или лифт
  импульс корректно передаётся платформе (скорость платформы больше не
  прибавляется к твоей, и нет резкой остановки), при уходе с платформы её импульс
  возвращается, а камера едет вместе с платформой.
- **Ветреный хребет переделан.** Ветер дует в трёх фиксированных полосах, с
  диагональными снежными линиями и плавным появлением/исчезновением — видно, где
  он начинается и заканчивается.
- **Мелочи:** обновлён текст обучения про курсор; в слотах сохранений видно,
  лёгкий это режим или обычный; в сборках Windows/macOS версия 1.4.0.

**Скачать:** Windows — `ASliperyClimb_Windows.zip`, macOS —
`ASliperyClimb_macOS.zip`, Linux — `ASliperyClimb_Linux.tar.gz` или пакеты
`ASliperyClimb_Linux_amd64.deb` / `ASliperyClimb_Linux_x86_64.rpm`.
Python и pygame устанавливать не нужно.

**Первый запуск:** Windows — «Windows защитила ваш компьютер» → Подробнее →
Выполнить всё равно; macOS — Системные настройки → Конфиденциальность и
безопасность → Всё равно открыть (или
`xattr -dr com.apple.quarantine "A Slipery Climb.app"`); сборка macOS только для
Apple Silicon.

**Управление:** мышь — прицел и бросок; **Alt** — переключить курсор; Esc —
сохранить и выйти в меню; пробел/Enter — пропустить вступление.

Сохранения: Windows `%APPDATA%\A Slipery Climb`; macOS
`~/Library/Application Support/A Slipery Climb`; Linux `~/.local/share/A Slipery Climb`.
