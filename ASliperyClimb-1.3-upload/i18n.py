"""i18n.py - 9-language support and font selection for A SLIPERY CLIMB.

Usage (already wired up in main.py):
    import i18n
    i18n.set_lang("zh")          # en / zh / ja / ko / ru / de / fr / it / es
    i18n.ui("settings")          # UI strings
    i18n.text("Good luck :)")    # in-level text (looked up by English source)
    i18n.get_font(48)            # font for the current language
    i18n.font_for("ja", 24)      # font for a specific language
"""

import glob
import os

import paths

import pygame

LANGS = [
    ("en", "English"),
    ("zh", "中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("ru", "Русский"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("it", "Italiano"),
    ("es", "Español"),
]

UI_EN = {
    "continue": "Continue",
    "new_game": "New Game",
    "reset": "Reset",
    "settings": "Settings",
    "exit": "Exit",
    "sound": "Sound effects",
    "music": "Music",
    "return": "Return",
    "language": "Language",
}

_ZH = {
    "continue": "继续", "new_game": "新游戏", "reset": "重置", "settings": "设置",
    "exit": "退出", "sound": "音效", "music": "音乐", "return": "返回", "language": "语言",
    "Welcome to the game!": "欢迎来到游戏！",
    "Try clicking your left mouse button :)": "试试点击鼠标左键 :)",
    "If you see this": "如果你看到这句",
    "Good job! You learned how to move horizontally": "很好！你学会了横向移动",
    "Hmm...how can we get over this?": "嗯……这要怎么过去？",
    "Maybe try throwing candy so it hits yourself?": "也许可以朝自己扔颗糖？",
    "Wow! you learned how to jump!": "哇！你学会跳了！",
    "You were smarter than I thought!": "你比我想的聪明！",
    "You learned everything you can!": "你已经学会了全部！",
    "Good luck :)": "祝你好运 :)",
    "That way --------->": "那边 --------->",
    "We are getting up aren't we?!": "我们正在往上爬，对吧？！",
    "By the way, I forgot to tell you": "顺便忘了告诉你",
    "You can actually control distance of the throw": "你其实能控制扔的距离",
    "By keeping your mouse closer or further to the character :)": "把鼠标放得离角色更近或更远就行 :)",
    "Go that way, you're not supposed to be here :)": "走那边，你不该来这儿 :)",
    "Left first. Then up.": "先往左。再往上。",
    "This is the top. For now.": "这就是山顶。暂时。",
    "This platform moves. Wait for it, then jump on.": "这块平台会动。等它过来再跳上去。",
    "Stand on it and it will carry you up.": "站上去，它会把你带上去。",
    "That was a long way down.": "这一下摔得可真远。",
    "Gravity: 1. You: 0.": "重力：1，你：0。",
    "You did that on purpose, right?": "你是故意的吧？",
    "The floor is not a checkpoint.": "地板不是检查点。",
    "Skilled players don't do that. Allegedly.": "高手不会这么干。据说。",
    "That is the fast way down.": "这是最快的下山方式。",
    "Your candy misses you.": "你的糖在等你。",
    "Bold strategy.": "好大胆的打法。",
    "Try again. Slower this time.": "再来一次，慢一点。",
    "I would say 'almost', but that would be a lie.": "我本来想说“就差一点”，但那是骗你。",
    "Take the stairs next time.": "下次走楼梯吧。",
    "The mountain is still up there.": "山还在上面。",
    "That was free advice.": "这是免费建议。",
    "Do not worry, nobody saw it.": "别担心，没人看见。",
    "You are doing great. Statistically.": "你做得很好。从统计上讲。",
}

_JA = {
    "continue": "続ける", "new_game": "新しいゲーム", "reset": "リセット", "settings": "設定",
    "exit": "終了", "sound": "効果音", "music": "音楽", "return": "戻る", "language": "言語",
    "Welcome to the game!": "ゲームへようこそ！",
    "Try clicking your left mouse button :)": "マウスの左ボタンを押してみて :)",
    "If you see this": "これが見えたら",
    "Good job! You learned how to move horizontally": "いいね！横移動を覚えたね",
    "Hmm...how can we get over this?": "うーん…どうやって越える？",
    "Maybe try throwing candy so it hits yourself?": "キャンディを自分に投げてみたら？",
    "Wow! you learned how to jump!": "わあ！ジャンプを覚えた！",
    "You were smarter than I thought!": "思ったより賢いね！",
    "You learned everything you can!": "全部覚えたね！",
    "Good luck :)": "がんばって :)",
    "That way --------->": "あっちだ --------->",
    "We are getting up aren't we?!": "上ってるよね？！",
    "By the way, I forgot to tell you": "そういえば言い忘れてた",
    "You can actually control distance of the throw": "投げる距離は調整できるよ",
    "By keeping your mouse closer or further to the character :)": "マウスをキャラに近づけたり離したりしてね :)",
    "Go that way, you're not supposed to be here :)": "あっちへ行って。ここにいるべきじゃないよ :)",
    "Left first. Then up.": "まず左へ。それから上へ。",
    "This is the top. For now.": "ここが頂上。今のところは。",
    "This platform moves. Wait for it, then jump on.": "この足場は動く。来るのを待って飛び乗ろう。",
    "Stand on it and it will carry you up.": "乗れば上まで運んでくれる。",
    "That was a long way down.": "ずいぶん遠くまで落ちたね。",
    "Gravity: 1. You: 0.": "重力：1、あなた：0。",
    "You did that on purpose, right?": "わざとでしょ？",
    "The floor is not a checkpoint.": "床はチェックポイントじゃない。",
    "Skilled players don't do that. Allegedly.": "熟練者はそんなことしない。たぶん。",
    "That is the fast way down.": "それが一番速い下り方だ。",
    "Your candy misses you.": "キャンディが寂しがってる。",
    "Bold strategy.": "大胆な作戦だね。",
    "Try again. Slower this time.": "もう一度。今度はゆっくり。",
    "I would say 'almost', but that would be a lie.": "「あと少し」と言いたいけど、嘘になる。",
    "Take the stairs next time.": "次は階段を使おう。",
    "The mountain is still up there.": "山はまだ上にある。",
    "That was free advice.": "無料の助言だった。",
    "Do not worry, nobody saw it.": "心配しないで、誰も見てない。",
    "You are doing great. Statistically.": "よくやってる。統計的には。",
}

_KO = {
    "continue": "계속", "new_game": "새 게임", "reset": "초기화", "settings": "설정",
    "exit": "종료", "sound": "효과음", "music": "음악", "return": "돌아가기", "language": "언어",
    "Welcome to the game!": "게임에 오신 것을 환영합니다!",
    "Try clicking your left mouse button :)": "마우스 왼쪽 버튼을 눌러보세요 :)",
    "If you see this": "이게 보인다면",
    "Good job! You learned how to move horizontally": "잘했어요! 수평 이동을 배웠네요",
    "Hmm...how can we get over this?": "음... 어떻게 넘어가지?",
    "Maybe try throwing candy so it hits yourself?": "캔디를 자신에게 던져보면?",
    "Wow! you learned how to jump!": "와! 점프를 배웠네요!",
    "You were smarter than I thought!": "생각보다 똑똑하네요!",
    "You learned everything you can!": "배울 건 다 배웠어요!",
    "Good luck :)": "행운을 빌어요 :)",
    "That way --------->": "저쪽이에요 --------->",
    "We are getting up aren't we?!": "올라가고 있죠?!",
    "By the way, I forgot to tell you": "그런데 말하는 걸 깜빡했네요",
    "You can actually control distance of the throw": "던지는 거리를 조절할 수 있어요",
    "By keeping your mouse closer or further to the character :)": "마우스를 캐릭터에 가까이 또는 멀리 두세요 :)",
    "Go that way, you're not supposed to be here :)": "저쪽으로 가세요. 여기 있으면 안 돼요 :)",
    "Left first. Then up.": "먼저 왼쪽. 그다음 위로.",
    "This is the top. For now.": "여기가 정상. 지금은.",
    "This platform moves. Wait for it, then jump on.": "이 발판은 움직여요. 기다렸다가 올라타세요.",
    "Stand on it and it will carry you up.": "올라타면 위로 데려다줘요.",
    "That was a long way down.": "꽤 멀리 떨어졌네요.",
    "Gravity: 1. You: 0.": "중력: 1, 당신: 0.",
    "You did that on purpose, right?": "일부러 그랬죠?",
    "The floor is not a checkpoint.": "바닥은 체크포인트가 아니에요.",
    "Skilled players don't do that. Allegedly.": "고수는 그러지 않아요. 아마도.",
    "That is the fast way down.": "그게 가장 빠른 내려가는 길이에요.",
    "Your candy misses you.": "캔디가 당신을 그리워해요.",
    "Bold strategy.": "대담한 전략이네요.",
    "Try again. Slower this time.": "다시. 이번엔 천천히.",
    "I would say 'almost', but that would be a lie.": "'거의 다 왔어'라고 말하고 싶지만 거짓말이 되겠네요.",
    "Take the stairs next time.": "다음엔 계단을 쓰세요.",
    "The mountain is still up there.": "산은 아직 위에 있어요.",
    "That was free advice.": "공짜 조언이었어요.",
    "Do not worry, nobody saw it.": "걱정 마세요, 아무도 못 봤어요.",
    "You are doing great. Statistically.": "잘하고 있어요. 통계적으로.",
}

_RU = {
    "continue": "Продолжить", "new_game": "Новая игра", "reset": "Сброс", "settings": "Настройки",
    "exit": "Выход", "sound": "Звуки", "music": "Музыка", "return": "Назад", "language": "Язык",
    "Welcome to the game!": "Добро пожаловать в игру!",
    "Try clicking your left mouse button :)": "Попробуй нажать левую кнопку мыши :)",
    "If you see this": "Если ты это видишь",
    "Good job! You learned how to move horizontally": "Молодец! Ты научился двигаться по горизонтали",
    "Hmm...how can we get over this?": "Хм... как это перепрыгнуть?",
    "Maybe try throwing candy so it hits yourself?": "Может, бросить конфету в себя?",
    "Wow! you learned how to jump!": "Ух ты! Ты научился прыгать!",
    "You were smarter than I thought!": "Ты умнее, чем я думал!",
    "You learned everything you can!": "Ты научился всему, чему мог!",
    "Good luck :)": "Удачи :)",
    "That way --------->": "Туда --------->",
    "We are getting up aren't we?!": "Мы ведь поднимаемся?!",
    "By the way, I forgot to tell you": "Кстати, забыл сказать",
    "You can actually control distance of the throw": "Ты можешь управлять дальностью броска",
    "By keeping your mouse closer or further to the character :)": "Держи мышь ближе или дальше от персонажа :)",
    "Go that way, you're not supposed to be here :)": "Иди туда, тебе здесь не место :)",
    "Left first. Then up.": "Сначала влево. Потом вверх.",
    "This is the top. For now.": "Это вершина. Пока что.",
    "This platform moves. Wait for it, then jump on.": "Эта платформа движется. Подожди её и прыгай.",
    "Stand on it and it will carry you up.": "Встань на неё, и она поднимет тебя.",
    "That was a long way down.": "Долго же ты падал.",
    "Gravity: 1. You: 0.": "Гравитация: 1. Ты: 0.",
    "You did that on purpose, right?": "Ты ведь специально, да?",
    "The floor is not a checkpoint.": "Пол — это не чекпоинт.",
    "Skilled players don't do that. Allegedly.": "Опытные так не делают. Говорят.",
    "That is the fast way down.": "Это самый быстрый спуск.",
    "Your candy misses you.": "Твоя конфета скучает по тебе.",
    "Bold strategy.": "Смелая стратегия.",
    "Try again. Slower this time.": "Ещё раз. Медленнее.",
    "I would say 'almost', but that would be a lie.": "Я бы сказал «почти», но это было бы враньё.",
    "Take the stairs next time.": "В следующий раз иди по лестнице.",
    "The mountain is still up there.": "Гора всё ещё наверху.",
    "That was free advice.": "Это был бесплатный совет.",
    "Do not worry, nobody saw it.": "Не волнуйся, никто не видел.",
    "You are doing great. Statistically.": "Ты отлично справляешься. Статистически.",
}

_DE = {
    "continue": "Weiter", "new_game": "Neues Spiel", "reset": "Zurücksetzen", "settings": "Einstellungen",
    "exit": "Beenden", "sound": "Soundeffekte", "music": "Musik", "return": "Zurück", "language": "Sprache",
    "Welcome to the game!": "Willkommen im Spiel!",
    "Try clicking your left mouse button :)": "Klick mal mit der linken Maustaste :)",
    "If you see this": "Wenn du das siehst",
    "Good job! You learned how to move horizontally": "Gut gemacht! Du hast gelernt, dich seitwärts zu bewegen",
    "Hmm...how can we get over this?": "Hm... wie kommt man da rüber?",
    "Maybe try throwing candy so it hits yourself?": "Vielleicht eine Süßigkeit auf dich selbst werfen?",
    "Wow! you learned how to jump!": "Wow! Du hast das Springen gelernt!",
    "You were smarter than I thought!": "Du warst schlauer, als ich dachte!",
    "You learned everything you can!": "Du hast alles gelernt, was du kannst!",
    "Good luck :)": "Viel Glück :)",
    "That way --------->": "Da lang --------->",
    "We are getting up aren't we?!": "Wir steigen auf, oder?!",
    "By the way, I forgot to tell you": "Übrigens, hab ich vergessen zu sagen",
    "You can actually control distance of the throw": "Du kannst die Wurfweite steuern",
    "By keeping your mouse closer or further to the character :)": "Maus näher oder weiter vom Charakter :)",
    "Go that way, you're not supposed to be here :)": "Geh da lang, hier solltest du nicht sein :)",
    "Left first. Then up.": "Erst nach links. Dann nach oben.",
    "This is the top. For now.": "Das ist der Gipfel. Vorerst.",
    "This platform moves. Wait for it, then jump on.": "Diese Plattform bewegt sich. Warte und spring drauf.",
    "Stand on it and it will carry you up.": "Stell dich drauf, sie trägt dich nach oben.",
    "That was a long way down.": "Das war ein weiter Weg nach unten.",
    "Gravity: 1. You: 0.": "Schwerkraft: 1. Du: 0.",
    "You did that on purpose, right?": "Das war Absicht, oder?",
    "The floor is not a checkpoint.": "Der Boden ist kein Checkpoint.",
    "Skilled players don't do that. Allegedly.": "Könner machen das nicht. Angeblich.",
    "That is the fast way down.": "Das ist der schnelle Weg nach unten.",
    "Your candy misses you.": "Deine Süßigkeit vermisst dich.",
    "Bold strategy.": "Mutige Strategie.",
    "Try again. Slower this time.": "Nochmal. Langsamer.",
    "I would say 'almost', but that would be a lie.": "Ich würde „fast“ sagen, aber das wäre gelogen.",
    "Take the stairs next time.": "Nimm nächstes Mal die Treppe.",
    "The mountain is still up there.": "Der Berg ist noch da oben.",
    "That was free advice.": "Das war ein Gratis-Tipp.",
    "Do not worry, nobody saw it.": "Keine Sorge, niemand hat's gesehen.",
    "You are doing great. Statistically.": "Du machst das super. Statistisch.",
}

_FR = {
    "continue": "Continuer", "new_game": "Nouvelle partie", "reset": "Réinitialiser", "settings": "Paramètres",
    "exit": "Quitter", "sound": "Effets sonores", "music": "Musique", "return": "Retour", "language": "Langue",
    "Welcome to the game!": "Bienvenue dans le jeu !",
    "Try clicking your left mouse button :)": "Essaie de cliquer avec le bouton gauche :)",
    "If you see this": "Si tu vois ça",
    "Good job! You learned how to move horizontally": "Bien joué ! Tu as appris à bouger horizontalement",
    "Hmm...how can we get over this?": "Hmm... comment passer par-dessus ?",
    "Maybe try throwing candy so it hits yourself?": "Essaie de te lancer un bonbon dessus ?",
    "Wow! you learned how to jump!": "Waouh ! Tu as appris à sauter !",
    "You were smarter than I thought!": "Tu es plus malin que je pensais !",
    "You learned everything you can!": "Tu as tout appris !",
    "Good luck :)": "Bonne chance :)",
    "That way --------->": "Par là --------->",
    "We are getting up aren't we?!": "On monte, hein ?!",
    "By the way, I forgot to tell you": "Au fait, j'ai oublié de te dire",
    "You can actually control distance of the throw": "Tu peux régler la distance du lancer",
    "By keeping your mouse closer or further to the character :)": "En approchant ou éloignant la souris du personnage :)",
    "Go that way, you're not supposed to be here :)": "Va par là, tu n'es pas censé être ici :)",
    "Left first. Then up.": "D'abord à gauche. Puis en haut.",
    "This is the top. For now.": "C'est le sommet. Pour l'instant.",
    "This platform moves. Wait for it, then jump on.": "Cette plateforme bouge. Attends-la et saute dessus.",
    "Stand on it and it will carry you up.": "Monte dessus, elle te portera vers le haut.",
    "That was a long way down.": "Ça faisait une sacrée chute.",
    "Gravity: 1. You: 0.": "Gravité : 1. Toi : 0.",
    "You did that on purpose, right?": "Tu l'as fait exprès, non ?",
    "The floor is not a checkpoint.": "Le sol n'est pas un checkpoint.",
    "Skilled players don't do that. Allegedly.": "Les pros ne font pas ça. Paraît-il.",
    "That is the fast way down.": "C'est la descente la plus rapide.",
    "Your candy misses you.": "Ton bonbon te regrette.",
    "Bold strategy.": "Stratégie audacieuse.",
    "Try again. Slower this time.": "Encore. Plus lentement.",
    "I would say 'almost', but that would be a lie.": "Je dirais « presque », mais ce serait mentir.",
    "Take the stairs next time.": "Prends l'escalier la prochaine fois.",
    "The mountain is still up there.": "La montagne est toujours là-haut.",
    "That was free advice.": "C'était un conseil gratuit.",
    "Do not worry, nobody saw it.": "Ne t'inquiète pas, personne n'a vu.",
    "You are doing great. Statistically.": "Tu t'en sors très bien. Statistiquement.",
}

_IT = {
    "continue": "Continua", "new_game": "Nuova partita", "reset": "Reimposta", "settings": "Impostazioni",
    "exit": "Esci", "sound": "Effetti sonori", "music": "Musica", "return": "Indietro", "language": "Lingua",
    "Welcome to the game!": "Benvenuto nel gioco!",
    "Try clicking your left mouse button :)": "Prova a premere il tasto sinistro del mouse :)",
    "If you see this": "Se vedi questo",
    "Good job! You learned how to move horizontally": "Bravo! Hai imparato a muoverti in orizzontale",
    "Hmm...how can we get over this?": "Hmm... come si supera?",
    "Maybe try throwing candy so it hits yourself?": "Prova a lanciarti una caramella addosso?",
    "Wow! you learned how to jump!": "Wow! Hai imparato a saltare!",
    "You were smarter than I thought!": "Sei più sveglio di quanto pensassi!",
    "You learned everything you can!": "Hai imparato tutto quello che puoi!",
    "Good luck :)": "Buona fortuna :)",
    "That way --------->": "Da quella parte --------->",
    "We are getting up aren't we?!": "Stiamo salendo, vero?!",
    "By the way, I forgot to tell you": "A proposito, ho dimenticato di dirtelo",
    "You can actually control distance of the throw": "Puoi controllare la distanza del lancio",
    "By keeping your mouse closer or further to the character :)": "Tenendo il mouse più vicino o lontano dal personaggio :)",
    "Go that way, you're not supposed to be here :)": "Vai da quella parte, non dovresti essere qui :)",
    "Left first. Then up.": "Prima a sinistra. Poi in alto.",
    "This is the top. For now.": "Questa è la cima. Per ora.",
    "This platform moves. Wait for it, then jump on.": "Questa piattaforma si muove. Aspettala e saltaci sopra.",
    "Stand on it and it will carry you up.": "Salici sopra, ti porterà in alto.",
    "That was a long way down.": "Che caduta lunga.",
    "Gravity: 1. You: 0.": "Gravità: 1. Tu: 0.",
    "You did that on purpose, right?": "L'hai fatto apposta, vero?",
    "The floor is not a checkpoint.": "Il pavimento non è un checkpoint.",
    "Skilled players don't do that. Allegedly.": "I giocatori esperti non lo fanno. Pare.",
    "That is the fast way down.": "È il modo più veloce per scendere.",
    "Your candy misses you.": "La tua caramella ti manca.",
    "Bold strategy.": "Strategia audace.",
    "Try again. Slower this time.": "Riprova. Più piano.",
    "I would say 'almost', but that would be a lie.": "Direi 'quasi', ma sarebbe una bugia.",
    "Take the stairs next time.": "La prossima volta prendi le scale.",
    "The mountain is still up there.": "La montagna è ancora lassù.",
    "That was free advice.": "Era un consiglio gratis.",
    "Do not worry, nobody saw it.": "Non preoccuparti, nessuno ha visto.",
    "You are doing great. Statistically.": "Stai andando benissimo. Statisticamente.",
}

_ES = {
    "continue": "Continuar", "new_game": "Nueva partida", "reset": "Reiniciar", "settings": "Ajustes",
    "exit": "Salir", "sound": "Efectos de sonido", "music": "Música", "return": "Volver", "language": "Idioma",
    "Welcome to the game!": "¡Bienvenido al juego!",
    "Try clicking your left mouse button :)": "Prueba a hacer clic con el botón izquierdo :)",
    "If you see this": "Si ves esto",
    "Good job! You learned how to move horizontally": "¡Bien hecho! Has aprendido a moverte en horizontal",
    "Hmm...how can we get over this?": "Hmm... ¿cómo se pasa esto?",
    "Maybe try throwing candy so it hits yourself?": "¿Y si te lanzas un caramelo a ti mismo?",
    "Wow! you learned how to jump!": "¡Guau! ¡Has aprendido a saltar!",
    "You were smarter than I thought!": "¡Eres más listo de lo que pensaba!",
    "You learned everything you can!": "¡Has aprendido todo lo que podías!",
    "Good luck :)": "Buena suerte :)",
    "That way --------->": "Por ahí --------->",
    "We are getting up aren't we?!": "Estamos subiendo, ¿verdad?!",
    "By the way, I forgot to tell you": "Por cierto, olvidé decirte",
    "You can actually control distance of the throw": "Puedes controlar la distancia del lanzamiento",
    "By keeping your mouse closer or further to the character :)": "Acercando o alejando el ratón del personaje :)",
    "Go that way, you're not supposed to be here :)": "Ve por ahí, no deberías estar aquí :)",
    "Left first. Then up.": "Primero a la izquierda. Luego arriba.",
    "This is the top. For now.": "Esta es la cima. Por ahora.",
    "This platform moves. Wait for it, then jump on.": "Esta plataforma se mueve. Espérala y salta encima.",
    "Stand on it and it will carry you up.": "Súbete, te llevará hacia arriba.",
    "That was a long way down.": "Vaya caída más larga.",
    "Gravity: 1. You: 0.": "Gravedad: 1. Tú: 0.",
    "You did that on purpose, right?": "Lo hiciste a propósito, ¿eh?",
    "The floor is not a checkpoint.": "El suelo no es un punto de control.",
    "Skilled players don't do that. Allegedly.": "Los expertos no hacen eso. Al parecer.",
    "That is the fast way down.": "Es la forma más rápida de bajar.",
    "Your candy misses you.": "Tu caramelo te echa de menos.",
    "Bold strategy.": "Estrategia valiente.",
    "Try again. Slower this time.": "Otra vez. Más despacio.",
    "I would say 'almost', but that would be a lie.": "Diría «casi», pero sería mentira.",
    "Take the stairs next time.": "La próxima vez usa las escaleras.",
    "The mountain is still up there.": "La montaña sigue ahí arriba.",
    "That was free advice.": "Fue un consejo gratis.",
    "Do not worry, nobody saw it.": "No te preocupes, nadie lo vio.",
    "You are doing great. Statistically.": "Lo estás haciendo genial. Estadísticamente.",
}

STRINGS = {
    "zh": _ZH,
    "ja": _JA,
    "ko": _KO,
    "ru": _RU,
    "de": _DE,
    "fr": _FR,
    "it": _IT,
    "es": _ES,
}

# Wind-zone hint (level text added together with the wind mechanic).
# Keeps all nine languages in sync without touching the big STRINGS literals.
_WIND_HINT = {
    "zh": "前面是风口：稳住落点！",
    "ja": "この先は強風。押されても踏ん張って！",
    "ko": "앞쪽은 돌풍. 밀려도 버텨요!",
    "ru": "Впереди ветер: держи курс!",
    "de": "Böen voraus: halt die Linie!",
    "fr": "Rafales devant : tiens ta ligne !",
    "it": "Raffiche davanti: tieni la linea!",
    "es": "¡Ráfagas delante! Mantén la línea.",
}
for _code, _label in _WIND_HINT.items():
    STRINGS.setdefault(_code, {})["Gusts ahead: hold your line!"] = _label

current = "en"

# Noto Sans SC subset (OFL) shipped with the game: keeps CJK readable on systems
# that have no CJK font installed at all.
BUNDLED_CJK_FONT = paths.asset("fonts", "NotoSansSC-Regular-subset-v2.ttf")
BUNDLED_KO_FONT = paths.asset("fonts", "NotoSansKR-Regular-subset-v2.ttf")


def _bundled_font(code):
    """Fallback font shipped with the game for this CJK language."""
    preferred = BUNDLED_KO_FONT if code == "ko" else BUNDLED_CJK_FONT
    if os.path.exists(preferred):
        return preferred
    if os.path.exists(BUNDLED_CJK_FONT):
        return BUNDLED_CJK_FONT
    return None

# CJK needs a system CJK font; other languages keep the pygame default font (original look)
_FONT_PATHS = {
    "zh": [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf",
           r"C:\Windows\Fonts\simsun.ttc",
           "/System/Library/Fonts/PingFang.ttc",
           "/System/Library/Fonts/Hiragino Sans GB.ttc",
           "/System/Library/Fonts/Supplemental/Songti.ttc",
           "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
           "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
           "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
           "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
           BUNDLED_CJK_FONT],
    "ja": [r"C:\Windows\Fonts\yugothm.ttc", r"C:\Windows\Fonts\msgothic.ttc",
           r"C:\Windows\Fonts\msyh.ttc",
           "/System/Library/Fonts/Hiragino Kaku Gothic ProN.ttc",
           "/System/Library/Fonts/Hiragino Sans GB.ttc",
           "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
           "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
           "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
           BUNDLED_CJK_FONT],
    "ko": [r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\msyh.ttc",
           "/System/Library/Fonts/AppleSDGothicNeo.ttc",
           "/System/Library/Fonts/AppleGothic.ttf",
           "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
           "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
           "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
           BUNDLED_KO_FONT],
}
# Linux distros move these fonts around, so also search by pattern.
_FONT_GLOBS = {
    "zh": ["/usr/share/fonts/**/NotoSansCJK*", "/usr/share/fonts/**/NotoSerifCJK*",
           "/usr/share/fonts/**/wqy*"],
    "ja": ["/usr/share/fonts/**/NotoSansCJK*", "/usr/share/fonts/**/wqy*"],
    "ko": ["/usr/share/fonts/**/NotoSansCJK*", "/usr/share/fonts/**/wqy*"],
}


def _search_glob(code):
    for pattern in _FONT_GLOBS.get(code, []):
        for path in sorted(glob.glob(pattern, recursive=True)):
            if path.lower().endswith((".ttc", ".ttf", ".otf")):
                return path
    return None


def _resolve_fonts():
    table = {}
    for code, paths in _FONT_PATHS.items():
        found = next((p for p in paths if os.path.exists(p)), None)
        if found:
            table[code] = [found]
        else:
            extra = _search_glob(code)
            if extra:
                table[code] = [extra]
            else:
                bundled = _bundled_font(code)
                table[code] = [bundled] if bundled else []
    return table


_FONT_PATHS = _resolve_fonts()
_font_cache = {}


def _font_path(code):
    for path in _FONT_PATHS.get(code, []):
        if os.path.exists(path):
            return path
    extra = _search_glob(code)
    if extra:
        _FONT_PATHS.setdefault(code, []).append(extra)
        return extra
    # The bundled fonts are CJK-only substitutes: other languages keep
    # the pygame default font (it has full Latin/Cyrillic coverage).
    if code in ("zh", "ja", "ko"):
        bundled = _bundled_font(code)
        if bundled:
            _FONT_PATHS.setdefault(code, []).append(bundled)
            return bundled
    return None


def get_font(size, code=None):
    """当前（或指定）语言对应的字体，按语言缓存。"""
    code = code or current
    key = (size, code)
    font = _font_cache.get(key)
    if font is None:
        path = _font_path(code)
        font = pygame.font.Font(path, size) if path else pygame.font.Font(None, size)
        _font_cache[key] = font
    return font


def font_for(code, size):
    return get_font(size, code)


# CJK glyphs render at em size and look much larger than Latin; scale them down
CJK_SCALE = 0.62


def scale():
    return CJK_SCALE if current in _FONT_PATHS else 1.0


def set_lang(code):
    global current
    if code == "en" or code in STRINGS:
        current = code


def ui(key):
    """界面词条：当前语言 → 英文默认值 → key 本身"""
    return STRINGS.get(current, {}).get(key) or UI_EN.get(key, key)


def text(source):
    """关卡文字：按英文原文查当前语言，没有就原文"""
    return STRINGS.get(current, {}).get(source) or source


UI_EN["win_title"] = "YOU MADE IT"
UI_EN["win_hint"] = "This is the end. For now."

_WIN = {
    "zh": ("你成功了", "这就是终点。暂时。"),
    "ja": ("やったね", "ここが終点。今のところは。"),
    "ko": ("해냈어요", "여기가 끝. 지금은."),
    "ru": ("ТЫ ДОБРАЛСЯ", "Это конец. Пока что."),
    "de": ("GESCHAFFT", "Das ist das Ende. Vorerst."),
    "fr": ("TU L'AS FAIT", "C'est la fin. Pour l'instant."),
    "it": ("CE L'HAI FATTA", "È la fine. Per ora."),
    "es": ("LO LOGRASTE", "Este es el final. Por ahora."),
}
for _code, (_title, _hint) in _WIN.items():
    STRINGS[_code]["win_title"] = _title
    STRINGS[_code]["win_hint"] = _hint


UI_EN["summit_msg"] = "You reached the summit. Just a little further."
_SUMMIT_MSG = {
    "zh": "已经到达山顶了。就差最后一点了。",
    "ja": "山頂に着いた。あと少しだ。",
    "ko": "정상에 도착했어요. 조금만 더!",
    "ru": "Ты на вершине. Ещё немного.",
    "de": "Du bist oben. Nur noch ein Stück.",
    "fr": "Tu es au sommet. Encore un peu.",
    "it": "Sei in vetta. Ancora un po'.",
    "es": "Estás en la cima. Un poco más.",
}
for _code, _txt in _SUMMIT_MSG.items():
    STRINGS[_code]["summit_msg"] = _txt


UI_EN["saves"] = "Saves"
UI_EN["achievements"] = "Achievements"
UI_EN["back"] = "Back"
UI_EN["slot"] = "Slot"
UI_EN["empty"] = "empty"
UI_EN["height"] = "height"
_UI2 = {
    "zh": {"saves": "存档", "achievements": "成就", "back": "返回", "slot": "存档", "empty": "空", "height": "高度"},
    "ja": {"saves": "セーブ", "achievements": "実績", "back": "戻る", "slot": "スロット", "empty": "空き", "height": "高さ"},
    "ko": {"saves": "저장", "achievements": "업적", "back": "뒤로", "slot": "슬롯", "empty": "비어 있음", "height": "높이"},
    "ru": {"saves": "Сохранения", "achievements": "Достижения", "back": "Назад", "slot": "Слот", "empty": "пусто", "height": "высота"},
    "de": {"saves": "Speichern", "achievements": "Erfolge", "back": "Zurück", "slot": "Slot", "empty": "leer", "height": "Höhe"},
    "fr": {"saves": "Sauvegardes", "achievements": "Succès", "back": "Retour", "slot": "Emplacement", "empty": "vide", "height": "hauteur"},
    "it": {"saves": "Salvataggi", "achievements": "Obiettivi", "back": "Indietro", "slot": "Slot", "empty": "vuoto", "height": "altezza"},
    "es": {"saves": "Partidas", "achievements": "Logros", "back": "Volver", "slot": "Ranura", "empty": "vacío", "height": "altura"},
}
for _code, _kv in _UI2.items():
    STRINGS[_code].update(_kv)


UI_EN["ach_unlocked"] = "Achievement unlocked"
_ACH_UNLOCKED = {
    "zh": "成就解锁",
    "ja": "実績解除",
    "ko": "업적 달성",
    "ru": "Достижение получено",
    "de": "Erfolg freigeschaltet",
    "fr": "Succès débloqué",
    "it": "Obiettivo sbloccato",
    "es": "Logro desbloqueado",
}
for _code, _txt in _ACH_UNLOCKED.items():
    STRINGS[_code]["ach_unlocked"] = _txt


_TIPS = {
    "Long way up. If a gap looks too wide, throw a candy in mid-air to push yourself.": {
        "zh": "还有很长的路。如果间隙太宽，就在空中扔糖果借力推自己一把。",
        "ja": "まだまだ先は長い。隙間が広すぎたら、空中でキャンディを投げて押してもらおう。",
        "ko": "길이 멀어요. 간격이 너무 넓으면 공중에서 사탕을 던져 반동을 이용하세요.",
        "ru": "Ещё долго. Если промежуток слишком широк — брось конфету в воздухе, чтобы подтолкнуться.",
        "de": "Noch ein weiter Weg. Ist eine Lücke zu breit, wirf in der Luft eine Süßigkeit, um dich abzustoßen.",
        "fr": "Encore long. Si un écart est trop large, lance un bonbon en l'air pour te propulser.",
        "it": "Ancora lunga. Se il salto è troppo largo, lancia una caramella in aria per spingerti.",
        "es": "Aún queda. Si el hueco es muy ancho, lanza un caramelo en el aire para impulsarte.",
    },
    "Higher up the jumps get longer. One or two mid-air blasts will help.": {
        "zh": "越高跳得越远。空中来一两次糖果爆炸会帮你。",
        "ja": "高くなるほどジャンプは長くなる。空中で1〜2回キャンディを爆発させよう。",
        "ko": "높이 올라갈수록 점프가 길어져요. 공중에서 사탕을 한두 번 터뜨려 보세요.",
        "ru": "Выше прыжки длиннее. Помогут одна-две конфеты в воздухе.",
        "de": "Weiter oben werden die Sprünge länger. Ein oder zwei Explosionen in der Luft helfen.",
        "fr": "Plus haut, les sauts s'allongent. Une ou deux explosions en l'air aident.",
        "it": "Più in alto i salti si allungano. Una o due esplosioni in aria aiutano.",
        "es": "Más arriba los saltos son más largos. Una o dos explosiones en el aire ayudan.",
    },
    "Almost there. Jump from this upper-left ledge down onto the summit.": {
        "zh": "就差一点。从这个左上方的台子往下跳，落到山顶平台上。",
        "ja": "もうすぐ。この左上の足場から山頂へ飛び降りよう。",
        "ko": "거의 다 왔어요. 이 왼쪽 위 발판에서 정상으로 뛰어내리세요.",
        "ru": "Почти на месте. Прыгай с этого выступа слева сверху вниз на вершину.",
        "de": "Fast oben. Spring von dieser Kante links oben auf das Gipfelplateau.",
        "fr": "Presque là. Saute de ce rebord en haut à gauche sur le sommet.",
        "it": "Quasi arrivato. Salta da questa sporgenza in alto a sinistra sulla cima.",
        "es": "Casi. Salta desde esta cornisa arriba a la izquierda hasta la cima.",
    },
}
for _en, _tr in _TIPS.items():
    for _code, _txt in _tr.items():
        STRINGS[_code][_en] = _txt


_TIPS2 = {
    "No walking here: throw candies to move. Throw backward, slide forward.": {
        "zh": "这里没有左右走：靠扔糖果移动。往后扔，人往前滑。",
        "ja": "歩けません。キャンディを投げて動こう。後ろに投げると前に滑る。",
        "ko": "걷기 없음: 사탕을 던져 이동하세요. 뒤로 던지면 앞으로 미끄러집니다.",
        "ru": "Ходить нельзя: бросай конфеты. Брось назад — скользишь вперёд.",
        "de": "Kein Laufen: wirf Süßigkeiten. Nach hinten werfen, nach vorne rutschen.",
        "fr": "Pas de marche : lance des bonbons. Lance en arrière, glisse en avant.",
        "it": "Niente camminata: lancia caramelle. Lancia indietro e scivoli avanti.",
        "es": "No se camina: lanza caramelos. Lanza atrás y desliza adelante.",
    },
    "Wait for the moving platform, then hop on. It will carry you.": {
        "zh": "等移动平台靠过来再跳上去，它会载你走。",
        "ja": "動く足場が来るのを待って乗ろう。運んでくれる。",
        "ko": "움직이는 발판이 오면 올라타세요. 데려다 줍니다.",
        "ru": "Дождись движущейся платформы и запрыгни. Она тебя увезёт.",
        "de": "Warte auf die fahrende Plattform und spring drauf. Sie trägt dich.",
        "fr": "Attends la plateforme mobile et saute dessus. Elle t'emporte.",
        "it": "Aspetta la piattaforma mobile e salta su. Ti porta lei.",
        "es": "Espera la plataforma móvil y súbete. Ella te lleva.",
    },
    "Dropping down is fine. Just don't fall off the map.": {
        "zh": "往下跳没关系，别掉出地图就行。",
        "ja": "下に降りるのは平気。落ちすぎに注意。",
        "ko": "아래로 내려가는 건 괜찮아요. 떨어지지만 마세요.",
        "ru": "Падать вниз можно. Главное — не сорваться с карты.",
        "de": "Runterfallen ist okay. Nur nicht von der Karte fallen.",
        "fr": "Tomber en bas, ça va. Ne tombe pas hors de la carte.",
        "it": "Cadere giù va bene. Non cadere fuori dalla mappa.",
        "es": "Caer abajo está bien. No te caigas del mapa.",
    },
    "Zigzag stairs ahead. Keep the hops small.": {
        "zh": "前面是之字楼梯，小步往上跳。",
        "ja": "この先はジグザグ階段。小さく跳ぼう。",
        "ko": "앞에 지그재그 계단. 작게 뛰세요.",
        "ru": "Впереди зигзаг-лестница. Прыгай понемногу.",
        "de": "Zickzack-Treppe voraus. Kleine Sprünge.",
        "fr": "Escalier en zigzag. Petits sauts.",
        "it": "Scala a zigzag. Salti piccoli.",
        "es": "Escalera en zigzag. Saltos pequeños.",
    },
    "Ride the elevator up. Throw candies to adjust on the way.": {
        "zh": "坐电梯上去，途中扔糖果调整位置。",
        "ja": "エレベーターで上へ。途中でキャンディを投げて調整。",
        "ko": "엘리베이터를 타고 올라가세요. 가면서 사탕으로 조정.",
        "ru": "Поднимайся на лифте. По пути подправляйся конфетами.",
        "de": "Fahr mit dem Aufzug hoch. Unterwegs mit Süßigkeiten korrigieren.",
        "fr": "Monte avec l'ascenseur. Ajuste avec des bonbons en route.",
        "it": "Sali con l'ascensore. Aggiusta con le caramelle.",
        "es": "Sube con el ascensor. Ajusta con caramelos.",
    },
    "Narrow ledges now. Take it slow.": {
        "zh": "接下来是窄台，慢慢来。",
        "ja": "ここからは狭い足場。ゆっくり行こう。",
        "ko": "이제 좁은 발판. 천천히 가세요.",
        "ru": "Дальше узкие выступы. Не спеши.",
        "de": "Jetzt schmale Kanten. Langsam angehen.",
        "fr": "Passerelles étroites. Vas-y doucement.",
        "it": "Cenge strette. Vai piano.",
        "es": "Cornisas estrechas. Con calma.",
    },
    "Last stretch: follow the left edge up to the launch pad.": {
        "zh": "最后一程：沿着左边往上，到起跳台。",
        "ja": "ラスト。左端をたどってジャンプ台へ。",
        "ko": "마지막 구간: 왼쪽 끝을 따라 도약대로.",
        "ru": "Последний рывок: держись левого края до трамплина.",
        "de": "Letzter Abschnitt: am linken Rand zur Absprungplattform.",
        "fr": "Dernier tronçon : longe le bord gauche jusqu'au tremplin.",
        "it": "Ultimo tratto: segui il bordo sinistro fino al trampolino.",
        "es": "Último tramo: sigue el borde izquierdo hasta la plataforma.",
    },
}
for _en, _tr in _TIPS2.items():
    for _code, _txt in _tr.items():
        STRINGS[_code][_en] = _txt


UI_EN["cutscene_skip"] = "Click or press Space to continue"
UI_EN["intro_line1"] = "Every winter, Santa climbs the great mountain to bring presents to people."
UI_EN["intro_line2"] = "The only way up: throw candy, let the blast push you, and climb."
UI_EN["intro_line3"] = "Reach the little cabin on the summit. Presents first, rest later."
UI_EN["win_line1"] = "You made it. The presents are delivered."
UI_EN["win_line2"] = "Snow is already covering the path behind you."
UI_EN["win_line3"] = "Tomorrow, it's time to climb again."

_CUT = {
    "zh": {"cutscene_skip": "点击或按空格继续",
           "intro_line1": "每年冬天，圣诞老人都会爬上这座高山，把礼物送到人们手里。",
           "intro_line2": "上山的路只有一条：扔糖果，借爆炸的反冲，一点点往上爬。",
           "intro_line3": "山顶的小屋就是终点。先把礼物送到，再休息。",
           "win_line1": "你上来了。礼物送到了。",
           "win_line2": "雪很快盖住了来时的路。",
           "win_line3": "明天，再爬一次。"},
    "ja": {"cutscene_skip": "クリックまたはスペースで続行",
           "intro_line1": "毎年冬、サンタはこの大きな山を登って人々にプレゼントを届ける。",
           "intro_line2": "登る方法はひとつ：キャンディを投げ、爆風に押されて登る。",
           "intro_line3": "山頂の小さな小屋がゴール。まず配達、休憩はあとで。",
           "win_line1": "登れたね。プレゼントは届けた。",
           "win_line2": "雪が来た道をあっという間に隠していく。",
           "win_line3": "明日また、登ろう。"},
    "ko": {"cutscene_skip": "클릭 또는 스페이스로 계속",
           "intro_line1": "매년 겨울, 산타는 이 큰 산을 올라 사람들에게 선물을 전한다.",
           "intro_line2": "올라가는 방법은 하나: 사탕을 던지고 폭발 반동으로 밀려 올라간다.",
           "intro_line3": "정상의 작은 오두막이 결승점. 배달 먼저, 휴식은 나중에.",
           "win_line1": "올라왔구나. 선물은 전달됐다.",
           "win_line2": "눈이 방금 지나온 길을 덮고 있다.",
           "win_line3": "내일 다시 올라가자."},
    "ru": {"cutscene_skip": "Нажмите или пробел, чтобы продолжить",
           "intro_line1": "Каждую зиму Санта поднимается на эту гору, чтобы принести людям подарки.",
           "intro_line2": "Подняться можно только так: бросить конфету, толчок взрыва — и вверх.",
           "intro_line3": "Маленькая хижина на вершине — финиш. Сначала подарки, потом отдых.",
           "win_line1": "Ты поднялся. Подарки доставлены.",
           "win_line2": "Снег уже заметает пройденный путь.",
           "win_line3": "Завтра снова в гору."},
    "de": {"cutscene_skip": "Klicken oder Leertaste zum Fortfahren",
           "intro_line1": "Jeden Winter steigt der Weihnachtsmann auf diesen Berg, um Geschenke zu bringen.",
           "intro_line2": "Hinauf geht es nur so: Süßigkeit werfen, Explosion schiebt, klettern.",
           "intro_line3": "Die kleine Hütte auf dem Gipfel ist das Ziel. Erst Geschenke, dann Pause.",
           "win_line1": "Du hast es geschafft. Die Geschenke sind verteilt.",
           "win_line2": "Schnee bedeckt schon den Weg hinter dir.",
           "win_line3": "Morgen geht es wieder hinauf."},
    "fr": {"cutscene_skip": "Clique ou Espace pour continuer",
           "intro_line1": "Chaque hiver, le Père Noël grimpe cette grande montagne pour apporter des cadeaux.",
           "intro_line2": "Une seule façon de monter : lancer des bonbons, l'explosion te pousse, tu grimpes.",
           "intro_line3": "La petite cabane au sommet, c'est l'arrivée. Les cadeaux d'abord, le repos ensuite.",
           "win_line1": "Tu y es arrivé. Les cadeaux sont livrés.",
           "win_line2": "La neige recouvre déjà le chemin derrière toi.",
           "win_line3": "Demain, on remonte."},
    "it": {"cutscene_skip": "Clic o Spazio per continuare",
           "intro_line1": "Ogni inverno Babbo Natale scala questa grande montagna per portare regali.",
           "intro_line2": "Si sale in un modo solo: lancia caramelle, l'esplosione ti spinge, e sali.",
           "intro_line3": "La piccola baita in cima è il traguardo. Prima i regali, poi il riposo.",
           "win_line1": "Ce l'hai fatta. I regali sono consegnati.",
           "win_line2": "La neve sta già coprendo la strada dietro di te.",
           "win_line3": "Domani si risale."},
    "es": {"cutscene_skip": "Haz clic o pulsa Espacio para continuar",
           "intro_line1": "Cada invierno, Papá Noel sube esta gran montaña para llevar regalos a la gente.",
           "intro_line2": "Solo hay una forma de subir: lanzar caramelos, la explosión te empuja y escalas.",
           "intro_line3": "La cabaña en la cima es la meta. Primero los regalos, luego el descanso.",
           "win_line1": "Lo lograste. Los regalos están entregados.",
           "win_line2": "La nieve ya cubre el camino que dejaste atrás.",
           "win_line3": "Mañana, otra vez a subir."},
}
for _code, _d in _CUT.items():
    STRINGS.setdefault(_code, {}).update(_d)


UI_EN["skip"] = "Skip"
_SKIP = {"zh": "跳过", "ja": "スキップ", "ko": "건너뛰기", "ru": "Пропустить",
         "de": "Überspringen", "fr": "Passer", "it": "Salta", "es": "Saltar"}
for _code, _word in _SKIP.items():
    STRINGS.setdefault(_code, {})["skip"] = _word


_FINAL_HINT = "Gifts first: throw candy and slide over to the cabin!"
_FINAL = {
    "zh": "先把礼物送过去：扔糖果借反冲滑到小屋！",
    "ja": "まずプレゼントを届けよう：キャンディを投げて小屋まで滑ろう！",
    "ko": "선물부터 전하자: 사탕을 던져 오두막까지 미끄러져 가자!",
    "ru": "Сначала подарки: бросай конфеты и скользи к хижине!",
    "de": "Erst die Geschenke: wirf Süßigkeiten und rutsche zur Hütte!",
    "fr": "D'abord les cadeaux : lance des bonbons et glisse jusqu'à la cabane !",
    "it": "Prima i regali: lancia caramelle e scivola fino alla baita!",
    "es": "Primero los regalos: ¡lanza caramelos y deslízate hasta la cabaña!",
}
for _code, _txt in _FINAL.items():
    STRINGS.setdefault(_code, {})[_FINAL_HINT] = _txt


# Wind zone sign (level text: looked up by its English source string)
_WIND_SIGN = "Gusts ahead: throw against the wind!"
_WIND_SIGN_T = {
    "zh": "前方起风：朝反方向扔糖果借力！",
    "ja": "この先は強風：風と逆向きにキャンディを投げよう！",
    "ko": "앞쪽에 강풍: 바람 반대쪽으로 사탕을 던지세요!",
    "ru": "Впереди ветер: бросай конфеты против ветра!",
    "de": "Gegenwind: wirf die Süßigkeit gegen den Wind!",
    "fr": "Du vent : lance le bonbon contre le vent !",
    "it": "Vento forte: lancia la caramella controvento!",
    "es": "Viento fuerte: lanza el caramelo contra el viento!",
}
for _code, _txt in _WIND_SIGN_T.items():
    STRINGS[_code][_WIND_SIGN] = _txt


# Extra hint (throwing backwards brakes you)
_BRAKE_TIP = "Backward throw also brakes you. Throw the other way to slow down."
_BRAKE_T = {
    "zh": "反着扔也能刹车：想减速就往前进方向扔。",
    "ja": "逆向きに投げるとブレーキになる。減速したいときは進行方向へ投げよう。",
    "ko": "반대로 던지면 브레이크가 돼요. 속도를 줄이려면 나아가는 방향으로 던지세요.",
    "ru": "Бросок назад работает как тормоз: чтобы замедлиться, бросай в сторону движения.",
    "de": "Rückwärts werfen bremst: wirf in die Bewegungsrichtung, um langsamer zu werden.",
    "fr": "Lancer en arrière freine : lance dans le sens du mouvement pour ralentir.",
    "it": "Lanciare all'indietro frena: lancia nella direzione del movimento per rallentare.",
    "es": "Lanzar hacia atrás frena: lanza en la dirección del movimiento para frenar.",
}
for _code, _txt in _BRAKE_T.items():
    STRINGS[_code][_BRAKE_TIP] = _txt


# Delete-save confirmation dialog
UI_EN["delete_save_title"] = "Delete save slot {n}?"
UI_EN["delete_save_hint"] = "This cannot be undone."
UI_EN["delete"] = "Delete"
UI_EN["cancel"] = "Cancel"
_DELETE = {
    "zh": ("删除存档 {n}？", "此操作无法撤销。", "删除", "取消"),
    "ja": ("セーブ {n} を削除しますか？", "この操作は取り消せません。", "削除", "キャンセル"),
    "ko": ("저장 {n}을(를) 삭제할까요?", "이 작업은 되돌릴 수 없습니다.", "삭제", "취소"),
    "ru": ("Удалить сохранение {n}?", "Отменить это будет нельзя.", "Удалить", "Отмена"),
    "de": ("Spielstand {n} löschen?", "Das kann nicht rückgängig gemacht werden.", "Löschen", "Abbrechen"),
    "fr": ("Supprimer la sauvegarde {n} ?", "Cette action est irréversible.", "Supprimer", "Annuler"),
    "it": ("Eliminare il salvataggio {n}?", "Questa azione è irreversibile.", "Elimina", "Annulla"),
    "es": ("¿Borrar la partida {n}?", "Esta acción no se puede deshacer.", "Borrar", "Cancelar"),
}
for _code, (_t, _h, _d, _c) in _DELETE.items():
    STRINGS[_code]["delete_save_title"] = _t
    STRINGS[_code]["delete_save_hint"] = _h
    STRINGS[_code]["delete"] = _d
    STRINGS[_code]["cancel"] = _c


# Tutorial screen
UI_EN["tutorial"] = "Tutorial"
_TUT = {
    "zh": "教程",
    "ja": "チュートリアル",
    "ko": "튜토리얼",
    "ru": "Обучение",
    "de": "Tutorial",
    "fr": "Tutoriel",
    "it": "Tutoriale",
    "es": "Tutorial",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["tutorial"] = _txt

UI_EN["Aim and throw"] = "Aim and throw"
_TUT = {
    "zh": "瞄准与投掷",
    "ja": "ねらいと投げ",
    "ko": "조준과 던지기",
    "ru": "Прицел и бросок",
    "de": "Zielen und werfen",
    "fr": "Viser et lancer",
    "it": "Mira e lancio",
    "es": "Apunta y lanza",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["Aim and throw"] = _txt

UI_EN["Hold the left mouse button to aim. The dotted line shows where the candy flies and where it will land."] = "Hold the left mouse button to aim. The dotted line shows where the candy flies and where it will land."
_TUT = {
    "zh": "按住鼠标左键瞄准。虚线显示糖果会飞到哪里、落在哪里。",
    "ja": "左クリックを押したまま狙う。点線がキャンディの飛ぶ先と落ちる場所を示す。",
    "ko": "마우스 왼쪽 버튼을 누른 채 조준하세요. 점선이 사탕이 날아가 떨어질 위치를 보여줍니다.",
    "ru": "Держи левую кнопку мыши, чтобы прицелиться. Пунктир показывает, куда полетит конфета.",
    "de": "Linke Maustaste halten zum Zielen. Die Punktlinie zeigt, wohin die Süßigkeit fliegt.",
    "fr": "Maintiens le clic gauche pour viser. La ligne pointillée montre où le bonbon va voler.",
    "it": "Tieni premuto il tasto sinistro per mirare. La linea tratteggiata mostra dove vola la caramella.",
    "es": "Mantén el botón izquierdo para apuntar. La línea de puntos muestra dónde volará el caramelo.",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["Hold the left mouse button to aim. The dotted line shows where the candy flies and where it will land."] = _txt

UI_EN["Throw strength"] = "Throw strength"
_TUT = {
    "zh": "投掷力度",
    "ja": "投げる強さ",
    "ko": "던지는 힘",
    "ru": "Сила броска",
    "de": "Wurfstärke",
    "fr": "Force du lancer",
    "it": "Forza del lancio",
    "es": "Fuerza del lanzamiento",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["Throw strength"] = _txt

UI_EN["The bar under the character shows how strong this throw is. Aiming further away throws harder."] = "The bar under the character shows how strong this throw is. Aiming further away throws harder."
_TUT = {
    "zh": "角色下方的横条显示这一下的力度。鼠标离人越远，扔得越远。",
    "ja": "キャラの下のバーが投げの強さ。遠くを狙うほど強く飛ぶ。",
    "ko": "캐릭터 아래 막대가 이번 던지기의 힘을 보여줍니다. 멀리 조준할수록 세게 던집니다.",
    "ru": "Полоска под персонажем показывает силу броска. Чем дальше прицел, тем сильнее бросок.",
    "de": "Der Balken unter der Figur zeigt die Wurfstärke. Weiter zielen = stärker werfen.",
    "fr": "La barre sous le personnage montre la force du lancer. Viser plus loin = lancer plus fort.",
    "it": "La barra sotto il personaggio mostra la forza. Mira più lontano per lanciare più forte.",
    "es": "La barra bajo el personaje muestra la fuerza. Apuntar más lejos lanza más fuerte.",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["The bar under the character shows how strong this throw is. Aiming further away throws harder."] = _txt

UI_EN["Move with recoil"] = "Move with recoil"
_TUT = {
    "zh": "靠后坐力移动",
    "ja": "反動で動く",
    "ko": "반동으로 이동",
    "ru": "Движение отдачей",
    "de": "Bewegung per Rückstoß",
    "fr": "Bouger par recul",
    "it": "Muoversi col rinculo",
    "es": "Moverse con el retroceso",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["Move with recoil"] = _txt

UI_EN["There is no walk key. Throw backwards to slide forward, and throw at your feet to jump."] = "There is no walk key. Throw backwards to slide forward, and throw at your feet to jump."
_TUT = {
    "zh": "没有走键：往后扔往前滑，往脚下扔起跳。",
    "ja": "歩くキーはない。後ろに投げると前へ滑り、足元に投げるとジャンプする。",
    "ko": "걷기 키는 없습니다. 뒤로 던지면 앞으로 미끄러지고, 발밑에 던지면 점프합니다.",
    "ru": "Кнопки «идти» нет: бросай назад — скользишь вперёд, бросай под ноги — прыгаешь.",
    "de": "Es gibt keine Lauftaste: nach hinten werfen = vorwärts rutschen, nach unten werfen = springen.",
    "fr": "Pas de touche pour marcher : lance en arrière pour glisser en avant, lance à tes pieds pour sauter.",
    "it": "Non c'è un tasto per camminare: lancia indietro per scivolare avanti, lancia ai piedi per saltare.",
    "es": "No hay tecla para caminar: lanza hacia atrás para deslizarte, lanza a tus pies para saltar.",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["There is no walk key. Throw backwards to slide forward, and throw at your feet to jump."] = _txt

UI_EN["Climb progress"] = "Climb progress"
_TUT = {
    "zh": "攀爬进度",
    "ja": "登った高さ",
    "ko": "등반 진행도",
    "ru": "Прогресс восхождения",
    "de": "Aufstiegsfortschritt",
    "fr": "Progression",
    "it": "Progresso",
    "es": "Progreso",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["Climb progress"] = _txt

UI_EN["The Santa on the left edge shows how high you have climbed."] = "The Santa on the left edge shows how high you have climbed."
_TUT = {
    "zh": "左侧的圣诞老人显示你爬了多高。",
    "ja": "左端のサンタがどれだけ登ったかを示す。",
    "ko": "왼쪽의 산타가 얼마나 올라왔는지 보여줍니다.",
    "ru": "Санта слева показывает, как высоко ты поднялся.",
    "de": "Der Weihnachtsmann links zeigt, wie hoch du geklettert bist.",
    "fr": "Le Père Noël à gauche montre à quelle hauteur tu es.",
    "it": "Il Babbo Natale a sinistra mostra quanto sei salito.",
    "es": "El Santa de la izquierda muestra cuánto has subido.",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["The Santa on the left edge shows how high you have climbed."] = _txt

UI_EN["Find the pointer"] = "Find the pointer"
_TUT = {
    "zh": "唤出光标",
    "ja": "カーソルを出す",
    "ko": "커서 보기",
    "ru": "Показать курсор",
    "de": "Mauszeiger zeigen",
    "fr": "Afficher le curseur",
    "it": "Mostra il cursore",
    "es": "Mostrar el cursor",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["Find the pointer"] = _txt

UI_EN["There is no pointer while playing. Hold Alt to show the cursor again."] = "There is no pointer while playing. Hold Alt to show the cursor again."
_TUT = {
    "zh": "游玩时没有光标，按住 Alt 就会显示。",
    "ja": "プレイ中はカーソルがない。Alt を押すと表示される。",
    "ko": "플레이 중에는 커서가 없습니다. Alt를 누르면 다시 표시됩니다.",
    "ru": "Во время игры курсора нет. Зажми Alt, чтобы показать его.",
    "de": "Im Spiel gibt es keinen Zeiger. Halte Alt, um ihn zu zeigen.",
    "fr": "Pas de curseur pendant le jeu. Maintiens Alt pour le montrer.",
    "it": "Durante il gioco non c'è cursore. Tieni Alt per mostrarlo.",
    "es": "No hay cursor mientras juegas. Mantén Alt para mostrarlo.",
}
for _code, _txt in _TUT.items():
    STRINGS[_code]["There is no pointer while playing. Hold Alt to show the cursor again."] = _txt


# Achievements hidden tab
UI_EN["hidden"] = "Hidden"
_HIDDEN_TAB = {
    "zh": "隐藏", "ja": "隠し", "ko": "숨김", "ru": "Скрытые",
    "de": "Versteckt", "fr": "Cachés", "it": "Nascosti", "es": "Ocultos",
}
for _code, _txt in _HIDDEN_TAB.items():
    STRINGS[_code]["hidden"] = _txt


# Achievement completed label (hidden achievements have one level)
UI_EN["completed"] = "Completed"
_COMPLETED = {
    "zh": "已完成", "ja": "達成", "ko": "완료", "ru": "Выполнено",
    "de": "Erreicht", "fr": "Terminé", "it": "Completato", "es": "Completado",
}
for _code, _txt in _COMPLETED.items():
    STRINGS[_code]["completed"] = _txt


# Shown for 5 s when the player falls at the same spot again and again
UI_EN["fall_tip"] = ("This spot keeps beating you. Brake before the jump, "
                     "then leap.")
_FALL_TIP = {
    "zh": "这里你已经掉下去好几次了：起跳前先反扔刹车，再跳。",
    "ja": "ここで何度も落ちている。跳ぶ前に逆向きに投げてブレーキをかけよう。",
    "ko": "여기서 여러 번 떨어졌어요. 뛰기 전에 반대로 던져 브레이크를 걸어 보세요.",
    "ru": "Ты уже падал здесь несколько раз. Затормози броском назад, потом прыгай.",
    "de": "Hier bist du schon oft gefallen. Bremse vor dem Sprung mit einem Rückwurf.",
    "fr": "Tu es déjà tombé plusieurs fois ici. Freine avant de sauter.",
    "it": "Sei già caduto qui più volte. Frena prima del salto.",
    "es": "Ya has caído varias veces aquí. Frena antes de saltar.",
}
for _code, _txt in _FALL_TIP.items():
    STRINGS[_code]["fall_tip"] = _txt


# Menu title: every language keeps its own deliberate typo flavour, like
# "SLIPERY" instead of "SLIPPERY" in English.
UI_EN["game_title"] = "A SLIPERY CLIMB"
_GAME_TITLE = {
    "zh": "一次滑留的攀登",
    "ja": "スリピー・クライム",
    "ko": "미끌어운 등반",
    "ru": "Скользкое восхождние",
    "de": "Ein rutschigerr Aufstieg",
    "fr": "Une ascencion glissante",
    "it": "Una salita scivoloza",
    "es": "Una escalada resbaladisa",
}
for _code, _txt in _GAME_TITLE.items():
    STRINGS[_code]["game_title"] = _txt


# Extra lines for the longer victory cutscene
UI_EN["win_line4"] = "Every metre was worth it."
UI_EN["win_line5"] = "See you next winter."
UI_EN["win_recap"] = "Highest point: {m} m"
_WIN_EXTRA = {
    "zh": ("每一米都值得。", "明年冬天再见。", "最高点：{m} 米"),
    "ja": ("どの一歩も無駄じゃなかった。", "また来年の冬に。", "最高到達点：{m} m"),
    "ko": ("모든 1미터가 값졌어요.", "내년 겨울에 만나요.", "최고 지점: {m} m"),
    "ru": ("Каждый метр был не зря.", "До следующей зимы.", "Высшая точка: {m} м"),
    "de": ("Jeder Meter hat sich gelohnt.", "Bis zum nächsten Winter.",
           "Höchster Punkt: {m} m"),
    "fr": ("Chaque mètre en valait la peine.", "À l'hiver prochain.",
           "Point le plus haut : {m} m"),
    "it": ("Ogni metro è valso la pena.", "Al prossimo inverno.",
           "Punto più alto: {m} m"),
    "es": ("Cada metro valió la pena.", "Hasta el próximo invierno.",
           "Punto más alto: {m} m"),
}
for _code, (_l4, _l5, _recap) in _WIN_EXTRA.items():
    STRINGS[_code]["win_line4"] = _l4
    STRINGS[_code]["win_line5"] = _l5
    STRINGS[_code]["win_recap"] = _recap
