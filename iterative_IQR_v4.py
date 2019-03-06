"""
Script for identifying outliers from simple liner regression models
using interquartile range (IQR). Points with IQR >= 1.5 are eliminated.

This script was written to assist Dr. Fu from the University of Pennsylvania
with her statistical analysis. She had developed her own modified method for
outlier identification using the IQR and had asked me to code a script to
automate the procedure.

The user has the option to determine outliers using the conventional approach
or an approach where the axes are swapped.

The user also has the option to iterate the procedure repeatedly wherein with
each iteration the outliers are removed and then the data are re-fit.

Parameters
----------------
DATAFILE - type the file name of the data file, including the file extension

SWAP_FLAG - "y" or "n" to swap the axes as part of the outlier identification

IT_FLAG - "y" or "n" to iterate the process until no outliers are identified

-----------------
Data is structured as a numpy structured array.

Plots of the data with outliers in red and linear models as dashed lines are
saved to the working directory.

A text listing the quartiles, IQR, and outliers is also saved to the working
directory.

by mas march 2019
"""

# Import Libraries
import numpy as np
import pylab as plt
import seaborn as sns
import os

# Set plotting styles
sns.set_style("ticks")
plt.rcParams['axes.linewidth'] = 2

# Watermark
__title__ = "iterative_iqr"
__author__ = "matt stetz"
__date__ = "4 March 2019"

##########################################
# User-Defined information below

# Name of data file
DATAFILE = "ellendata.txt"

# Swap x and y Axes during outlier analysis (y/n)?
SWAP_FLAG = "y"

# Perform iteratively? (y/n)
IT_FLAG = "n"

##########################################


# Functions
def read_file(datafile=DATAFILE):
    """This function reads the data file and returns the data
    as a list of tuples where each row in the data file is the tuple.

    :param datafile: str, file name
    :return: list, file contents
    """
    try:
        f = open(os.getcwd()+"/"+datafile)
    except FileNotFoundError:
        print("ERROR: Data file not found.")
    else:
        with f:
            return [tuple(entry.split()) for entry in f]


def calc_quartiles(sorted_diffs, cutoff):
    """This function calculates the quartiles based on the residuals
    (difference between observed data and model). Note that indexing has to be
    done with int.

    :param sorted_diffs: np array, residuals (float)
    :param cutoff: float (cutoff value from Dr. Fu's method)
    :return: float, quartile value
    """

    # Have to convert to int since using as an index
    point_1 = int(cutoff) - 1
    point_2 = point_1 + 1
    distance = np.sqrt((sorted_diffs[point_2] - sorted_diffs[point_1])**2)

    # Account for integer truncation, linear interpolation is used if integer
    # is truncated
    point_f = cutoff - int(cutoff)

    if point_f == 0:
        quartile = sorted_diffs[int(cutoff) - 1]
    else:
        quartile = sorted_diffs[point_1] + point_f*distance

    return quartile


def get_outlier_index(diffs, iqr, quartile_3, quartile_1):
    """This function determines if the value is beyond 1.5*IQR

    :param diffs: np array, residuals (float)
    :param iqr: float, IQR value
    :param quartile_3: float, 3rd quartile
    :param quartile_1: float, 1st quartile
    :return: list, list of outlier values (float)
    """
    return [diff for diff in diffs if diff >= (quartile_3 + 1.5*iqr)
            or diff <= (quartile_1 - 1.5*iqr)]


def map_outliers(outlier_list, residuals, data):
    """This function determines the ID of the outlier values.

    :param outlier_list: list, outlier values (float)
    :param residuals: np array, residuals (float)
    :param data: np array, the data set
    :return: list, outlier IDs (str)
    """
    return [data[np.where(residuals == entry)[0][0]] for entry in outlier_list]


def get_outliers(diffs, names, counter):
    """This function determines the IQR cutoffs values using Dr. Fu's
    alternative method. The cutoffs are then passed to the calc_quartiles
    function to determine the quartiles. The quartiles are then used to
    identify the outliers by being passed to the get_outlier_index function.
    The outlier IDs are obtained and organized using the outlier_ids funciton.

    :param diffs: np array, residuals (float)
    :param names: np array, IDs
    :param counter: int, counter keeping track of iterations
    :return: list, outlier IDs (str)
    """
    # sort residuals
    sorted_diffs = np.sort(diffs)
    # get quartile position index (float)
    lower_cutoff = 0.25 * (len(diffs) + 3)
    upper_cutoff = 0.25 * (3*len(diffs) + 1)
    # calc quartiles
    quartile_1 = calc_quartiles(sorted_diffs, lower_cutoff)
    quartile_3 = calc_quartiles(sorted_diffs, upper_cutoff)
    # define iqr
    iqr = quartile_3 - quartile_1
    # get outlier index
    outlier_list = get_outlier_index(diffs, iqr, quartile_3, quartile_1)
    # get outlier id from index
    outlier_ids = map_outliers(outlier_list, diffs, names)

    # open output file
    outlier_str = "".join(str(outlier_ids))
    with open(os.getcwd() + "/" + "summary.txt", "a") as f:
        f.write('\n')
        f.write("{:<6} {:<15} {:<15} {:<9} {:<6}"
                .format(counter, np.round(quartile_1, 4),
                        np.round(quartile_3, 4), np.round(iqr, 4),
                        outlier_str))
        f.write('\n')

    return outlier_ids


