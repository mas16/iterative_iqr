# Iterative IQR

by Matt Stetz
03/2012

## Introduction

This script identifies outliers from a linear regression model using the interquartile range method (IQR)

* Conventional IQR analysis can be performed by setting the it_flag='N'
* Iterative IQR analysis can be performed by setting the it_flag='Y'

I wrote this script to automate analysis that was previously done using an Excel spreadsheet compiled by Dr. Yinan Fu

Versions of this script have been used in the following publications:

* Fu Y et al JACS 2012 132(20) 8543-50
* Stetz M et al JBNMR 2016 65(3-4) 157-70

## Conventional IQR Analysis

The data are first modeled using linear regression. Differences between the observed and modeled data are calculated and ranked by percentile.

The IQR is defined as the difference between upper and lower quartiles (75th and 25th percentile, respectively)

Outliers are defined as the following:

* Difference between observed and modeled is below the 25th percentile - 1.5IQR
* Difference between observed and modeled is above the 75th percentile + 1.5IQR

## Iterative IQR Analysis

If the script is run in iterative mode (it_flag='Y'), the IQR analysis is performed as follows:

* Conventional IQR analysis to identify outliers
* Remove outliers 
* Determine new linear regression model for remaining data
* Conventional IQR analysis to identify outliers
* Iterate until no more outliers are identified

## Notes

* No assumptions are are made about dependent or independent variable designations
* IQR analysis is performed for both possibilities

## Input Data Format

Data should be in a tab delimited text file with three columns:
* Column 1: Data Identifier/Name
* Column 2: X Values
* Column 3: Y Values
