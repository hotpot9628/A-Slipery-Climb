# A SLIPERY CLIMB · SUMMIT — 1.5.0

**The first official release.** Versions 1.0 – 1.4.1 were preview builds; this
one is the real thing. Everything below is new since 1.4.1.

## New in 1.5

### Free Climb (after the first Regular-mode clear)
Clear the mountain once in **Regular** mode and an extra button appears on the
victory screen and in the main menu. An Easy-mode clear does not count. It opens
the whole mountain as a sandbox:

- a map of the entire climb sits in the top-right corner — click it (or press
  **M**) to expand it
- **right-click** anywhere on the expanded map to teleport there; the game picks
  the nearest ledge and drops you on it
- achievements are disabled in this mode, and the summit no longer traps you:
  jump off whenever you want
- nothing is saved — it is a sandbox, not a save slot
- the first clear of every profile explains the new mode right on the victory
  screen

### Profiles (accounts)
One computer, several players: each profile gets its own five save slots, its own
achievements, its own "cleared" status and its own Free Climb unlock. Create,
rename and delete profiles on the new **Profiles** screen. Your existing saves
and achievements are moved into the first profile automatically, so nothing is
lost.

### Run timer
The current run time is shown next to the Exit button. It pauses while the
Free Climb map is open, stops when you reach the summit, and is shown on the
victory screen. Saved runs keep their time.

### Quit confirmation
Closing the window or pressing **Exit** asks "Quit the game?" first.

### Update prompt
The first official release already knows how to tell you about the next one:

- at start-up the game quietly asks GitHub Releases for the newest version;
  if there is something newer, the main menu shows "Update available" with
  an **Open download page** button
- **Later** hides it for this run; **Skip this version** remembers your choice
  for that version only
- only `https://api.github.com` is contacted - no personal data is sent, and
  nothing is downloaded or installed automatically
- offline or rate-limited? The game simply starts without a prompt

## Fixed in 1.5

- **Esc** now returns to the menu from the Saves, Settings and Profiles screens
- **Back / Return** wording unified — every screen says **Back** now
- one button style everywhere: buttons are blue again, including the in-game
  Exit button, the slider +/− buttons, the fullscreen toggle, the language
  picker and the new Free Climb buttons
- every button now has rounded corners
- **Free Climb:** leaving the summit restores the normal ice friction, and the
  summit's invisible wall is off in that mode
- **Free Climb:** the minimap and the welcome banner explain the map and that
  achievements are off
- **Free Climb:** reaching the summit no longer switches to the Jingle Bells
  summit theme (that stays for the real climb)
- **Free Climb:** the map teleport can now reach the final summit platform too
- the quit dialog pauses the whole game while it is open
- profile names can be typed with any input method (Chinese, Japanese,
  Korean); the IME composition is shown in the field
- the name box is bigger and counts characters, **Ctrl+V** pastes a name
  typed elsewhere, and Enter no longer submits while the IME is composing
- Korean profile names now render correctly (the CJK font has no Hangul
  glyphs), and symbols the fonts cannot draw are filtered out
- corrupted or hand-edited save / profile files can no longer crash the game
- the game is now built with **Python 3.8**, so it also runs on older
  machines and older Linux distributions

*1.0 – 1.4.1 stay available in Releases and are now marked as pre-release.*

---

# A SLIPERY CLIMB · SUMMIT — 1.5.0 — 中文

**首个正式版本。** 1.0 – 1.4.1 都是预览版，这一版才是正式发布。以下都是 1.4.1
之后的新内容。

## 1.5 新增

### 自由攀登（常规模式首次通关后解锁）
用**常规模式**通关一次后，胜利界面和主菜单会多出一个按钮，把整座雪山变成
沙盒（简单模式通关不算）：

- 右上角有一张全山小地图，点击它（或按 **M**）展开
- 在展开的地图上**右键**，就能传送到对应位置（会自动落到最近的平台）
- 这个模式不解锁成就；山顶也不再把你关在里面，随时可以跳下去
- 不占存档位、不会保存
- 每个账号首次通关时，会在胜利界面直接介绍这个新模式

### 账号系统
一台电脑多个玩家：每个账号有独立的 5 个存档位、独立的成就、独立的“是否通关”
和独立的自由攀登解锁。在新加的「账号」界面里新建 / 重命名 / 删除账号。已有的
存档和成就会自动迁移到第一个账号里，不会丢。

### 计时器
左上角（退出按钮旁边）显示本趟用时；打开全图时暂停，登顶后停表，胜利界面也会
显示。带存档的趟次会保留用时。

### 退出确认
点退出或关闭窗口时会先问一句“确定退出游戏吗？”。

### 更新提示
首个正式版就已经会提醒你下一次更新了：

- 启动时后台悄悄向 GitHub Releases 查询最新版本；有新版本时主菜单会显示
  「发现新版本」和「打开下载页」按钮
- 「稍后」本次启动不再提示；「跳过此版本」只跳过这一个版本
- 只连接 `https://api.github.com`，不发送任何个人信息，也不会自动下载/安装
- 断网或被限流时静默跳过，不影响游戏

## 1.5 修复

