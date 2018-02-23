#Script for calculating Interquartile Range (IQR)
#For Linear Regression

#Points with IQR >= 1.5 are eliminated
#Script follows Microsoft Excel Spreadsheet made by Dr. Yinan Fu
#See Ref: Fu Y et al JACS 2012 134(20) 8543-50

#Data should be in delimited text file with:
#Residue ID in the first column,
#The first variable in the second column,
#The second variable in the third column

#Version History:

#IQR.py by MAS 03/2012
#Basic IQR calculation and filtering of outliers
#For two parameter linear regression
#Data visualization is provided as .png file(s)
#Option to perform once or iteratively
#No assumptions are made about dependent or independent variables
#Both possibilities are considered

#IQR_update.py by MAS 03/31/2012
#Added iterative recalcuation of IQR after filtering of outliers

#IQR_v3.py by MAS 02/21/2018
#Cleaned up code

###################################################################
#User input below:

#Enter datapath to file (include .txt extension)
datapath='C:/Users/matt/Documents/Scripts/Interquartile_Range/ellendata.txt'

#Enter datapath to output folder
outpath='C:/Users/matt/Documents/Scripts/Interquartile_Range/'

#Perform iteratively (Y or N)?
it_flag='y'


###################################################################
#Import Libraries
import numpy as np
import pylab as plt
import scipy.stats as sci

###################################################################
#Set parameters for graphics

plt.rcParams['ps.fonttype']=42
plt.rcParams['ps.useafm']=True
plt.rcParams['axes.linewidth'] = 2.0

###################################################################
#Functions

#Open .txt file, read it, and store data
def readfile(datafile):
    data = file(datafile,"r")
    contents = data.readlines()
    data.close()
    return contents

#Parse data into separate lists
def parsedata(datafile):
    resname=[]
    var1=[]
    var2=[]
    for x in range(len(datafile)):
        split=datafile[x].split()
        resname.append(split[0])
        var1.append(float(split[1]))
        var2.append(float(split[2]))
    return resname,var1,var2

#Linear regression model of data
def linfit(xval,yval):
    z=np.polyfit(xval,yval,1)
    return z

#Linear regression model expression 
def linfiteq(fit):
    eq=np.poly1d(fit)
    print "\nfit equation: " + str(eq)
    return eq

#Generate predicted y-values from regression model
def predyval(xval,yval,eq):
    predylist=[]
    for x in xval:
        predylist.append(eq(x))
    return predylist

#Calculate difference between observed and predicted values
def gen_difflist(yval,predictedyval):
    diffyval=[]
    i=0
    while i < len(yval):
        diffyval.append(predictedyval[i]-yval[i])
        i+=1
    return diffyval

#Find outliers by IQR
def find_outliers(diffyval):

    #Sort list of differences
    sortedyval=np.sort(diffyval)
    lenlist=float(len(sortedyval))

    #Get quartile position index
    lco=0.25*(lenlist+3)
    uco=0.25*((3*lenlist)+1)

    #Get quartile indices
    lco1=int(lco/1)-1
    lco2=lco1+1
    uco1=int(uco/1)-1
    uco2=uco1+1

    #Linear interpolation
    disl=float(np.sqrt((sortedyval[lco2]-sortedyval[lco1])**2))
    disu=float(np.sqrt((sortedyval[uco2]-sortedyval[uco1])**2))
    lcosf=lco-float(int(lco/1))
    ucosf=uco-float(int(uco/1))

    if lcosf == 0:
        qrt1 = sortedyval[lco-1]
    else:
        qrt1 = sortedyval[lco1]+(lcosf*disl)
    if ucosf == 0:
        qrt3 = sortedyval[uco-1]
    else:
        qrt3 = sortedyval[uco1]+(ucosf*disu)

    iqr = qrt3-qrt1
    iqrs= 1.5*float(iqr)

    print "\nqrt 1: " + str(qrt1)
    print "\nqrt 3: " + str(qrt3)
    print "\ninterquartile range: " + str(iqr)

    outlierlist=[]

    print "\nlower cut off:"
    print float(qrt1-iqrs)
    print "\nupper cut off:"
    print float(qrt3+iqrs)

    for y in diffyval:
        if y <= float(qrt1-iqrs) or y >= float(qrt3+iqrs):
            outlierlist.append(y)
    return outlierlist

#Get outlier list index
def outlier_index(diffyval,outliers):
    outlierindexlist=[]
    for x in outliers:
        outlierindexlist.append(np.where(diffyval==x)[0][0])
    return outlierindexlist

#Get outlier ID using index
def outlier_id(outlierindexlist,reslist):
    outlierreslist=[]
    for x in outlierindexlist:
        outlierreslist.append(reslist[x])
    return outlierreslist

#Perform statistical analysis
def run(res,xval,yval):
    fit=linfit(xval,yval)
    print "\nr^2: " + str(np.round((sci.pearsonr(xval,yval)[0])**2,3))
    fiteq=linfiteq(fit)
    predictedy=predyval(xval,yval,fiteq)
    diffylist=gen_difflist(yval,predictedy)
    outliers=find_outliers(diffylist)
    outlierindex=outlier_index(diffylist,outliers)
    outlierids=outlier_id(outlierindex,res)
    return outlierids, fiteq

