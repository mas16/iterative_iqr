"""
Script for calculating Interquartile Range (IQR) for
Identification of Outliers in Linear Regression Model.

Points with IQR >= 1.5 are eliminated.

Script follows Microsoft Excel Spreadsheet made by Dr. Yinan Fu
See Ref: Fu Y et al JACS 2012 134(20) 8543-50

Data should be in delimited text file with:
Residue ID in the first column
The first variable in the second column
The second variable in the third column

NOTE: You may have a problem running this script if your text
file was generated on MacOS! We used Windows for this project.

Version History:

IQR.py by MAS 03/2012
Basic IQR calculation and filtering of outliers.
For two parameter linear regression.

Data visualization is provided as .png file(s).
No assumptions are made about dependent or independent variables.

IQR_update.py by MAS 03/31/2012
Added iterative recalcuation of IQR after filtering of outliers.

iterative_IQR_v1.py by MAS 02/21/2018
Cleaned up code.

iterative_IQR_v2.py by MAS 08/2018
Streamlined code to be more pythonic.

iterative_IQR_v3.py by MAS 09/2018
Streamlined code to be more pythonic.

MAS 10/2018
Added annotations.
"""

###################################################################
#Import Libraries
from __future__ import division
import numpy as np
import pylab as plt
import scipy.stats as sci
import sys

#Set parameters for graphics so that figures can be edited in adobe
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['ps.useafm'] = True
plt.rcParams['axes.linewidth'] = 2.0

###################################################################
#User input below:

#Enter datapath to file (include .txt extension)
DATAPATH = 'C:/Users/matt/Desktop/github/iterative_iqr/ellendata.txt'

#Enter datapath to output folder
OUTPATH = 'C:/Users/matt/Desktop/github/iterative_iqr/'

#Perform iteratively (Y or N)?
IT_FLAG = 'y'

###################################################################
#Functions

def read_file(datafile):
    """Open txt file, read it, and store data."""
    data = file(datafile, "r")
    contents = data.readlines()
    data.close()
    return contents

def split_data(datafile):
    """Split data (this is for windows formatted txt)."""
    split = [entry.split() for entry in datafile]
    return split

def parse_data(datafile):
    """Separate data into different lists."""
    resname = [entry[0] for entry in datafile]
    var_1 = [float(entry[1]) for entry in datafile]
    var_2 = [float(entry[2]) for entry in datafile]
    return resname, var_1, var_2

def linfit(xval, yval):
    """Linear regression model of data."""
    z = np.polyfit(xval, yval, 1)
    return z
 
def linfit_eq(fit):
    """Linear regression model equation."""
    eq = np.poly1d(fit)
    print ("\nfit equation: " + str(eq))
    return eq

def pred_yval(xval, eq):
    """Generate predicted y-values from regression model."""
    pred_y = [eq(entry) for entry in xval]
    return pred_y

def gen_difflist(yval, predictedyval):
    """Calculate difference between observed and predicted values."""
    if len(yval) == len(predictedyval):
        diff = [predictedyval[x]-yval[x] for x in range(len(yval))]
        return diff
    else:
        print ("Error: data size mismatch")
        sys.exit()

def find_outliers(diffyval):
    """Find outliers by IQR."""
    #Sort list of differences
    sortedyval = np.sort(diffyval)
    lenlist = float(len(sortedyval))

    #Get quartile position index
    lco = int(0.25*(lenlist+3))
    uco = int(0.25*((3*lenlist)+1))

    #Get quartile indices
    lco1 = int(lco/1)-1
    lco2 = lco1+1
    uco1 = int(uco/1)-1
    uco2 = uco1+1

    #Linear interpolation
    disl  = float(np.sqrt((sortedyval[lco2]-sortedyval[lco1])**2))
    disu  = float(np.sqrt((sortedyval[uco2]-sortedyval[uco1])**2))
    lcosf = lco-float(int(lco/1))
    ucosf = uco-float(int(uco/1))

    if lcosf == 0:
        print (lco-1)
        qrt1 = sortedyval[lco-1]
    else:
        qrt1 = sortedyval[lco1]+(lcosf*disl)
    if ucosf == 0:
        qrt3 = sortedyval[uco-1]
    else:
        qrt3 = sortedyval[uco1]+(ucosf*disu)

    iqr  = qrt3-qrt1
    iqrs = 1.5*float(iqr)

    print ("\nqrt 1: " + str(qrt1))
    print ("\nqrt 3: " + str(qrt3))
    print ("\ninterquartile range: " + str(iqr))

    outlier_list = []

    print ("\nlower cut off:")
    print (float(qrt1-iqrs))
    print ("\nupper cut off:")
    print (float(qrt3+iqrs))

    for val in diffyval:
        if val <= float(qrt1-iqrs) or val >= float(qrt3+iqrs):
            outlier_list.append(val)
    return outlier_list        

def outlier_index(diffyval, outliers):
    """Get outlier list indices."""
    outindex_list = [np.where(diffyval == entry)[0][0] for entry in outliers]
    return outindex_list

