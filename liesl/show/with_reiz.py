# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 15:48:36 2019

@author: Robert Guggenberger
"""

import reiz
# %%
canvas = reiz.Canvas()
canvas.open()
# %%

backbar = reiz.visual.Bar(height=1, width=0.2)
import random
while True:
    frontbar = reiz.visual.Bar(height=random.random(), width=0.19, color='red')
    cue = reiz.Cue(visualstim=[backbar, frontbar])
    cue.show(canvas)
    reiz.clock.sleep(0.1)