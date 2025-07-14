import curses

def main(stdscr):
    # 設定
    curses.curs_set(0)  # カーソル非表示
    stdscr.keypad(True)
    stdscr.addstr("これは上部の出力です（残る）\n")
    stdscr.addstr("↓キーで選んでEnterで決定\n")
    stdscr.refresh()

    options = ["リンゴ", "バナナ", "みかん", "ぶどう"]
    selected = 0

    # サブウィンドウを作成（高さ: 選択肢数 + α, 幅: 40, 位置: y=3, x=0）
    menu_win = curses.newwin(len(options) + 2, 40, 3, 0)

    while True:
        # メニュー表示
        menu_win.clear()
        menu_win.box()  # 枠をつける
        for i, option in enumerate(options):
            prefix = "→ " if i == selected else "   "
            menu_win.addstr(i + 1, 1, f"{prefix}{option}")
        menu_win.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in [curses.KEY_ENTER, 10, 13]:
            break  # Enterで決定

    # 決定結果をターミナル下部に表示
    stdscr.addstr(8, 0, f"選ばれたのは: {options[selected]}\n")
    stdscr.refresh()
    stdscr.getch()

    stdscr.clear()
    curses.endwin()
    print("選択完了！この出力はターミナルに残ります")




    # ↓終了時にcursesの画面をクリアして、元に戻す

    # ↓普通のprintで出力（ログとして残る）


curses.wrapper(main)
