# -*- coding: utf-8 -*-

# This python script will not be executed by MIDA automatically
#
# Users may execute this .py file by hand (e.g., python plotScript.py)
#
# Created by: Xin

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import os

nChains = 3 # the number of MCMC chains (0: single MCMC chains)
outDir = 'F:\Lab\Work\MIDA\Code\MIDA-command\DAresults/' # the path of DA results
outJ = 'mismatch_accepted.csv' # file to save mismatch between obs and simu
outC = 'parameter_accepted.csv' # file to save accepted parameter values
outConvergenceFile = 'convergence.txt' # file to save G-R convergence estimators
paramNum=21 # the number of parameters used in DA
# the name of parameters
names_in_DA = ['c1','c2','c3','c4','c5','c6','c7','c8','c9','c10','c11','c12','c13','c14','c15','c16','c17','c18','c19','c20','c21']
is_show = 1 # 1: to show figures; 0: to save figures

""" read DA results and generate plots
"""
plt.style.use('ggplot')
rnpic = math.floor(np.sqrt(paramNum))
cnpic = paramNum - rnpic * rnpic + rnpic
if nChains>0: # multiple MCMC chains
    outDir_default = outDir  # the path of DA results
    outJ_default = outJ  # filename
    outC_default = outC  # filename
    for i in range(nChains):
        outDir = outDir_default + 'Chain_' + str(i) + '/'
        outJ = outDir + outJ_default
        outC = outDir + outC_default
        try:
            dfOutC = pd.read_csv(outC, index_col=0)
            c = dfOutC.values  # convert it to numpy array
        except:
            raise Exception(
                'WARNING: Error occurred when reading ' + outC_default + 'in the Chain_' + str(i) + ' folder.')
        # histograms for parameters
        plt.ion()
        plt.figure(2 * i + 1)
        for j in range(paramNum):
            plt.subplot(rnpic, cnpic, j + 1)
            plt.hist(c[:, j], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[j])
            plt.tick_params(top='off', right='off')
            plt.legend()
        plt.suptitle('Posterior distributions of parameters')
        if is_show:
            plt.show()
        else:
            plt.savefig(outDir + '/ppdf.png')  # save figures
            print('****Saving figures: OK (in '+outDir+')****')
        # the 2nd plot: mismatches between observations and simulation
        try:
            dfOut = pd.read_csv(outJ, index_col=0)
            jerror = dfOut.values  # convert it to numpy array
        except:
            raise Exception('WARNING: Error occurred when reading ' + outJ_default + ' in the Chain_' + str(
                i) + ' folder.')
        jnum = range(jerror.shape[0] // 2, jerror.shape[0])  # only show the final 1/2 part
        plt.figure(2 * i + 2)
        plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
        plt.title(
            'Mismatches between observations and simulation outputs during MCMC sampling')
        plt.xlabel('Samples')
        plt.ylabel('Mismatch')
        if is_show:
            plt.show()
        else:
            plt.savefig(outDir + '/mismatch.png')  # save figures
            print('****Saving figures: OK (in '+outDir+')****')
    # 3rd plot: convergence test
    plt.figure(2 * nChains + 1)
    if outConvergenceFile!='' and os.path.isfile(outConvergenceFile):
        try:
            # outConvergenceFile has already been changed absolute path in step1()  or plotNamelist()
            dfGRList = pd.read_csv(outConvergenceFile, index_col=0)
            GRList = dfGRList.values  # convert it to numpy array
        except:
            raise Exception(
                'WARNING: Error occurred in reading ' + outConvergenceFile + ' under DAresults/ folder.')
        if len(GRList) == paramNum:
            plt.plot(range(1, paramNum + 1), GRList, 'b-', label='GR convergence estimator')
            plt.title('GR convergence estimator')
            plt.xlabel('Parameter')
            plt.ylabel('GR estimator')
        else:
            raise Exception(
                'WARNING: The number of GR estimators doesn\'t equal to the number of parameters used in DA. No plot for G-R test.')
        if is_show:
            plt.show()
        else:
            plt.savefig(outDir + '/GR-convergence.png')
            print('****Saving figures: OK (in '+outDir+')****')
    else:
        print('WARNING: convergence file ('+outConvergenceFile+') is not a file. No plots for G-R convergence test')

else:  # a single MCMC chain
    try:
        dfOutC = pd.read_csv(outC, index_col=0)
        c = dfOutC.values  # convert it to numpy array
    except:
        raise Exception('WARNING: Error occurred when reading ' + outC + 'under DAresults/ folder.')
    # histograms for parameters
    plt.ion()
    plt.figure(1)
    for j in range(paramNum):
        plt.subplot(rnpic, cnpic, j + 1)
        plt.hist(c[:, j], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[j])
        plt.tick_params(top='off', right='off')
        plt.legend()
    plt.suptitle('Posterior distributions of parameters')
    if is_show:
        plt.show()
    else:
        plt.savefig(outDir + '/ppdf.png', bbox_inches='tight')  # save figures
        print('****Saving figures: OK (in '+outDir+')****')
    # the 2nd plot: mismatches between observations and simulation
    try:
        dfOut = pd.read_csv(outJ, index_col=0)
        jerror = dfOut.values  # convert it to numpy array
    except:
        raise Exception('WARNING: Error occurred when reading ' + outJ + 'under DAresults/ folder.')
    jnum = range(jerror.shape[0] // 2, jerror.shape[0])  # only show the final 1/2 part
    plt.figure(2)
    plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
    plt.title(
        'Mismatches between observations and simulation outputs during MCMC sampling')
    plt.xlabel('Samples')
    plt.ylabel('Mismatch')
    if is_show:
        plt.show()
    else:
        plt.savefig(outDir + '/mismatch.png')  # save figures
        print('****Saving figures: OK (in '+outDir+')****')
