#! /usr/bin/env python3
#
#  Copyright (C) 2004  Matthieu Bec.
#
#  This file is part of python-nc2480.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  python-nc2480 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__version__ = '0.2.3'

import curses
from curses import wrapper
import curses.panel
import time

debug = False # trace mouse event, show separators

# for f in `ls /lib/kbd/consolefonts`; do echo $f; setfont $f ; sleep 0.2; done

class colortable:
    # overriden by init color
    green_on_black  = curses.A_NORMAL
    yellow_on_black = curses.A_NORMAL
    red_on_black    = curses.A_NORMAL
    white_on_black  = curses.A_NORMAL


class style:
    OK   = curses.A_NORMAL | colortable.green_on_black
    NTC  = curses.A_BOLD   | colortable.green_on_black
    WRN  = curses.A_BOLD   | colortable.yellow_on_black
    ERR  = curses.A_BOLD   | colortable.red_on_black
    WSD  = curses.A_BLINK  | colortable.white_on_black


class text_widget:
    def __init__(self, parent, lstart, cstart, cspan, text=None, justify='ljust', **kwd):
        self.cspan = cspan
        self.text = text
        self.justify = justify
        # +1 for cursor after insertion of the last character (doh..)
        self.win = parent.win.derwin(1, cspan + 1, lstart, cstart)
        self.win.leaveok(True)
        #self.win.scrollok(False)
        if text:
            text_insert = {'rjust': text.rjust, 'ljust': text.ljust}[justify]
            self.win.addnstr(0, 0, text_insert(self.cspan), self.cspan, curses.A_NORMAL)

    def set_text(self, text, justify=None, style=curses.A_NORMAL):
        if not justify: justify = self.justify
        text_insert = {'rjust': text.rjust, 'ljust': text.ljust}[justify]
        # clear methods clears the extra +1 cursor character
        # we don't want that and format the text to fit exactly
        #self.win.clear()
        #self.win.erase()
        #self.win.clrtoeol()
        #self.win.deleteln()
        self.win.addnstr(0, 0, text_insert(self.cspan), self.cspan, style)
        #XXX#self.win.refresh()
        self.win.syncup() # XXX YEAH! XXX
        curses.panel.update_panels()
        curses.doupdate()

    def set_char_attrs(self, char_attrs):
        c,a = char_attrs
        for i, cc in enumerate(c):
            self.win.addch(0, i, cc, a[i]) # XXX attr
        self.win.syncup()
        curses.panel.update_panels()
        curses.doupdate()

class hb_widget:
    def __init__(self, title, parent, lstart, cstart):
        if title: tcols = len(title) + 1
        else: tcols = 0
        pane = parent.subpanel(1, 3 + tcols, lstart, cstart)
        pane.win.clear()
        self._style = style.OK
        if title: pane.win.addstr(0, 3, title, self._style)
        self.widget = text_widget(pane, 0, 1, 1)
        self.widget.win.addch(0, 0, curses.ACS_DIAMOND, self._style)
        self.pane = pane
        self.title = title
        self._beat = 0

    def pulse(self):
        if self._beat: marker = curses.ACS_DIAMOND
        else: marker = curses.ACS_BULLET # ' '
        self.widget.win.addch(0, 0, marker, self._style)
        self._beat = not self._beat
        self.pane.win.syncup()
        curses.panel.update_panels()
        curses.doupdate()

    def valid(self, state):
        if state: self._style = style.OK
        else: self._style = style.ERR
        if self.title: self.pane.win.addstr(0, 3, self.title, self._style)
        self.pane.win.syncup()
        curses.panel.update_panels()
        curses.doupdate()


