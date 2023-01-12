# Initial Setup:
# Import all the libraries we need

import matplotlib.pyplot as plt
import numpy as np
import csv
import math
import random

from BSE import market_session

# The next are helper functions that you will use later, if they don't make
# much sense now, don't worry too much about it they will become clearer later:


# Use this to plot trades of a single experiment
def plot_trades(trial_id):
    prices_fname = trial_id + '_tape.csv'
    x = np.empty(0)
    y = np.empty(0)
    with open(prices_fname, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            time = float(row[1])
            price = float(row[2])
            x = np.append(x, time)
            y = np.append(y, price)

    plt.plot(x, y, 'x', color='black')


# Use this to run an experiment n times and plot all trades
def n_runs_plot_trades(n, trial_id, start_time, end_time, traders_spec,
                       order_sched):
    x = np.empty(0)
    y = np.empty(0)

    for i in range(n):
        trialId = trial_id + '_' + str(i)
        tdump = open(trialId + '_avg_balance.csv', 'w')

        market_session(trialId, start_time, end_time, traders_spec,
                       order_sched, tdump, True, False)

        tdump.close()

        with open(trialId + '_tape.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                time = float(row[1])
                price = float(row[2])
                x = np.append(x, time)
                y = np.append(y, price)

    plt.plot(x, y, 'x', color='black')


# !!! Don't use on it's own
def getorderprice(i, sched, n, mode):
    pmin = min(sched[0][0], sched[0][1])
    pmax = max(sched[0][0], sched[0][1])
    prange = pmax - pmin
    stepsize = prange / (n - 1)
    halfstep = round(stepsize / 2.0)

    if mode == 'fixed':
        orderprice = pmin + int(i * stepsize)
    elif mode == 'jittered':
        orderprice = pmin + int(i * stepsize) + random.randint(
            -halfstep, halfstep)
    elif mode == 'random':
        if len(sched) > 1:
            # more than one schedule: choose one equiprobably
            s = random.randint(0, len(sched) - 1)
            pmin = min(sched[s][0], sched[s][1])
            pmax = max(sched[s][0], sched[s][1])
        orderprice = random.randint(pmin, pmax)
    return orderprice


# !!! Don't use on it's own
def make_supply_demand_plot(bids, asks):
    # total volume up to current order
    volS = 0
    volB = 0

    fig, ax = plt.subplots()
    plt.ylabel('Price')
    plt.xlabel('Quantity')

    pr = 0
    for b in bids:
        if pr != 0:
            # vertical line
            ax.plot([volB, volB], [pr, b], 'r-')
        # horizontal lines
        line, = ax.plot([volB, volB + 1], [b, b], 'r-')
        volB += 1
        pr = b
    if bids:
        line.set_label('Demand')

    pr = 0
    for s in asks:
        if pr != 0:
            # vertical line
            ax.plot([volS, volS], [pr, s], 'b-')
        # horizontal lines
        line, = ax.plot([volS, volS + 1], [s, s], 'b-')
        volS += 1
        pr = s
    if asks:
        line.set_label('Supply')

    if bids or asks:
        plt.legend()
    plt.show()


# Use this to plot supply and demand curves from supply and demand ranges and stepmode
def plot_sup_dem(seller_num, sup_ranges, buyer_num, dem_ranges, stepmode):
    asks = []
    for s in range(seller_num):
        asks.append(getorderprice(s, sup_ranges, seller_num, stepmode))
    asks.sort()
    bids = []
    for b in range(buyer_num):
        bids.append(getorderprice(b, dem_ranges, buyer_num, stepmode))
    bids.sort()
    bids.reverse()

    make_supply_demand_plot(bids, asks)


# plot sorted trades, useful is some situations - won't be used in this worksheet
def in_order_plot(trial_id):
    prices_fname = trial_id + '_tape.csv'
    y = np.empty(0)
    with open(prices_fname, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            price = float(row[2])
            y = np.append(y, price)
    y = np.sort(y)
    x = list(range(len(y)))

    plt.plot(x, y, 'x', color='black')


# plot offset function
def plot_offset_fn(offset_fn, total_time_seconds):
    x = list(range(total_time_seconds))
    offsets = []
    for i in range(total_time_seconds):
        offsets.append(offset_fn(i))
    plt.plot(x, offsets, 'x', color='black')


    # schedule_offsetfn returns time-dependent offset, to be added to schedule prices
def schedule_offsetfn(t):

    pi2 = math.pi * 2
    t = t / 100
    c = math.pi * 3000
    wavelength = t / c
    gradient = 100 * t / (c / pi2)
    amplitude = 100 * t / (c / pi2)
    offset = gradient + amplitude * math.sin(wavelength * t)
    return int(round(offset, 0))


def offset_t(t):
    return int(round(t / 10, 0))


# ===== main ======


def run_prde(n_days, k, F):
    # set up common parameters for all market sessions
    start_time = 0.0
    end_time = 60.0 * 60.0 * 24.0 * n_days
    duration = end_time - start_time

    # define traders
    sellers_spec = [('PRDE', 10, {
        'k': k,
        's_min': -1.0,
        's_max': +1.0,
        'F': F
    })]
    buyers_spec = sellers_spec
    traders_spec = {'sellers': sellers_spec, 'buyers': buyers_spec}

    range1 = (50, 100) #, schedule_offsetfn)
    range2 = (150, 200) #, schedule_offsetfn)
    range3 = (220, 280) #, schedule_offsetfn)

    supply_schedule = [{
        'from': start_time,
        'to': start_time + duration / 3,
        'ranges': [range1],
        'stepmode': 'random'
    }, {
        'from': start_time + duration / 3,
        'to': start_time + 2 * duration / 3,
        'ranges': [range2],
        'stepmode': 'random'
    }, {
        'from': start_time + 2 * duration / 3,
        'to': end_time,
        'ranges': [range3],
        'stepmode': 'random'
    }]
    demand_schedule = supply_schedule

    order_interval = 5
    order_sched = {
        'sup': supply_schedule,
        'dem': demand_schedule,
        'interval': order_interval,
        'timemode': 'drip-jitter'
    }

    # n_trials is how many trials (i.e. market sessions) to run in total
    n_trials = 1

    trial = 1

    while trial < (n_trials + 1):

        #  trial_id = 'bse_i%02d_%04d' % (order_interval, trial)
        trial_id = 'k%02d_F%2.2f_d%02d_%02d' % (k, F, n_days, trial)

        tdump = open(f'{trial_id}_avg_balance.csv', 'w')
        dump_all = True
        verbose = True

        market_session(trial_id, start_time, end_time, traders_spec,
                       order_sched, tdump, dump_all, verbose)

        tdump.close()
        trial = trial + 1


#  run_prde(0.1, 4, 0.8)
for k_value in range(4, 8, 1):
    for F_value in np.arange(0.1, 2.0, 0.1):
        run_prde(4, k_value, F_value)
