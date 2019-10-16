from core.constants import BASE_DIPLOMAT_COST


def maximum_diplomats_to_buy(gold, current):
    gk = gold / BASE_DIPLOMAT_COST
    n = 0
    while True:
        if current * n + (n ** 2 + n) / 2 <= gk:
            n += 1
        else:
            n -= 1
            return n
