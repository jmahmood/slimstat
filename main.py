import logging
import random
import statistics
import time
import bbev
from scipy.stats._stats_py import TtestResult

from logColours import ColorFormatter
from weightHandler import *
import evdev
from scipy import stats

DEBUG = True

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
if DEBUG:
    ch.setLevel(logging.DEBUG)
else:
    ch.setLevel(logging.INFO)
ch.setFormatter(ColorFormatter())
logger.addHandler(ch)

weight_data_database = sqlite3.Connection("./test.db",
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
if DEBUG:
    weight_data_database.set_trace_callback(logger.debug)

create_database_table(weight_data_database)
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
device_path = (device.path for device in devices if device.name == 'Nintendo Wii Remote Balance Board').__next__()
balance_board: evdev.InputDevice = evdev.InputDevice(
    device_path,
)
"""
The next step should be using statistical functions to determine whether or not your weight loss, over a period of time
was statistically significant, with a "There is a 14% chance of a change in weight" etc..

I assumed I could do this w/ z-scores, but I can't seem to convert the z-score.

We probably want to add more samples to the calculation.

"""


def morning(comparison_time: datetime.datetime):
    return 5 <= comparison_time.time().hour < 11


def afternoon(comparison_time: datetime.datetime):
    return 11 <= comparison_time.time().hour < 16


def evening(comparison_time: datetime.datetime):
    return 16 <= comparison_time.time().hour < 22


def night(comparison_time: datetime.datetime):
    return comparison_time.time().hour < 5 or comparison_time.time().hour >= 22


def _sethour(comparison_time: datetime.datetime, start: datetime.datetime, end: datetime.datetime):
    if morning(comparison_time):
        start = start.replace(hour=5)
        end = end.replace(hour=11)
    elif afternoon(comparison_time):
        start = start.replace(hour=11)
        end = end.replace(hour=16)
    elif evening(comparison_time):
        start = start.replace(hour=16)
        end = end.replace(hour=22)
    elif night(comparison_time):
        start = start - datetime.timedelta(days=1)
        start = start.replace(hour=22)
        end = end.replace(hour=5)
    else:
        raise Exception(comparison_time)
    return start, end


def get_start_end(comparison_time: datetime.datetime, days_ago):
    start = comparison_time - datetime.timedelta(days=days_ago)
    end = comparison_time - datetime.timedelta(days=days_ago)
    start = start.replace(minute=0)
    end = end.replace(minute=0)
    return start, end


def four_weeks_ago(comparison_time: datetime.datetime):
    return _sethour(comparison_time, *get_start_end(comparison_time, 28))


def last_week(comparison_time: datetime.datetime):
    return _sethour(comparison_time, *get_start_end(comparison_time, 7))


def yesterday(comparison_time: datetime.datetime):
    return _sethour(comparison_time, *get_start_end(comparison_time, 1))


def debug_statistics(title, all_samples):
    if len(all_samples) == 0:
        logger.debug(f"""
==========================================================================================
No Data Available: {title}
==========================================================================================""")
    else:
        normal_distribution = statistics.NormalDist.from_samples(all_samples)
        logger.debug(f"""
==========================================================================================
{title}
==========================================================================================
mean: {normal_distribution.mean}
median: {normal_distribution.median}
stddev: {normal_distribution.stdev}
variance: {normal_distribution.variance}
==========================================================================================""")


def debug_t_test_stats(t_test: TtestResult, threshold):
    logger.debug(f"""
t statistic: {t_test.statistic}
pvalue: {t_test.pvalue}
dof: {t_test.df}
CI: {t_test.confidence_interval(1 - threshold)} 
""")


def has_lost_weight(threshold, recent_data_all_samples, previous_data_all_samples):
    sample_size = min([len(recent_data_all_samples), len(previous_data_all_samples)])
    lose_weight_t_test = stats.ttest_rel(
        random.sample(recent_data_all_samples, k=sample_size),
        random.sample(previous_data_all_samples, k=sample_size),
        None, 'omit', 'less')
    debug_t_test_stats(lose_weight_t_test, threshold)
    return lose_weight_t_test.pvalue < threshold


for event in balance_board.read_loop():
    if event.code == evdev.ecodes.BTN_A or DEBUG:
        now = datetime.datetime.now()
        # now = now.replace(hour=9)
        samples = get_data_range_mean(weight_data_database,
                                      *_sethour(now, *get_start_end(now, 0)))

        yesterday_samples = get_data_range_mean(weight_data_database,
                                                *yesterday(now))

        last_week_samples = get_data_range_mean(weight_data_database,
                                                *last_week(now))

        four_weeks_ago_samples = get_data_range_mean(weight_data_database,
                                                     *four_weeks_ago(now))
        debug_statistics("Recent Data", samples)
        debug_statistics("Yesterday's Data", yesterday_samples)
        debug_statistics("Last Week's Data", last_week_samples)
        debug_statistics("Last Month's Data", four_weeks_ago_samples)

        if len(samples) == 0:
            logger.error("No samples for today.  Please weigh yourself first.")
            quit()

        if len(yesterday_samples) > 0:
            logger.info(
                f"""Is there an 80% chance or greater than you lost weight between now and yesterday?  {
                has_lost_weight(0.10, samples, yesterday_samples)}""")

        if len(last_week_samples) > 0:
            logger.info(
                f"""Is there an 80% chance or greater than you lost weight between now and last week?  {
                has_lost_weight(0.10, samples, last_week_samples)}""")

        if len(four_weeks_ago_samples) > 0:
            logger.info(
                f"""Is there an 80% chance or greater than you lost weight between now and four weeks ago?  {
                has_lost_weight(0.10, samples, last_week_samples)}""")
        balance_board.close()
        quit()

    if event.code == evdev.ecodes.ABS_HAT1X and event.value > 500:
        # start the process
        balance_board_inner: evdev.InputDevice = evdev.InputDevice(
            device_path,
        )

        weight_data = bbev.calculate_weight_with_statistics(
            balance_board_inner,
            100,
            logger
        )

        trimmed_stats = weight_data.trimmed_statistics(30)
        logger.info(f"""
            Mean: {trimmed_stats['mean']}
            Median: {trimmed_stats['median']}
            STDEV: {trimmed_stats['stdev']}
            Samples: {trimmed_stats['samples']}
        """)

        to_save: WeightData = {
            "mean": trimmed_stats['mean'],
            "median": trimmed_stats['median'],
            "stdev": trimmed_stats['stdev'],
            "samples": trimmed_stats['samples'],
            "measurement_datetime": datetime.datetime.now(),
        }
        save_data(weight_data_database, to_save)
        time.sleep(1)