def perform_outlier_analysis(x_data, y_data, names, counter):
    """This function fits a linear model to the data, determines the residuals,
    and then calls the get_outliers function to identify the outliers.

    :param x_data: np array, x axis values (float)
    :param y_data: np array, y axis values (float)
    :param names: np array, IDs (str)
    :param counter: int, counter keeping track of iterations
    :return: list (outliers), outlier values (float);
             array-like (linear model), linear model
    """
    linear_model = np.poly1d(np.polyfit(x_data, y_data, 1))
    residuals = linear_model(x_data) - y_data
    outliers = get_outliers(residuals, names, counter)
    return outliers, linear_model


def remove_outliers(x_outliers, y_outliers, data):
    """This function uses the outlier values to identify the outlier ID. This
    is accomplished using the np.where method. If the option to swap axes
    (outlier_flag) is set to "no", then the outliers identified from swapping
    the axes are ignored.

    Outliers are then deleted. Operations on np arrays are not done in-place,
    so the updated dataset is assigned to the object, "data."

    :param x_outliers: list, outlier values determined conventional way
    :param y_outliers: list, outlier values determined after swapping axes
    :param data: np array, the data
    :return: list (unique_outliers), outlier IDs;
             np array (data), the data without the outliers
    """
    unique_outliers = list(set(x_outliers + y_outliers))
    for entry in unique_outliers:
        if entry in data["name"]:
            index = np.where(data["name"] == entry)[0][0]
            data = np.delete(data, index)
    return unique_outliers, data


def plot_one(outliers, model, data, counter):
    """Plotting the data under the condition that axes are not swapped.

    :param outliers: list, outlier IDs (str)
    :param model: array_like, linear model
    :param data: np array, the data set
    :param counter: int, counter keeping track of iterations
    :return: None
    """
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    smooth_x = np.linspace(min(data["xval"]), max(data["xval"]), 1000)
    plt.plot(data["xval"], data["yval"], "ok", markersize=6)
    plt.plot(smooth_x, model(smooth_x), "--k", linewidth=2.5)
    for outlier in outliers:
        index = np.where(data["name"] == outlier)[0][0]
        plt.plot(data["xval"][index], data["yval"][index], "or", markersize=6)
    plt.tick_params(width=2, labelsize=14)
    plt.axis([0, 0.6, 0, 0.6])
    plt.xlabel("Independent Variables", fontsize=14)
    plt.ylabel("Dependent Variables", fontsize=14)
    sns.despine()
    plt.savefig(os.getcwd()+"/"+"no_swap_round"+str(counter)+".png")
    plt.clf()


def plot_all(x_outliers, y_outliers, x_model, y_model, data, counter):
    """Plotting the data. Outliers shown in red. Linear model shown as dotted
    line.

    :param x_outliers: list, outlier IDs (str)
    :param y_outliers: list, outlier IDs (str)
    :param x_model: array_like, linear model
    :param y_model: array_like, linear model
    :param data: np array, the data
    :param counter: int, counter keeping track of iterations
    :return: None
    """
    w, h = plt.figaspect(1.5)
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_subplot(211)
    ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    smooth_x = np.linspace(min(data["xval"]), max(data["xval"]), 1000)
    smooth_y = np.linspace(min(data["yval"]), max(data["yval"]), 1000)
    plt.plot(data["xval"], data["yval"], "ok", markersize=6)
    plt.plot(smooth_x, x_model(smooth_x), "--k", linewidth=2.5)
    for outlier in x_outliers:
        index = np.where(data["name"] == outlier)[0][0]
        plt.plot(data["xval"][index], data["yval"][index], "or", markersize=6)
    plt.tick_params(width=2, labelsize=14)
    plt.axis([0, 1.1*max(data["xval"]), 0, 1.1*max(data["yval"])])
    plt.xlabel("Independent Variables", fontsize=14)
    plt.ylabel("Dependent Variables", fontsize=14)
    ax = fig.add_subplot(212)
    ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    plt.plot(data["yval"], data["xval"], "ok", markersize=6)
    plt.plot(smooth_y, y_model(smooth_y), "--k", linewidth=2.5)
    for outlier in y_outliers:
        index = np.where(data["name"] == outlier)[0][0]
        plt.plot(data["yval"][index], data["xval"][index], "or", markersize=6)
    plt.tick_params(width=2, labelsize=14)
    plt.axis([0, 1.1*max(data["yval"]), 0, 1.1*max(data["xval"])])
    plt.xlabel("Independent Variables", fontsize=14)
    plt.ylabel("Dependent Variables", fontsize=14)
    plt.subplots_adjust(left=0.2, hspace=0.5)
    sns.despine()
    plt.savefig(os.getcwd() + "/" + "swap_round" + str(counter) + ".png")


