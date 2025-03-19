# -*- coding: utf-8 -*-
#时间复杂度O(1)
def calculate_money(distance):
    if distance==0:
        return 0
    elif distance<=6000:
        return 3
    elif distance<=12000:
        return 4
    elif distance<=22000:
        return 5
    elif distance<=32000:
        return 6
    else:
        return int((distance-32000)/20000)+7
    