#Perform statistical analysis with axes swapped
def run_swap(res,xval,yval):
    fit=linfit(yval,xval)
    fiteq=linfiteq(fit)
    predictedy=predyval(yval,xval,fiteq)
    diffylist=gen_difflist(xval,predictedy)
    outliers=find_outliers(diffylist)
    outlierindex=outlier_index(diffylist,outliers)
    outlierids=outlier_id(outlierindex,res)
    return outlierids, fiteq

#Remove outliers
def remove_outliers(res,xval,yval,out):
    index=[]
    f_res=[]
    f_xval=[]
    f_yval=[]
    for x in range(len(out)):
        index.append(res.index(out[x]))
    for x in range(len(res)):
        #Prevent having indices change after an element is removed
        if x in index:
            pass
        else:
            f_res.append(res[x])
            f_xval.append(xval[x])
            f_yval.append(yval[x])
    return f_res,f_xval,f_yval

#Don't consider outlier more than once
def remove_duplicate(list1,list2):
    len_1=len(list1)
    len_2=len(list2)
    f_list1=[]
    f_list2=[]
    if len_1>=len_2:
        i=0
        index=[]
        for x in range(len(list1)):
            while i < len(list2):
                if list1[x]==list2[i]:
                    index.append(x)
                    i+=1
                else:
                    i+=1
            i=0
        for x in range(len(list1)):
            if x not in index:
                f_list1.append(list1[x])
        f_list2=list2
    else:
        i=0
        index=[]
        for x in range(len(list2)):
            while i < len(list1):
                if list2[x]==list1[i]:
                    index.append(x)
                    i+=1
                else:
                    i+=1
            i=0
        for x in range(len(list2)):
            if x not in index:
                f_list2.append(list2[x])
        f_list1=list1
    return f_list1, f_list2

#Perform outlier identification
def get_outliers(res,xval,yval):
    out1,eq=run(res,xval,yval)
    out2,eq_s=run_swap(res,xval,yval)
    out1,out2=remove_duplicate(out1,out2)
    out=out1+out2
    return out, eq, eq_s

#Start Iterations
def iterate(res,xval,yval):
    out,fiteq,fiteq_s=get_outliers(res,xval,yval)
    plot(res,xval,yval,out,fiteq,fiteq_s)
    c=0
    print '\noutliers in round ' + str(c+1) + ': '
    print out
    while len(out) != 0:
        c+=1
        res,xval,yval=remove_outliers(res,xval,yval,out)
        out,fiteq,fiteq_s=get_outliers(res,xval,yval)
        plot(res,xval,yval,out,fiteq,fiteq_s)
        print '\noutliers in round ' + str(c+1) + ': '
        print out
    return res,xval,yval

#Simple plotting function, show outliers in red
def plot(res,xval,yval,out,eq,eq_s):
    plt.subplot(2,1,1)
    plt.plot(xval,yval,'ok')
    for x in range(len(out)):
        plt.plot(xval[res.index(out[x])],yval[res.index(out[x])],'or')
    plt.plot(xval,eq(xval),'-k',linewidth=1.0)
    plt.title('Fit eq: y ='+str(eq),fontsize=16)
    plt.xlabel('Column 1 values',fontsize=16)
    plt.ylabel('Column 2 values',fontsize=16)
    plt.tick_params(direction='out')
    plt.tick_params(right="off")
    plt.tick_params(top="off")
    plt.tick_params(width=2.0)
    plt.tick_params(axis='both',which='major',labelsize=16)
    plt.subplot(2,1,2)
    plt.plot(yval,xval,'ok')
    for x in range(len(out)):
        plt.plot(yval[res.index(out[x])],xval[res.index(out[x])],'or')
    plt.plot(yval,eq_s(yval),'-k',linewidth=1.0)
    plt.title('Fit eq: y ='+str(eq_s),fontsize=16)
    plt.xlabel('Column 2 values',fontsize=16)
    plt.ylabel('Column 1 values',fontsize=16)
    plt.tick_params(direction='out')
    plt.tick_params(right="off")
    plt.tick_params(top="off")
    plt.tick_params(width=2.0)
    plt.tick_params(axis='both',which='major',labelsize=16)
    plt.subplots_adjust(hspace=0.75)
    plt.show()
    return 0

if __name__=='__main__':
    RES,XVAL,YVAL=parsedata(readfile(datapath))
    if it_flag in ['N','No','n','NO']:
        outliers,fiteq,fiteq_s=get_outliers(RES,XVAL,YVAL)
        print 'outliers: '
        print outliers
        plot(RES,XVAL,YVAL,outliers,fiteq,fiteq_s)
    elif it_flag in ['Y','Yes','y','YES']:
        RES,XVAL,YVAL=iterate(RES,XVAL,YVAL)
    else:
        print 'Please select a valid flag for performing iterative IQR: Y or N.'