def run_analysis(data, counter, outlier_flag):
    """This function executes the IQR calculation by first calling
    perform_outlier_analysis which generates the linear model of the data and
    identifiers the outliers then calling remove_outliers to generate a new
    data set devoid of outliers.

    :param data: np array, the data
    :param counter: int, counter variable keeping track of iterations
    :param outlier_flag: str, "y" or "n" denoting whether or not to swap axes
    :return: list (all_outliers), list of outlier IDs (str);
             np array (data), the data without outliers;
    """
    x_outliers, x_model = perform_outlier_analysis(data["xval"], data["yval"],
                                                   data["name"], counter)
    if outlier_flag == "n":
        plot_one(x_outliers, x_model, data, counter)
        all_outliers, data = remove_outliers(x_outliers, [], data)
    elif outlier_flag == "y":
        y_outliers, y_model = perform_outlier_analysis(data["yval"],
                                                       data["xval"],
                                                       data["name"], counter)
        plot_all(x_outliers, y_outliers, x_model, y_model, data, counter)
        all_outliers, data = remove_outliers(x_outliers, y_outliers, data)
    else:
        raise ValueError("No data for outlier determination!")
    return all_outliers, data


def iterate_analysis(all_outliers, data, outlier_flag, counter):
    """This function executes the IQR calculation (run_analysis) recursively
    until no more outliers are identified.

    :param all_outliers: list, list of str values outlier IDs
    :param data: np array, the data
    :param outlier_flag: str, "y" or "n", denoting whether or not to swap axes
    :param counter: int, counter variable keeping track of number of iterations
    :return: None
    """
    while len(all_outliers) > 0:
        counter += 1
        all_outliers, data = run_analysis(data, counter, outlier_flag)


def check_flags(flag):
    """This function checks if the flag variables set by the user are valid.
    Valid flags are variations of "yes" or "no". If the flag is valid, it is
    then converted to a standardized flag "y" or "n". If the flag is not valid
    an exception is raised

    :param flag: str, ideally something similar to "yes" or "no"
    :return: str, standardized flag: "y" or "n"
    """
    if flag in ["n", "N", "no", "No", "NO"]:
        flag = "n"
    elif flag in ["y", "Y", "yes", "Yes", "YES", "YEs", "yES", "yeS", "yEs"]:
        flag = "y"
    else:
        raise ValueError("Please use an acceptable flag (for example, y or n)")
    return flag


def run(swap_flag=SWAP_FLAG, it_flag=IT_FLAG):
    """This function transforms the data to a numpy structured array
    and executes the appropriate IQR calculation based on what the user has
    set the flags to:

    swap_flag = "y" : Swap x and y axes when determining outliers. The total
    number of outliers is the sum of outliers identified before and after
    swapping the x and y axes.

    it_flag = "n" : Perform IQR iteratively. This means once outliers are
    identified, they are removed and the IQR calculation is repeated.

    :param swap_flag: str, "y" or "n"
    :param it_flag: str, "y" or "n"
    :return: None
    """
    # Initialize output file
    with open(os.getcwd() + "/" + "summary.txt", "w") as f:
        f.write("{:<6} {:<15} {:<15} {:<9} {:<6}"
                .format("ROUND", "1st QUARTILE", "3rd QUARTILE", "IQR",
                        "OUTLIERS"))
    # Check flags to make sure they are compatible with "y" or "n"
    swap_flag = check_flags(swap_flag)
    it_flag = check_flags(it_flag)
    # Read data from input file
    all_data = read_file()
    # Make structured array
    # Note all_data.shape will be (n,) but operations are still vectorized
    all_data = np.array(all_data, dtype=[("name", "U10"), ("xval", float),
                                         ("yval", float)])
    # Start counter to keep track of IQR iterations (start at 1)
    counter = 1
    # Run first IQR calculation
    outliers, data = run_analysis(all_data, counter, swap_flag)
    # Check if the user wants to repeat the IQR calculation iteratively
    if it_flag == 'y':
        iterate_analysis(outliers, data, swap_flag, counter)


if __name__ == '__main__':
    run()
