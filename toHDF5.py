# Test code to convert data into hdf5 file
#===========================================================
# Groups are like directories; datasets are like files.
# Read data:
# Inspect elements using "i for i in F" (F refers to the file variable)
# If there is a dataset1 in gruop1
# Use "data = F['gruop1/dataset1']" to read data
# Columns in data: u,g,r,i,z,ra,dec,x,y,eu,eg,er,ei,ez
# Attributes in data: 'redshift','redshift_error','class','ObjectX','ObjectY','ID'
# Must use "data.attrs['attribute_name']" to read attributes
#===========================================================

from numpy import *
import h5py
from os import listdir

#obj_columns = 0u,1g,2r,3i,4z,5zs,6ezs,7cls,8ra,9dec,10x,11y,12cenx,13ceny,14eu,15eg,16er,17ei,18ez

dataPath = 'sqd12_1_datan/' #directory path 

F = h5py.File('pixel_test.hdf5','w') #file name 

#cols = ['u','g','r','i','z','zs','ezs','cls','ra','dec','x','y','cenx','ceny','eu','eg','er','ei','ez']
#hdr = F.create_dataset('columns',data=cols)

for i in listdir(dataPath):
	grp = F.create_group(i)
	ALLobjs = genfromtxt(dataPath+i+'/'+i+'.list',dtype='str')
	objs = []
	if i is not 'BACKGROUND':
		for o in ALLobjs:
			tmp = loadtxt(dataPath+i+'/'+o)
			if len(tmp) != 0: objs.append(o)
		numObjs = 0
		for j in objs:
			temp = loadtxt(dataPath+i+'/'+j)
			tempData = transpose([temp[:,0],temp[:,1],temp[:,2],temp[:,3],temp[:,4],temp[:,8],temp[:,9],temp[:,10],\
			temp[:,11],temp[:,14],temp[:,15],temp[:,16],temp[:,17],temp[:,18]])
			dset = grp.create_dataset(str(numObjs),data=tempData,compression='gzip')
			dset.attrs['redshift'] = temp[0,5]
			dset.attrs['redshift_error'] = temp[0,6]
			dset.attrs['class'] = i #temp[0,7]
			dset.attrs['objectX'] = temp[0,12]
			dset.attrs['objectY'] = temp[0,13]
			dset.attrs['ID'] = j[0:19]
			numObjs += 1
	else:
		numObjs = 0
		for j in ALLobjs:
			temp = loadtxt(dataPath+i+'/'+j)
			tempData = transpose([temp[:,0],temp[:,1],temp[:,2],temp[:,3],temp[:,4],temp[:,8],temp[:,9],temp[:,10],\
			temp[:,11],temp[:,14],temp[:,15],temp[:,16],temp[:,17],temp[:,18]])
			dset = grp.create_dataset(str(numObjs),data=tempData,compression='gzip')
			dset.attrs['redshift'] = temp[0,5]
			dset.attrs['redshift_error'] = temp[0,6]
			dset.attrs['class'] = i #temp[0,7]
			dset.attrs['objectX'] = temp[0,12]
			dset.attrs['objectY'] = temp[0,13]
			dset.attrs['ID'] = j[0:9]
			numObjs += 1
			
		

