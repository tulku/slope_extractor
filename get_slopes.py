import collections
import csv
import datetime
import matplotlib.pyplot as plt
import numpy
import os
import sys


def moving_average(input_array, n=3):
    """
    Computes the moving average of an `input_array` with
    windows size n.
    """
    ret = numpy.cumsum(input_array, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def read_data(csv_file_path, measurement_col='O2 Charge', date_col='Date', time_col='Time', seconds_col='Time(s)'):
    """ Reads the sensor data from a CSV file. Returns a vector of measurements. """
    if not os.path.isfile(csv_file_path):
        print ('The provided data file cannot be found: {}'.format(csv_file_path))
    measurements = []
    ignored_count = 0
    with open(csv_file_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            date_string = '{} {}'.format(row[date_col], row[time_col])
            date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            try:
                measurements.append(Measurement(date, row[seconds_col], row[measurement_col]))
            except ValueError:
                ignored_count += 1
        print ('Ignored {} rows because some value was invalid. '
               'For example "--" instead of a sensor value.'.format(ignored_count))
    return Measurements(measurements)


class Measurement:
    """ Groups all the elements of a measurement """
    def __init__(self, timestamp, second, value):
        self.timestamp = timestamp
        self.second = float(second)
        self.value = float(value)


class Measurements:
    """
    Gets a list of Measurement and splits them into samples with positive slopes
    and samples with negative slopes.
    """
    def __init__(self, measurement_list, diff_noise=0.4):
        self._measurements = measurement_list
        # Convert to a series of numpy arrrays.
        self._values = numpy.array([m.value for m in self._measurements])
        self._seconds = numpy.array([m.second for m in self._measurements])
        self._timestamps = numpy.array([m.timestamp for m in self._measurements])

        # Calculate the first derivate of the values.
        self._values_diff = numpy.diff(self._values)
        ### Gets all the indices where the _valies_diff is bigger then -noise.
        ### These should be all the indices where the slope is 'mostly' positive.
        positive = numpy.where(self._values_diff > -1*diff_noise)
        ### Gets all the indices where the _valies_diff is smaller then -noise.
        ### These should be all the indices where the slope is 'very' negative.
        negative = numpy.where(self._values_diff < -1*diff_noise)

        # Get only the measurements points and with positive derivatives.
        self._positive_values = self._values[positive]
        # Get the seconds that correspond to those positive points.
        self._positive_seconds = self._seconds[positive]
        # Get the timestamps that correspond to those positive points.
        self._positive_timestamps = self._timestamps[positive]
        # Get only the measurements points with negative derivatives.
        self._negative_values = self._values[negative]
        # Get the seconds that correspond to those negative points.
        self._negative_seconds = self._seconds[negative]
        # Get the timestamps that correspond to those negative points.
        self._negative_timestamps = self._timestamps[negative]

        ## Split the original array into the different positive slopes.
        # The [0] is numpy being weird, safe to ignore.
        self._positive_slopes = numpy.split(self._values, negative[0])
        self._positive_slopes_seconds = numpy.split(self._seconds, negative[0])
        self._positive_slopes_timestamps = numpy.split(self._timestamps, negative[0])
        print ('Found {} positive slopes!'.format(len(self._positive_slopes)))


    def plot_all(self):
        plt.plot(self._seconds, self._values)
        legends = ['original values']
        for index, positive_slope in enumerate(self._positive_slopes):
            plt.plot(self._positive_slopes_seconds[index], positive_slope, '.')
            legends.append('positive_slope_{}'.format(index))

        plt.legend(legends)

    def smooth(self, window=5):
        """
        Smooths the measured values using a moving average of window `window`
        """
        values = numpy.array([m.value for m in self._measurements])
        smoothed_values = moving_average(values, window)
        seconds = [m.second for m in self._measurements[window-1:]]
        SmoothedValues = collections.namedtuple('SmoothValues', ['seconds', 'smoothed_values'])
        return SmoothedValues(seconds, smoothed_values)


def write_to_multple_files(output_base, base_name, all_times, all_seconds, all_values):
    """
    Writes one csv file per 'slope'. all_times, all_seconds, all_values are lists of lists. Each inner
    list containes the times, seconds and values that form one of the slopes.
    """
    slope_number = 1
    for times, seconds, values in zip(all_times, all_seconds, all_values):
        out_filename = os.path.join(output_base, '{}_{}.csv'.format(base_name, slope_number))
        times = [time.strftime('%Y-%m-%d %H:%M:%S') for time in times]

        with open(out_filename, 'w') as outfile:
            outfile.write('Time, Time(s), O2 Charge\n')
            out_csv = csv.writer(outfile)
            for row_data in zip(times, seconds, values):
                out_csv.writerow(row_data)
        slope_number += 1


class SlopesWriter:
    """
    Writes the found slopes to different csv files and one csv with all the slopes.
    """
    def __init__(self, measurements, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self._output_base = output_path
        self._measurements = measurements

    def write(self):
        write_to_multple_files(self._output_base, 'positive_slope',
                               self._measurements._positive_slopes_timestamps,
                               self._measurements._positive_slopes_seconds,
                               self._measurements._positive_slopes)

if __name__ == '__main__':
    # TODO: replace with argparse
    measurements = read_data(sys.argv[1])
    measurements.plot_all()
    # measurements.smooth()
    w = SlopesWriter(measurements, 'files/')
    w.write()
    plt.show()