- **存档、设置、账号**界面按 **Esc** 现在能回主菜单
- 英文的 **Back / Return** 说法统一成 **Back**
- 按钮统一成蓝色：包括游戏里的退出按钮、音量滑块的 +/−、全屏开关、语言选择
  和新加的自由攀登按钮
- 所有按钮都改成了圆角
- **自由攀登**：离开山顶后会恢复正常冰面摩擦力，山顶的隐形墙在该模式下关闭
- **自由攀登**：小地图和开场提示会说明地图玩法和“不解锁成就”
- **自由攀登**：到达山顶后不再切换到 Jingle Bells（那首曲子只属于正式攀登）
- **自由攀登**：全山地图右键传送现在也能传到最终的山顶平台了
- 退出确认弹窗打开时整个游戏暂停
- 账号改名现在支持中日韩等输入法（组字过程显示在输入框里）
- 改名框更大、带字数显示；支持 **Ctrl+V** 粘贴别处打好的名字；
  输入法还在组字时按回车不会误提交
- 韩文账号名现在能正常显示（中文字体里没有韩文字形），
  字体画不出的符号会被过滤掉
- 损坏或被手动改过的存档 / 账号文件不会再让游戏崩溃
- 改用 **Python 3.8** 打包，老一点的电脑和老版本 Linux 也能跑

*1.0 – 1.4.1 仍然可以在 Releases 里下载，现在已经标为预览版。*

---

# A SLIPERY CLIMB · SUMMIT — 1.5.0 — Русский

**Первый официальный релиз.** Версии 1.0 – 1.4.1 были предварительными сборками,
эта — официальная. Всё ниже — новое по сравнению с 1.4.1.

## Новое в 1.5

### Свободный подъём (открывается после первого прохождения в обычном режиме)
Пройди гору один раз в **обычном** режиме — и на экране победы и в главном меню
появится кнопка, которая открывает всю гору как песочницу (лёгкий режим не
считается):

- в правом верхнем углу — карта всей горы; нажми на неё (или **M**), чтобы
  развернуть
- **правый клик** по развёрнутой карте телепортирует туда (игра сама ставит тебя
  на ближайший уступ)
- в этом режиме достижения не открываются, а вершина больше не запирает:
  с неё можно спрыгнуть когда угодно
- режим ничего не сохраняет и не занимает слот
- при первом прохождении каждого профиля этот режим объясняется прямо на экране
  победы

### Профили (аккаунты)
Один компьютер — несколько игроков: у каждого профиля свои 5 слотов сохранения,
свои достижения, свой статус «пройдено» и своя разблокировка Свободного подъёма.
Создавать, переименовывать и удалять профили — на новом экране «Профили». Старые
сохранения и достижения автоматически переезжают в первый профиль, ничего не
теряется.

### Таймер
Время текущего забега показывается рядом с кнопкой выхода. Пауза, пока открыта
карта, остановка на вершине, время видно на экране победы. Сохранённые забеги
сохраняют время.

### Подтверждение выхода
Закрытие окна или кнопка **«Выход»** сначала спрашивают «Выйти из игры?».

### Проверка обновлений
Первый официальный релиз уже умеет сообщать о следующем:

- при запуске игра тихо спрашивает у GitHub Releases последнюю версию; если
  есть новее, в главном меню появляется «Доступно обновление» и кнопка
  **Открыть страницу загрузки**
- **Позже** скрывает напоминание до конца запуска; **Пропустить эту версию**
  запоминает выбор только для этой версии
- связь только с `https://api.github.com`; личные данные не отправляются,
  ничего не скачивается и не устанавливается автоматически
- без сети или при лимите запросов игра просто запускается без напоминания

## Исправлено в 1.5

- **Esc** теперь возвращает в меню с экранов сохранений, настроек и профилей
- **Back / Return** унифицировано — везде **Back**
- единый стиль кнопок: снова синие, включая кнопку выхода в игре, +/− громкости,
  переключатель полного экрана, выбор языка и новые кнопки Свободного подъёма
- у всех кнопок теперь скруглённые углы
- **Свободный подъём:** после ухода с вершины возвращается обычное трение льда,
  невидимая стена на вершине в этом режиме отключена
- **Свободный подъём:** миникарта и приветствие объясняют карту и что достижения
  отключены
- **Свободный подъём:** на вершине больше не включается Jingle Bells (эта музыка
  осталась для настоящего восхождения)
- **Свободный подъём:** телепорт по карте теперь может перенести и на финальную
  вершину
- диалог выхода ставит игру на паузу, пока он открыт
- имя профиля можно ввести любым методом ввода (китайский, японский,
  корейский); композиция IME видна в поле
- поле имени стало больше и показывает число символов; **Ctrl+V** вставляет
  имя, набранное в другом месте; Enter не отправляет имя, пока IME набирает
- корейские имена профилей теперь отображаются правильно (в китайском
  шрифте нет хангыля), а символы, которые шрифты не рисуют, отфильтровываются
- повреждённые или вручную изменённые файлы сохранений и профилей больше не
  роняют игру
- игра теперь собирается на **Python 3.8**, поэтому запускается и на более
  старых машинах и старых дистрибутивах Linux

*Версии 1.0 – 1.4.1 по-прежнему доступны в Releases и теперь помечены как
предварительные.*
