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

class style:
    def __init__(self, flat_fonts = False):
        if flat_fonts:
            self.v_blocks = [chr(0xe000 + i) for i in range(15)] # Basic Multilingual Plane, Private Use Area
            self.v_block_empty = ' '
            self.v_block_sep = ' '
        else:
            self.v_blocks = [chr(0x2581 + i) for i in range(8)]
            self.v_blocks.insert(0, chr(0x20)) # ' '
            self.v_block_empty = self.v_blocks[0]
            self.v_block_sep = self.v_blocks[-1]

        self.v_blocks_len = len(self.v_blocks)

        self.h_blocks = [chr(0x258F - i) for i in range(8)]
        self.h_blocks.insert(0, chr(0x20))
        self.h_blocks_len = len(self.h_blocks)

block_style=style(False)
flat_style=style(True)

def h_pct(pct, nchar=1, sep=False, style=block_style):
    if sep: fullblock = style.h_blocks[-2]
    else: fullblock = style.h_blocks[-1]
    blocks100 = nchar * style.h_blocks_len
    blocksval = int(blocks100 * pct)
    full = int(blocksval / style.h_blocks_len)
    frac = int(blocks100 * pct - style.v_blocks_len * full)
    if frac == 0 and full > 0:
        ret = (full - 1) * fullblock + style.h_blocks[-1] + style.h_blocks[frac]
    else:
        ret = full * fullblock + style.h_blocks[frac]
    return ret


def v_pct(pct, nchar=1, sep=False, style=block_style):
    if sep: fullblock = style.v_blocks[-2]
    else: fullblock = style.v_blocks[-1]
    blocks100 = nchar * style.v_blocks_len
    blocksval = int(blocks100 * pct)
    full = int(blocksval / style.v_blocks_len)
    frac = int(blocks100 * pct - style.v_blocks_len * full)
    if frac == 0 and full > 0:
        ret = (full - 1) * fullblock + style.v_blocks[-1] + style.v_blocks[frac]
    else:
        ret = full * fullblock + style.h_blocks[frac]
    return ret

# histogram plot
class stripgraph:
    def __init__(self, lspan=1, cspan=80, vmin=0.0, vmax=100.0, style=block_style):
        self.min = vmin
        self.max = vmax
        self.lspan = lspan
        self.cspan = cspan
        self.bbits = len(style.v_blocks)  # bits total
        self.nbits = lspan * self.bbits   # bits per line
        self.czero = [style.v_block_empty for i in range(lspan)]
        self.style = style

        self.data = [[style.v_block_empty for i in range(cspan)] for i in range(lspan)]

    def pct_repr(self, pct): # 0<pct<1
        if pct>=1.0: pct=0.9999 # XXX
        elif pct<0.0: pct=0.0
        nbits = int(pct * self.nbits)
        bbits = nbits % self.bbits
        blks = (nbits - bbits) // self.bbits
        rep = self.czero[:]
        for i in range(blks):
            rep[i] = self.style.v_block_sep
        if blks < self.lspan: rep[blks] = self.style.v_blocks[bbits]
        rep.reverse()
        return rep

    def data_repr(self, v):
        if v > self.max: v = self.max
        elif v < self.min: v = self.min
        data = self.pct_repr(v / (self.max - self.min))
        return data

    def push_data(self, v):
        d = self.data_repr(v)
        for l in range(self.lspan):
            self.data[l].pop(0)
            self.data[l].append(d[l])

    def printval(self, v):
        for l in self.data_repr(v): print(l)

    def print(self):
        for l in range(self.lspan):
            print(''.join(self.data[l]))

    def line_data(self):
        d = []
        for l in range(self.lspan):
            d.append(''.join(self.data[l]))
        return d


if __name__ == '__main__':
    for c in block_style.v_blocks: print(c, end='')
    print(len(block_style.v_blocks))
    for c in block_style.h_blocks: print(c)
    print(len(block_style.h_blocks))
    for p in range(101):
        print(h_pct(p / 100., 100))
    for p in range(101):
        print(f'{h_pct(p / 100., 10, sep=True):<12s} {p:3d} %')
    for p in range(101):
        print(f'{h_pct(p / 100., 90, sep=False)} {p} %')
    # no easy way to display v_pct
