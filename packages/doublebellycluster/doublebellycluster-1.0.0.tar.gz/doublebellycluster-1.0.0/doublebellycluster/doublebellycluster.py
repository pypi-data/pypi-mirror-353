
import copy
from sklearn.cluster import DBSCAN
from sklearn.neighbors import KNeighborsClassifier
import itertools
import scipy.spatial.distance

from datetime import datetime, timedelta
from itertools import permutations
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")



def get_inter_dist(df,col):

    r= np.array(df.drop(col, axis = 1))
    dists = scipy.spatial.distance.cdist(r,r)
    distm = pd.DataFrame(dists,
                         index = df.index,
                         columns = df.index)

    colu = df[col].unique()
    colu = [list(items) for items in permutations(colu, r=2)]

    dist_mat_lil=[]
    for i in colu:
        i0 = df.loc[df[col] == i[0]].index.to_list()
        i1 = df.loc[df[col] == i[1]].index.to_list()
        dist_mat_lil += [i+[distm.loc[i0,i1].min().min()]]

    dist_mat_lil = pd.pivot_table(pd.DataFrame(dist_mat_lil),index = 0, columns = 1,values = 2)

    return dist_mat_lil

def flat(ll):
    return list(itertools.chain(*ll))

class Doubleclustering:

    def __init__(self, showing_all = False, eps = 5):
        self.working = True
        self.eps = eps
        self.cut_edge_disjoint = 0.15
        self.showing_all = showing_all

    def d3plot(self, xy):

        xy=xy[['Close']]

        xy.columns = ['f']
        xy[0] = np.arange(len(xy))+1
        
        xy -= xy.min()
        xy /= xy.max()

        xy *= 100
        xy['len']=1

        self.D = 1

        self.fs = xy

        
    def do_fs_beer(self):

        fs = self.fs

        r= np.array(fs[list(range(self.D))])
        d_mat = scipy.spatial.distance.cdist(r,r)
        self.d_mat=d_mat

        eps = fs[range(self.D)].std(0).diff().min()*2

        c = 100
        height = 5
        dbs = DBSCAN(eps= self.eps, min_samples=1)
        fs['l']=-1
        fs['l1']=-1
        while c > 5:

            fs1 = fs.loc[fs.f > c - height]
            dbs = dbs.fit(fs1[range(self.D)])
            fs.loc[fs1.index,'l'] = dbs.labels_

            a_get0 = fs.loc[fs1.index].groupby('l')['l1'].unique().reset_index()
            a_get0['l1'] = a_get0['l1'].map(lambda x: list(x))
            a_get0['1']=a_get0['l1'].map(lambda x: len([i for i in x if i!=-1 ]))
            a_get0 = list(itertools.chain(*a_get0.loc[a_get0['1'] >= 2, 'l1'].to_list()))
            a_get0 = [i for i in a_get0 if i != -1]
            a_get1 = fs.loc[fs1.index].groupby('l1')['l'].count()
            a_get1 = fs.loc[fs1.index].groupby('l1').apply(lambda x: pd.Series({
                'len': x['len'].sum()
                # ,'mind '+str(c): d_mat.loc[x.index, x.index].min().max() + 2 * d_mat.loc[x.index, x.index].min().std()
            }))

            #a_get1 = a_get1.loc[a_get1['len']>50]
            a_get1 = a_get1.drop('len', axis=1)
            a_get1 = a_get1.loc[a_get1.index.isin(a_get0)]

            if len(a_get1) > 0:
                fs = fs.merge(a_get1, on = ['l1'], how = 'left')
                fs['col '+ str(c)] = np.nan
                fs.loc[fs['l1'].isin(a_get1.index),  'col ' + str(c)] = fs.loc[fs['l1'].isin(a_get1.index),'l1']

            fs['l1'] = copy.deepcopy(fs['l'])
            c -= height

        fs = fs.drop(['l','l1'],axis=1)

        self.fs = fs


    def fs_regress_allneed(self):

        fs = self.fs

        d_framedata = fs.iloc[:,self.D + 3:]
        col = d_framedata.columns
        d_framedata = d_framedata[[i for i in col if 'col' in i]]
        for i in range(0,d_framedata.shape[1]-1):
            re = list(d_framedata.iloc[:,i].dropna().index)

            for jj in range(i+1,d_framedata.shape[1]):

                a_var_step1 = list(d_framedata.iloc[re,jj].unique())
                promejutoc_var = d_framedata.iloc[:, jj]
                promejutoc_var[promejutoc_var.isin(a_var_step1)]=np.nan
                d_framedata.iloc[:, jj] = promejutoc_var

        col = d_framedata.columns
        def get_h_done(x):
            x_k = np.where(x >= 0)[0]
            if len(x_k)>0:
                k = min(list(x_k))
                res = [int(col[k].split(' ')[1]), x[k]]
            else:
                res = [np.nan]*2
            return res
        

        det_matrix = pd.DataFrame( np.array( d_framedata.apply(lambda x: get_h_done(x), axis =1).to_list()),
                                  columns = ['level','cl'])
        
        fs = fs.join(det_matrix)
        fs['fin_join'] = det_matrix.astype(str).apply(lambda x: '-'.join(x), axis =1)
        fs = fs.sort_values(['level','cl'])
        fs_to_plot = fs.loc[fs['fin_join']!='nan-nan']

        self.fs = fs
        self.fs_to_plot = fs_to_plot

        

    def do_color_cluster(self):

        fs_to_plot = self.fs_to_plot

        pair_mat_0 = fs_to_plot.groupby('fin_join')[list(range(self.D))].mean()
        
        colt1 = list(fs_to_plot.columns[:self.D])+['fin_join']
        pair_mat_0 = get_inter_dist(fs_to_plot[colt1], 'fin_join')
        pair_mat_0 = pair_mat_0.fillna(0)
        
        dbs = DBSCAN(min_samples=1, metric='precomputed', eps=self.cut_edge_disjoint)
        dd = dbs.fit(pair_mat_0)
        dd=dd.labels_

        while True:
            if len(set(dd))==1:
                dbs = DBSCAN(min_samples=1, metric='precomputed', eps=self.cut_edge_disjoint)
                dd = dbs.fit(pair_mat_0)
                dd=dd.labels_

            else:
                break
            self.cut_edge_disjoint-=0.05

        dd_t0 = [[] for i in range(len(set(dd)))]
        for k,i in enumerate(dd):
            dd_t0[i]+=[pair_mat_0.index[k]]


        fin_class={}
        for i in dd_t0:
            for j in i:
                fin_class[j]=i[0]

        fs_to_plot['fin_join'] = fs_to_plot['fin_join'].map(fin_class)   ##
        self.fs_to_plot = fs_to_plot



    def do_model_clusterspare(self, percentile_cut, xy):

        fs_to_plot = self.fs_to_plot
        fs = self.fs

        fs = fs.drop(['fin_join'],axis=1).merge(fs_to_plot[list(range(self.D))+['fin_join']], on = list(range(self.D)), how = 'left')
        llist = list(fs.loc[fs['fin_join'].isna()==False,'level'].unique()[::-1]) +[0.]
        fs['level'] = fs['f'].map(lambda x: max([i for i in llist if i<= int(x)]))
        for i in llist:
            x = fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()==False)]
            Knn = KNeighborsClassifier(n_neighbors=2)
            Knn.fit(x[list(range(self.D))], x['fin_join'])
            if len(fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()), 'fin_join']):
                fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()), 'fin_join'] = Knn.predict(fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()), list(range(self.D))])

        self.fs = fs

        fs_to_plot = fs.loc[fs['level']>=percentile_cut]

        dd_t = fs_to_plot.sort_values(0)
        
        return dd_t

    def do_ddcluster(self, xy):
        self.d3plot( xy)
        self.do_fs_beer()
        self.fs_regress_allneed()
        dd_t = self.do_model_clusterspare(0, xy)
        return dd_t

    def graph_mother_do_cluster(self, xy):
        self.eps = 5
        xy["fin_join"] = self.do_ddcluster(xy)["fin_join"].to_list()
        self.eps = 3
        xy["fin_join_3"] = self.do_ddcluster(xy)["fin_join"].to_list()
        
        
        x_est = xy.groupby('fin_join_3').apply(lambda x:pd.Series({'end':x['t'].max(),
                                            'delta':(x['t'].max() - x['t'].min()).seconds//60,
                                            'leg':abs(x['Close'].iloc[0]-x['Close'].iloc[-1]),
                                            'hieht':x['Close'].max()-x['Close'].iloc[[0,-1]].max() })).sort_values('end')
        
        x_est = x_est.loc[(x_est.delta<1200)&(x_est.delta>10)]

        time = x_est.end.iloc[-2]
        period= x_est.iloc[1:-1].delta.mean()
        a_var_R_reliable =  [time + timedelta(minutes =i*period) for i in range(4)]
        
        x_est = xy.groupby('fin_join').apply(lambda x:pd.Series({'end':x['t'].max(),
                                            'delta':(x['t'].max() - x['t'].min()).seconds//60,
                                            'leg':abs(x['Close'].iloc[0]-x['Close'].iloc[-1]),
                                            'hieht':(x['Close'].max()-x['Close'].min())/x['Close'].min() })).sort_values('end')
        
        
        return dd_t, a_var_R_reliable,period, x_est

    def hip_high(self, di,eps= 2):

        try:
                
            di['color'] =0

            df=copy.deepcopy(di)

            self.eps = eps
            df["fin_join"] = self.do_ddcluster(df)["fin_join"].to_list()
            x_est = df.groupby('fin_join')['Close'].max().reset_index()
            x_est['max']=1
            df = df.merge(x_est, on=['fin_join','Close'])
            di = di.merge(df[['t','Close','max']], on = ['t','Close'], how='left')

            df=copy.deepcopy(di)
            df['Close']*=-1

            self.eps = eps
            df["fin_join"] = self.do_ddcluster(df)["fin_join"].to_list()
            x_est = df.groupby('fin_join')['Close'].max().reset_index()
            x_est['min']=-1
            df = df.merge(x_est, on=['fin_join','Close'])
            df['Close']*=-1


            di = di.merge(df[['t','Close','min']], on = ['t','Close'], how='left')
            di=di.fillna(0)


            di['color']=di.apply(lambda x: x['max']+ x['min'] if x['max']==1 or x['min']==-1  else 0 ,axis=1)

            di=di.drop(['max','min'],axis=1)

            return di
        except Exception as e:
            print(e)
            return None


        dd_pax=di.loc[di['color']==1]
        dd_pax['cl'] = np.arange(len(dd_pax))
        X = dd_pax[['Close', 'd']]
        y = np.arange(len(dd_pax))
        from sklearn.neighbors import KNeighborsClassifier
        neigh = KNeighborsClassifier(n_neighbors=1)
        neigh.fit(X, y)

        dd=di.loc[di['color']==-1][['Close', 'd']]
        X = dd[['Close', 'd']]
        dd['cl'] = neigh.predict(X)
        dd.columns = ['Close_low', 'd_low','cl']
        dd = dd.groupby('cl')['Close_low'].mean().reset_index()
        dd = dd_pax[['t','Close','cl']].merge(dd, on = 'cl')
        dd['percent_change']=(dd['Close']-dd['Close_low'])/dd['Close_low']
        dd['change']=(dd['Close']-dd['Close_low'])
        
        return dd