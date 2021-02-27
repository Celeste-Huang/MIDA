import pandas as pd
import numpy as np
import time
import MIDAmodule


if __name__ == '__main__':
    print('******Welcome to use Model Independent Data Assimilation (MIDA) module (command-line version)******')
    is_success_step1 = 0
    is_success_step2 = 0
    is_success_step3 = 0
    namelistFile='./namelist.txt' # namelist.txt should be in the same folder with MIDA
    print('******Start a MIDA task (Local Time: ' +time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+ ')******')
    mida_case = MIDAmodule.MIDAexp()
    try:
        mida_case.step1(namelistFile, 0)
        is_success_step1 = 1 # success in step 1
    except:
        print('WARNING: Error occurred in step1 (Data preparation).')
    if is_success_step1:
        try:
            # printDA.csv should be in the same folder with MIDA. It indicate what to be print during DA
            try:
                printDA = pd.read_csv('./printDA.csv') # 5 rows, 2 columns
                printList = np.array(printDA[printDA.columns[1]].astype(int).tolist())
            except:
                print('WARNING: Can\'t reading printDA.csv. Now MIDA will print mismatch and acceptRate during DA.')
                printList=[1,1,0,0,0]
            mida_case.step2(printList)
            is_success_step2 = 1 # success in step 2
        except:
            print('WARNING: Error occurred in step 2 (Executation of DA).')
    if is_success_step1 and is_success_step2:
        try:
            mida_case.step3(namelistFile, is_success_step2)
            is_success_step3 = 1 # success in step 1
        except:
            print('WARNING: Error occurred in step 3 (Visualization).')
    if is_success_step1 and is_success_step2 and is_success_step3:
        print('******Succeed to run MIDA (Local Time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ')******')
    else:
        print('******Fail to run MIDA (Local Time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ')******')
    ### wait input to exit MIDA
    input('Please type Enter to exit MIDA:')
def help():
    print('')