def outlier_id(outlier_index_list, res_list):
    """Get outlier ID using index."""
    outlier_res_list = [res_list[entry] for entry in outlier_index_list]    
    return outlier_res_list

def run(res, xval, yval):
    """Perform statistical analysis."""
    fit = linfit(xval, yval)
    print ("\nr^2: " + str(np.round((sci.pearsonr(xval, yval)[0])**2, 3)))
    fiteq = linfit_eq(fit)
    predictedy = pred_yval(xval, fiteq)
    diffylist = gen_difflist(yval, predictedy)
    outliers = find_outliers(diffylist)
    outlierindex = outlier_index(diffylist, outliers)
    outlierids = outlier_id(outlierindex, res)
    return outlierids, fiteq

def remove_outliers(res, xval, yval, out):
    """Remove outliers."""
    index_list = [res.index(entry) for entry in out]
    f_res = []
    f_xval = []
    f_yval = []
    for index in range(len(res)):
        if index not in index_list:
            f_res.append(res[index])
            f_xval.append(xval[index])
            f_yval.append(yval[index])
    return f_res, f_xval, f_yval

def remove_duplicate(list1, list2):
    """Remove duplicate outliers.

    This has to be done because outliers are determined
    separately regardless of choice of x and y variables.
    """
    if len(list1) > len(list2):
        list1_trim = [entry for entry in list1 if entry not in list2]
        return list1_trim, list2
    else:
        list2_trim = [entry for entry in list2 if entry not in list1]
        return list1, list2_trim

def get_outliers(res, xval, yval):
    """Perform outlier identification."""
    out1, eq = run(res, xval, yval)
    #Swap axes
    out2, eq_s = run(res, yval, xval)
    out1, out2 = remove_duplicate(out1, out2)
    out = out1 + out2
    return out, eq, eq_s

def plot(res, xval, yval, out, eq, eq_s, opath, ext):
    """Simple plotting function, show outliers in red."""
    plt.subplot(2, 1, 1)
    plt.plot(xval, yval, 'ok')
    for x in range(len(out)):
        plt.plot(xval[res.index(out[x])], yval[res.index(out[x])], 'or')
    plt.plot(xval, eq(xval), '-k', linewidth=1.0)
    plt.title('Fit eq: y ='+str(eq), fontsize=16)
    plt.xlabel('Column 1 values', fontsize=16)
    plt.ylabel('Column 2 values', fontsize=16)
    plt.tick_params(direction='out', top="off", right="off", width=2.0,
                    axis='both', which ='major', labelsize=16)
    plt.subplot(2, 1, 2)
    plt.plot(yval, xval, 'ok')
    for x in range(len(out)):
        plt.plot(yval[res.index(out[x])],xval[res.index(out[x])], 'or')
    plt.plot(yval,eq_s(yval),'-k',linewidth=1.0)
    plt.title('Fit eq: y ='+str(eq_s),fontsize=16)
    plt.xlabel('Column 2 values',fontsize=16)
    plt.ylabel('Column 1 values',fontsize=16)
    plt.tick_params(direction='out',top="off",right="off",
                    width=2.0,axis='both',which='major',labelsize=16)
    plt.subplots_adjust(hspace=0.75)
    plt.tight_layout()
    plt.savefig(opath+ext+'.png')
    plt.clf()
    return 0

def iterate(res, xval, yval, opath):
    """Start iterative IQR analysis."""
    out, fiteq, fiteq_s = get_outliers(res, xval, yval)
    plot(res, xval, yval, out, fiteq, fiteq_s, opath, 'round1')
    c = 0
    print ('\noutliers in round ' + str(c+1) + ': ')
    print (out)
    #I prefer to use a while loop
    #here because an unpredictable condition must be met to stop iteration
    while len(out) != 0:
        c += 1
        res, xval, yval = remove_outliers(res, xval, yval, out)
        out, fiteq, fiteq_s = get_outliers(res, xval, yval)
        plot(res, xval, yval, out, fiteq, fiteq_s, opath, 'round'+str(c+1))
        print ('\noutliers in round ' + str(c+1) + ': ')
        print (out)
    return res, xval, yval

def main(datapath, outpath, it_flag):
    """Execute everything."""
    res, xval, yval = parse_data(split_data(read_file(datapath)))
    #Check for some common ways a user could type "no"
    if it_flag in ['N','No','n','NO']:
        outliers, fiteq, fiteq_s = get_outliers(res, xval, yval)
        print ('outliers: ')
        print (outliers)
        plot(res, xval, yval, outliers, fiteq, fiteq_s, outpath, 'conventional')
    #Check for some common ways a user could type "yes"
    elif it_flag in ['Y','Yes','y','YES']:
        res, xval, yval = iterate(res, xval, yval, outpath)
    else:
        print 'Please select a valid flag for iterative IQR: Y or N.'
        sys.exit()
    return 0
    
if __name__ == '__main__':
    main(DATAPATH, OUTPATH, IT_FLAG)
