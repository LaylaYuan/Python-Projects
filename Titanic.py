import json
import numpy as np
import matplotlib.pyplot as plt
import random
from sklearn.preprocessing import MinMaxScaler
import scipy.spatial.distance as distance

f = open("titanic.json","r")
d = json.load(f)
#print d[0].values()

Data = np.zeros((len(d),6))
for i in range(len(d)):
    if d[i]['Age'] == '':  
        Data[i][0] = None   
    else:
        Data[i][0] = float(d[i]['Age'])
    if d[i]['Fare'] == '':
        Data[i][1] = None
    else:
        Data[i][1] = float(d[i]['Fare'])
    Data[i][2]=float(d[i]['SiblingsAndSpouses'])+float(d[i]['ParentsAndChildren'])
    if d[i]['Embarked'] == '':
        Data[i][3] = None
    elif d[i]['Embarked'] == 'C':
        Data[i][3] = 1.0
    elif d[i]['Embarked'] == 'Q':
        Data[i][3] = 2.0
    elif d[i]['Embarked'] == 'S':
        Data[i][3] = 3.0
    if d[i]['Sex'] == '':
        Data[i][4] = None
    elif d[i]['Sex'] == 'male':
        Data[i][4] = 0.0
    elif d[i]['Sex'] == 'female':
        Data[i][4] = 1.0
    Data[i][5] = float(d[i]['Survived'])
#print Data

# delete missing values
Clean_Data = []
for row in Data:
    NAN = 0
    for i in range(len(row)):
        if np.isnan(row[i]):
            NAN += 1
    if NAN == 0:
        Clean_Data.append(row)
Clean_Data = np.array(Clean_Data)
#print Clean_Data


from sklearn import cluster
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

#normalize the data 	
def normalization(X,max_X,min_X):
    X = (X-min_X)/(max_X - min_X)
    return X

for i in range(len(Clean_Data[0])):
    Clean_Data[:,i] = normalization (Clean_Data[:,i],np.max(Clean_Data[:,i]),np.min(Clean_Data[:,i]))

#split features and targets
Feature = []
Target = []
for line in Clean_Data:
    Feature.append(line[:5])
    Target.append(line[-1])
#print Feature
Feature = np.array(Feature)

Z = linkage(Feature,method='ward',metric='euclidean')
dendrogram(Z,leaf_rotation=90, leaf_font_size=2)

plt.title('hierarchical clustering dendrogram')
plt.xlabel('sample index')
plt.ylabel('distance')
plt.axhline(y=10, color='black')
plt.show()
print 'WE chose distance = 10 as threshold, where k = 3'

centroids = []#randomly initialize three threshold
i = 0
k = 3
while i < k:
	centroids.append(Feature[random.randint(0,Feature.shape[0])])
	i += 1

#print centroids

def _converged(old_centriods, centroids):
		# if centroids not changed, we say 'converged'
		set1 = set([tuple(c) for c in old_centriods])
		set2 = set([tuple(c) for c in centroids])
		return (set1 == set2)

converged = False

names = ['Age','Fare','Companion Count','Embarked','Sex']
j = 0
while converged == False:
#calculate the distance between each point and threshold
	old_centriods = np.copy(centroids)
	Cluster1 = []
	Cluster2 = []
	Cluster3 = []
	for i in range(len(Feature)):
		Distance1 = distance.euclidean(Feature[i], centroids[0])
		Distance2 = distance.euclidean(Feature[i], centroids[1])
		Distance3 = distance.euclidean(Feature[i], centroids[2])
		if min(Distance1,Distance2,Distance3) == Distance1:
			Cluster1.append(Clean_Data[i])
		elif min(Distance1,Distance2,Distance3) == Distance2:
			Cluster2.append(Clean_Data[i])
		elif min(Distance1,Distance2,Distance3) == Distance3:
			Cluster3.append(Clean_Data[i])

	Cluster1 = np.array(Cluster1)
	Cluster2 = np.array(Cluster2)
	Cluster3 = np.array(Cluster3)
	centroids = []
	#recompute the center centroids
	centroids.append([np.mean(Cluster1[:, 0]), np.mean(Cluster1[:, 1]), np.mean(Cluster1[:, 2]), np.mean(Cluster1[:, 3]), np.mean(Cluster1[:, 4])])
	centroids.append([np.mean(Cluster2[:, 0]), np.mean(Cluster2[:, 1]), np.mean(Cluster2[:, 2]), np.mean(Cluster2[:, 3]), np.mean(Cluster2[:, 4])])
	centroids.append([np.mean(Cluster3[:, 0]), np.mean(Cluster3[:, 1]), np.mean(Cluster3[:, 2]), np.mean(Cluster3[:, 3]), np.mean(Cluster3[:, 4])])
	#print centroids
	#check whether the centriods will change or not
	converged = _converged(old_centriods,centroids)
	print 'Now after',j,'times iteraton, the converged is',converged
	
	#if j == 0 or j == 5 or j == 10 or j == 100 or converged:
	
	
	if j == 0 or j == 5 or j == 10 or j == 100 or converged:
		n = 1
		for i in range(0, 5):
			for m in range(0, 5):
				if i < m:
					plt.subplot(2,5,n)
					print 'now i is,',i,'m is,',m
					for a in range(0,len(Cluster1)):
						if Cluster1[a][5]==1.:
							plt.plot(Cluster1[:,i], Cluster1[:,m], 'b.')
						else:
							plt.plot(Cluster1[:,i], Cluster1[:,m], 'g.')
					for a in range(0,len(Cluster2)):
						if Cluster2[a][5]==1.:
							plt.plot(Cluster2[:,i], Cluster2[:,m], 'b.')
						else:
							plt.plot(Cluster2[:,i], Cluster2[:,m], 'g.')
					for a in range(0,len(Cluster3)):
						if Cluster3[a][5]==1.:
							plt.plot(Cluster3[:,i], Cluster3[:,m], 'b.')
						else:
							plt.plot(Cluster3[:,i], Cluster3[:,m], 'g.')
				
					plt.plot(centroids[0][i], centroids[0][m], 'x',label='centroid 1',color='red')
					plt.plot(centroids[1][i], centroids[1][m], 'x',label='centroid 2', color='m')
					plt.plot(centroids[2][i], centroids[2][m], 'x',label='centroid 3', color='y')
					#plt.title(names[i] + ' vs. ' + names[m])
					plt.xlabel(names[i])
					plt.ylabel(names[m])
					
					#plt.savefig('%s_vs_%s_%i.png' % (names[i], names[k], j))
					#plt.clf()
					n += 1
		# # plt.savefig('Q1b.iteration_%s.png' % j)
		# # plt.clf()
		plt.legend()
		plt.show()
	

					# plt.plot(Cluster1[:, i], Cluster1[:, k], 'gx')
					# plt.plot(Cluster2[:, i], Cluster2[:, k], 'bx')
					# plt.plot(Cluster3[:, i], Cluster3[:, k], 'kx')	
					# plt.show()
	j += 1

		
