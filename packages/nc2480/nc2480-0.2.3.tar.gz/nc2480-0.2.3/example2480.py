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

import nc2480
from nc2480 import vu
import time
from math import sin, pi

#nc2480.debug = True # trace mouse event and empty space

style = vu.flat_style
#style = vu.block_style

class demo(nc2480.top2480):

    def __init__(self, scrn, *args, **kwd):
        super().__init__(scrn, title='nc2480 demo', callback = self.update, poll10th=1)

        self.counter = 0
        self.pldata = 0

        #---
        p0                  = self.add_page()
        plotbox             = p0.subpanel(24, 60, 0, 0, title='BOX', boxed=True)
        self.strip_lspan    = 22
        self.w_strip        = [plotbox.titled_entry(1+i, '', justify='rjust') for i in range(self.strip_lspan)]
        self.strip          = vu.stripgraph(lspan=self.strip_lspan, cspan=58, style=style)


        healthbox           = p0.subpanel(19, 20, 0, 60, boxed=True)
        self.healthwdg      = nc2480.hb_widget('Health', healthbox, 0, 2)
        self.w_slvhb        = healthbox.titled_entry(2, 'counter')
        self.w_force_minmax = healthbox.titled_entry(4, 'toggle')
        self.w_force_step   = healthbox.titled_entry(5, 'bool')
        self.w_follow_error = healthbox.titled_entry(6, 'flag_0')
        self.w_calibrated   = healthbox.titled_entry(7, 'flag_1')
        self.w_masterhb     = healthbox.titled_entry(8, 'hb')
        self.w_io           = healthbox.titled_entry(9, 'cn')
        self.w_hk           = healthbox.titled_entry(10, 'dz')
        self.w_enable       = healthbox.titled_entry(12, 'val')
        self.w_close_loop   = healthbox.titled_entry(13, 'perf')
        self.cv_pwr_en_     = healthbox.titled_entry(15, 'ena*')
        self.drv_sv         = healthbox.titled_entry(16, 'drv')

        statsbox            = p0.subpanel(5, 20, 19, 60, title='Stats', boxed=False)
        self.w_kbs          = statsbox.titled_entry(1, 'kB/s')
        self.w_fps          = statsbox.titled_entry(2, 'fps')
        self.w_bads         = statsbox.titled_entry(3, 'bfs')

        #---
        p1                  = self.add_page()
        exebox              = p1.subpanel(24, 80, 0, 0, boxed=True, title='Exec')
        self.localtime      = exebox.titled_entry(2, 'localtime:')
        self.txt1           = exebox.titled_entry(3, 'pdo:', justify='ljust')

        #---
        p2 = self.add_page()
        aboutbox = p2.subpanel(24, 80, 0, 0, boxed=True, title='About')
        about = aboutbox.titled_entry(2, 'Author:')
        about.set_text('Matthieu Bec <mdcb808@gmail.com>', justify='ljust')

    def update(self):
        self.pldata+=0.1
        pdata = (sin(self.pldata)+1)*50
        self.strip.push_data(pdata)
        ldata = self.strip.line_data()
        for i in range(self.strip_lspan): self.w_strip[i].set_text(ldata[i])

        self.localtime.set_text(time.strftime('%F %H:%M:%S', time.localtime()))
        #
        self.healthwdg.valid(True)
        self.counter += 1
        if self.counter > 10:
            self.healthwdg.pulse()
            self.counter = 1
        self.w_slvhb.set_text(str(self.counter))

        def styled_bool(w, v, test):
            if v != test: w.set_text(str(v), style = nc2480.style.ERR)
            else: w.set_text(str(v))

        styled_bool(self.w_force_minmax, self.counter % 2, 0)
        self.w_force_step.set_text('1')
        self.w_follow_error.set_text('1')
        self.w_calibrated.set_text('1')
        self.w_masterhb.set_text('1')
        self.w_io.set_text('1')
        self.w_hk.set_text('1')

        self.w_enable.set_text(f'{pdata:.03f}')
        self.w_close_loop.set_text('1')

        self.cv_pwr_en_.set_text('1')
        self.drv_sv.set_text('1')

        self.w_kbs.set_text('170.6')
        self.w_fps.set_text('40.1')
        self.w_bads.set_text('10')

        self.txt1.set_text('bunch of text')


def main(scr, *args, **kw):
    w = demo(scr, *args, **kw)
    w.mainloop()


if __name__ == '__main__':
    nc2480.run(main)
