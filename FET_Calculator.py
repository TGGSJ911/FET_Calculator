#############################################################
# load library
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
from scipy import stats
import os
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')
#############################################################


class Calculator:
    def __init__(self, period, skiprows, channel_width, channel_length, oxideThickness):
        self.data = None
        self.skiprows = skiprows
        self.names = ['Vg', 'Vd', 'Ig', 'Id', 'Is', 'absId', 'absIg']
        self.period = period
        self.W = channel_width
        self.L = channel_length
        self.Cox = float(3.9*8.854*1e-12/(oxideThickness*1e-9))  # F/m^2

    def fileReader(self, folderPath, outputpath):
        folder = folderPath  # 'd1\\f4\\'
        self.csv = []
        mu = []
        on_off_ratio = []
        Vg_range = 0  # where self.data starts
        dir = os.path.join("{}".format(folder))
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file[-1] == 'v':
                    self.csv.append(file)
        for idx, file in enumerate(self.csv[:]):
            rawdata = pd.read_csv(
                '{}\{}'.format(folder, file), skiprows=self.skiprows)  # 259 #########need to fix
            self.data = rawdata.iloc[Vg_range:, 1:8]
            self.data = self.data.apply(pd.to_numeric, errors='coerce')
            self.data.columns = self.names
            self.data.reset_index()
            temp_on_off_ratio = 0
            for i in range(1):
                Vds = -(self.data.iloc[self.period*i, 1:2])  # V
                tempMu = self.getMobility(
                    self.W[idx][0], self.L, Vds, self.Cox, (self.period*i), 'p')
                on_current = self.data.iloc[self.period *
                                            (i+1):self.period*(i+2), 5:6].max().values[0]
                off_current = self.data.iloc[self.period *
                                             (i+1):self.period*(i+2), 5:6].min().values[0]
                temp_on_off_ratio = max(
                    temp_on_off_ratio, abs(on_current/off_current))
                mu.append(tempMu)
            if temp_on_off_ratio < 1e5:
                on_off_ratio.append(temp_on_off_ratio)
            else:
                on_off_ratio.append(0)
        mu_df = pd.DataFrame({'device': self.csv, 'Mobility': mu})
        onOff_df = pd.DataFrame(
            {'device': self.csv, 'On-off-Ratio': on_off_ratio[:]})
        # export
        output_df = pd.DataFrame(
            {'device': self.csv, 'Mobility': mu, 'On-off-Ratio': on_off_ratio[:]})
        # r'C:\Users\GSJ\Desktop\d1\f4\result\result.csv'
        #now = datetime.now()
        #date_time = now.strftime("%m/%d/%Y")
        export = output_df.to_csv(
            '{}\\result.csv'.format(outputpath), index=None, header=True)
        return mu_df, onOff_df

    def plot(self, folder):
        # need to add stop button
        for idx, file in enumerate(self.csv[:]):
            rawdata = pd.read_csv(
                '{}\{}'.format(folder, file), skiprows=self.skiprows)  # 259 #########need to fix
            self.data = rawdata.iloc[0:, 1:8]
            self.data = self.data.apply(pd.to_numeric, errors='coerce')
            self.data.columns = self.names
            self.data.reset_index()
            self.IVPlot(self.data, 1.2, file)

    def monotonicStack(self, nums, chtype):
        # to make sure the slope is always monotonic decreasing for p-type or
        # increasing for n-type
        stack = []
        for i in range(len(nums)):
            if not stack:
                stack.append(nums[i])
            if chtype == 'n' or 'N':
                if stack and stack[-1] > nums[i]:
                    stack.append(nums[i])
            if chtype == 'p' or 'P':
                if stack and stack[-1] > nums[i]:
                    stack.append(nums[i])
        return stack

    def getslope(self, Ids, Vg):
        slopeCollection = []
        for i in range(1, len(Ids)):
            try:
                slope = (Ids[i-1]-Ids[i])/(Vg[i]-Vg[i-1])
                slopeCollection.append(slope)
            except:
                slopeCollection.append(0)
        return max(slopeCollection)

    def getMobility(self, W, L, Vds, Cox, Vg_range, chtype):
        Vg = self.data.iloc[Vg_range:Vg_range +
                            self.period, 0:1].T.values[0]
        Ids = self.data.iloc[Vg_range:Vg_range +
                             self.period, -2].values  # A
        VgIds = pd.DataFrame({'Ids': Ids, 'Vg': Vg})
        # use montonic queue to store only monotonic decreaseing datafor p-type device
        Ids = self.monotonicStack(Ids, chtype)
        Vg_monotone = []
        for current in Ids:
            Vg_monotone.append(
                VgIds.loc[VgIds['Ids'] == current, 'Vg'].iloc[0])
        Vg = Vg_monotone
        mu = self.getslope(Ids, Vg)*L/(Cox*W*Vds).values[0]*1e3
        return mu

    def IVPlot(self, data, scale, title):
        lowVds = data.iloc[:2*self.period, :]
        lowVds_upperbound = data.iloc[:2 *
                                      self.period, 5:6].max().values[0]
        lowVds_lowerbound = data.iloc[:2 *
                                      self.period, 5:6].min().values[0]
        highVds = data.iloc[2*self.period+1:, :]
        highVds_upperbound = data.iloc[2 *
                                       self.period+1:, 5:6].max().values[0]
        highVds_lowerbound = data.iloc[2 *
                                       self.period+1:, 5:6].min().values[0]
        sns.set(font_scale=1)
        sns.set_style('whitegrid')
        fig, ax = plt.subplots(ncols=2, figsize=(6, 6))  # figsize=(6, 6)
        # plt.subplots_adjust(left=0, right=3)
        plt.tight_layout()
        sns.regplot(x='Vg', y='absId', data=data.iloc[:2*self.period, :], scatter_kws={
                    "s": 180}, fit_reg=False, ax=ax[0])
        ax[0].set_title('{}: Vds= {}V'.format(
            title, lowVds['Vd'][0]), fontsize=14)
        ax[0].set_ylim(0, lowVds_upperbound*1.2)
        ax[0].set_xlabel('Vg (V)', fontsize=18)
        ax[0].set_ylabel('Ids (A)', fontsize=18)
        sns.regplot(x='Vg', y='absId', data=data.iloc[2*self.period+1:, :], scatter_kws={
                    "s": 180}, fit_reg=False, ax=ax[1])
        ax[1].set_title('{}: Vds= {}V'.format(
            title, highVds['Vd'][2*self.period+1]), fontsize=14)
        ax[1].set_ylim(0, highVds_upperbound*1.2)
        ax[1].set_xlabel('Vg (V)', fontsize=18)
        ax[1].set_ylabel('Ids (A)', fontsize=18)
        plt.show()
        # need to print out all
