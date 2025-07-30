
import copy
import numpy as np
import pandas as pd
import os
import warnings

import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.mixture import GaussianMixture

showing_all = True

xy = pd.read_excel('C:/Users/User/Desktop/accidents.xlsx')

means_init = np.array(xy.groupby('col')['xx','yy'].mean())

X = np.array(xy[['xx','yy']])

gm = GaussianMixture(n_components=5, random_state=0,means_init=means_init,
                     weights_init=np.array([0.1,0.1,0.1,0.3,0.4])).fit(X)
print(gm.means_)

xy['col1']=gm.predict(X)
print(gm.predict_proba(X)*100)

def plot_color_map( df, name, show_save = True):
    fig, ax = plt.subplots()
    scatter_x = np.array(df.iloc[:,0])
    scatter_y = np.array(df.iloc[:,1])
    group = np.array(df.iloc[:,2])

    for g in np.unique(group):
        i = np.where(group == g)
        ax.scatter(scatter_x[i], scatter_y[i], label=g)
    ax.legend()
    
    if show_save:
        plt.show()
    else:
        fig.savefig(name+'.png')

plot_color_map( xy[['xx','yy','col']], '12_picccture', show_save = False)
plot_color_map( xy[['xx','yy','col1']], '23_picccture', show_save = False)