class popup_widget:
    def __init__(self, text):
        lines = text.split('\n')
        cols = 0
        for l in lines:
            if len(l) > cols: cols = len(l)
        popwin = curses.newwin(len(lines) + 2, cols + 4, 24 // 2 - len(lines) // 2 - 2, 80 // 2 - cols // 2 - 2)
        popwin.border()
        for i, l in enumerate(lines):
            popwin.addstr(i + 1, 2, l)
        self.panel = curses.panel.new_panel(popwin)
        self.hide()

    def hide(self, *args, **kwds):
        self.panel.hide()
        curses.panel.update_panels()
        curses.doupdate()

    def show(self, *args, **kwds):
        self.panel.top()
        self.panel.show()
        curses.panel.update_panels()
        curses.doupdate()

    def pop(self, topwin):
        self.show()
        topwin.hookAdd(1.0, self.hide)


class pane:
    def __init__(self, pwin, lspan, cspan, lstart, cstart, title=None, boxed=True, **kwd):
        self.win = pwin.derwin(lspan, cspan, lstart, cstart)
        self.boxed = boxed
        title_attr = curses.A_NORMAL
        if 'bold' in kwd:       title_attr |= curses.A_BOLD
        if 'blink' in kwd:      title_attr |= curses.A_BLINK
        if 'reverse' in kwd:    title_attr |= curses.A_REVERSE
        if 'standout' in kwd:   title_attr |= curses.A_STANDOUT
        if 'underline' in kwd:  title_attr |= curses.A_UNDERLINE
        if boxed: self.win.box()
        if title: self.win.addstr(0, 2, f' {title} ', title_attr)
        self.coords = lspan, cspan, lstart, cstart

    def subpanel(self, lspan, cspan, lstart, cstart, title=None, boxed=False, **kwd):
        return pane(self.win, lspan, cspan, lstart, cstart, title, boxed, **kwd)

    def titled_entry(self, row, title, justify='rjust'):
        if self.boxed: offset = 2
        else: offset = 1
        lent = len(title)
        lspan, cspan, lstart, cstart = self.coords
        if lent: text_widget(self, row, offset, lent, text=title)
        else: lent=-1
        return text_widget(self, row, lent + offset + 1, cspan - 2 * offset - 1 - lent, justify=justify)

    def settitle(self, title, _style=None):
        if _style is None: _style=style.OK # colortable fully initialized during __init__
        if self.boxed:
            self.win.bkgdset(' ', _style)
            self.win.box()
        self.win.addstr(0, 2, f' {title} ', _style)
        #XXX#self.win.refresh()
        self.win.syncup() # XXX YEAH! XXX
        curses.panel.update_panels()
        curses.doupdate()


class page2480:
    def __init__(self, border=False):
        self.win = curses.newwin(top2480.num_lines, top2480.num_columns, 0, 0)
        self.panel = curses.panel.new_panel(self.win)
        if border: self.win.border()
        if debug: self.win.bkgdset('_', colortable.green_on_black)
        else:     self.win.bkgdset(' ', colortable.green_on_black)

    def subpanel(self, lspan, cspan, lstart, cstart, title=None, boxed=True, **kwd):
        return pane(self.win, lspan, cspan, lstart, cstart, title, boxed, **kwd)


class top2480:
    num_lines = 24
    num_columns = 80

    def __init__(self, scrn, title=None, callback=None, poll10th=10, help_string=None, on_quit=None):
        # TODO curses.has_colors(), curses.can_change_color()
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN,   curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW,  curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED,     curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_WHITE,   curses.COLOR_BLACK)
            colortable.green_on_black   = curses.color_pair(1)
            colortable.yellow_on_black  = curses.color_pair(2)
            colortable.red_on_black     = curses.color_pair(3)
            colortable.white_on_black   = curses.color_pair(4)
            style.OK   = colortable.green_on_black
            style.NTC  = colortable.green_on_black  | curses.A_BOLD
            style.WRN  = colortable.yellow_on_black | curses.A_BOLD  # | curses.A_REVERSE | curses.A_BLINK
            style.ERR  = colortable.red_on_black    | curses.A_BOLD
            style.WSD  = colortable.white_on_black  | curses.A_BLINK
        except Exception as e:
            pass

        # setup top window
        curses.noecho()
        if callback is None:
            curses.cbreak()
        else:
            curses.halfdelay(poll10th) # 10-th of seconds
        self.callback = callback

        try: curses.curs_set(0) # mac i-terms
        except BaseException: pass

        self.scrn = scrn
        self.pages = []
        self.current_page = -1

        if title: self.xtitle(title)

        self.key_callback_registry = {}
        self.mouse_callback_registry = []
        self.hook_callback_registry = []
        self.running = True
        self.help_string = help_string
        self.on_quit = on_quit
        self.keyAdd('q', self.quit)
        self.keyAdd(curses.KEY_LEFT, self.show_prev)
        self.keyAdd(curses.KEY_RIGHT, self.show_next)

        # one line footer window
        self.footer_win = curses.newwin(1, top2480.num_columns, top2480.num_lines - 1, 0)
        self.footer_pan = curses.panel.new_panel(self.footer_win)

        #
        self.fun = popup_widget('INSERT  COINS' + '\n' +
                                ' TO CONTINUE ')
        self.keyAdd('p', self.popfun)

        if debug: self.mouseAdd(self.trace_mouse_evt)

    def xtitle(self, title):
        print(f'\033]0;{title}\007') # icon + window
        #print(f'\033]1;{title}\007') # icon
        #print(f'\033]2;{title}\007') # window

    def add_page(self, border=False):
        p = page2480(border=border)
        self.pages.append(p)
        return p

    def clear_footer(self, *arg, **kwd):
        self.footer_pan.hide()
        curses.panel.update_panels()
        curses.doupdate()

    def proc_one(self):
        k = self.scrn.getch()
        if k == -1:
            if self.callback: self.callback()
            tnow = time.time()
            hcr = []
            for tstart, fun, arg, kwd in self.hook_callback_registry:
                if tnow > tstart:
                    fun(self, *arg, **kwd)
                else:
                    hcr.append((tstart, fun, arg, kwd))
            self.hook_callback_registry = hcr
        else:
            if k == curses.KEY_MOUSE:
                m_evt = curses.getmouse()
                for fun, arg, kwd in self.mouse_callback_registry:
                    fun(self, m_evt, *arg, **kwd)
            elif k in self.key_callback_registry:
                fun, arg, kwd = self.key_callback_registry[k]
                fun(self, k, *arg, **kwd)
            else:
                if not self.help_string:
                    self.help_string = ', '.join([curses.keyname(k).decode() for k in self.key_callback_registry.keys()])
                #self.print_footer(curses.unctrl(k)+self.help_string)
                self.print_footer(f"Key \"{curses.keyname(k).decode()}\" invalid: {self.help_string}")

    def mainloop(self):
        # realize UI
        self.footer_pan.top()
        self.footer_pan.hide()
        curses.panel.update_panels()
        curses.doupdate()

        try:
            # show page 0
            self.current_page = 1
            self.show_prev(None, None)
        except Exception as e:
            #pass
            raise SystemError(str(e))

        while self.running:
            self.proc_one()

        if self.on_quit:
            self.on_quit()

    def keyAdd(self, k, cb_func, *cb_args, **cb_kwd):
        if isinstance(k, str): # chr in reality
            self.key_callback_registry[ord(k)] = (cb_func, cb_args, cb_kwd)
        else:
            self.key_callback_registry[k] = (cb_func, cb_args, cb_kwd)

    def mouseAdd(self, cb_func, *cb_args, **cb_kwd):
        self.mouse_callback_registry.append((cb_func, cb_args, cb_kwd))
        curses.mousemask(curses.ALL_MOUSE_EVENTS) # BUTTON1_CLICKED

    def hookAdd(self, timeout, cb_func, *cb_args, **cb_kwd):
        self.hook_callback_registry.append((time.time() + timeout, cb_func, cb_args, cb_kwd))

    def quit(self, win, key, *args, **kwd):
        self.running = False

    def popfun(self, win, key, *args, **kwd):
        self.fun.pop(topwin=self)

    def show_next(self, win, key, *args, **kwd):
        if len(self.pages)<2: return
        if self.current_page + 1 < len(self.pages):
            self.pages[self.current_page].panel.hide()
            self.current_page += 1
            self.pages[self.current_page].panel.show()
            curses.panel.update_panels()
            curses.doupdate()
            #self.print_footer('show'+str(self.current_page)+str(pages[self.current_page]))
        else:
            #already on last
            pass

    def show_prev(self, win, key, *args, **kwd):
        if len(self.pages)<2: return
        if self.current_page > 0:
            self.pages[self.current_page].panel.hide()
            self.current_page -= 1
            self.pages[self.current_page].panel.show()
            curses.panel.update_panels()
            curses.doupdate()
            #self.print_footer('show'+str(self.current_page)+str(pages[self.current_page]))
        else:
            #already on first
            pass

    def trace_mouse_evt(self, win, evt, *args, **kwd):
        eid, x, y, z, bstate = evt
        self.print_footer(f'l: {y} c: {x}', 1)

    def print_footer(self, msg, timeout=1):
        self.footer_win.clear()
        self.footer_win.addnstr(0, 0, msg, top2480.num_columns - 1)
        self.footer_win.refresh()
        self.footer_pan.show()
        curses.panel.update_panels()
        self.hookAdd(1.0, self.clear_footer)


def run(app, *arg, **kwd):
    try:
        wrapper(app, *arg, **kwd)
    finally:
        try: curses.endwin()
        except: pass
