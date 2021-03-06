#!/usr/bin/python

__author__='Alankar Kotwal'

import sys
import os
import time

configOptions={}

try:
	configFile=open(sys.argv[1], "r")
except IndexError:
	configFile=open("config.cfg", "r")
configLines=configFile.readlines()

for line in configLines:
	if line[0]=='#' or line[0]=='\n':
		pass
	else:
		try:
			configOptions[line.split('=')[0]]=line.split('=')[1].rstrip()
		except IndexError:
			pass

if configOptions['USE_MPI']=='yes':
	try:
		from mpi4py import MPI as m
	except ImportError:
		configOptions['USE_MPI']=='no'

catagories=[]
if configOptions['USE_GALAXIES']=='yes':
	catagories.append("GALAXY")
if configOptions['USE_STARS']=='yes':
	catagories.append("STAR")
if configOptions['USE_QSOS']=='yes':
	catagories.append("QSO")

bandsList=configOptions['BANDS']
bands=bandsList.split(',')
	
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/image_registration')
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/generate_training')
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/training')

from image_registration import *
from generate_training import *
from training import *

#os.system("rm -rf data/ data_test/")

start=time.time()

os.system("rm -rf "+configOptions['PROCESSING_DIR'])

try:
	if configOptions['REGENERATE_PIXEL_DATA']=='yes':		
		try:
			os.mkdir(configOptions['PROCESSING_DIR'])
			for i in range(int(configOptions['N_PROCESSORS'])):
				os.mkdir(configOptions['PROCESSING_DIR']+"/"+str(i))
				os.system("cp "+configOptions['IMAGE_PHOTOZ_PATH']+"/generate_training/default_sextr_config/* "+configOptions['PROCESSING_DIR']+"/"+str(i))			
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/GALAXY")
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/STAR")
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/QSO")
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/BACKGROUND")
			os.mkdir(configOptions['TRAINING_IMAGES_DIR'])
		except OSError:
			pass

		preprocess_catalog(configOptions['TRAINING_CATALOG'], configOptions['TRAINING_CATALOG_PROCESSED'])
		
		if configOptions['LOCAL_IMAGES']=='yes':
			pass
		else:
			download_images(configOptions['TRAINING_CATALOG_PROCESSED'], configOptions['TRAINING_IMAGES_DIR'], logfile=configOptions['LOGFILE'])
		if configOptions['LOG_INDEPENDENTLY']=='yes':
			make_logfile(configOptions['TRAINING_CATALOG_PROCESSED'])

		logfile=open(configOptions['LOGFILE'], "r")
		logfileLines=logfile.readlines()
		logfile.close()
		
		def generate_training_data(argsList): # args is a list [iden, configOptions, jobID]
			for args in argsList:
				for band in bands:
					os.system("cp "+args[1]['TRAINING_IMAGES_DIR']+"/"+args[0]+"-"+band+".fits "+args[1]['PROCESSING_DIR']+"/"+str(args[2]))
				list_in=[]
				images_list=[]
				int_error_image_list=[]
				error_image_list=[]
				sex_image_list=[]
				seg_image_list=[]
				sexConfigFiles=[]
				ref_image=args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+"-r.fits"
				for band in bands:
					list_in.append(args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+"-"+band+".fits")
					images_list.append(args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+"-"+band+"_reg.fits")
					int_error_image_list.append(args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+"-"+band+"_error_int.fits")
					error_image_list.append(args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+"-"+band+"_error.fits")
					sex_image_list.append(args[0]+"-"+band+"_reg.fits")
					seg_image_list.append(args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+band+"_seg.fits")
					sexConfigFiles.append(band+".sex")
				register_reproject_with_errors(list_in, images_list, int_error_image_list, error_image_list, ref_image, args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/", headerName=args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+".hdr")
				convert_catalog_to_exp_pixels(ref_image, args[1]['TRAINING_CATALOG_PROCESSED'], args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/sky.list")
				sextract(sex_image_list, sexConfigFiles, args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/")
				for catagory in catagories:
					#print catagory
					generate_training_objects(args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/ref.cat", args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/ref.fits", args[1]['TRAINING_CATALOG_PROCESSED'], images_list, error_image_list, catagory, args[1]['TRAINING_CLASSIFIED_DATA_DIR'])
				if args[1]['USE_BACKGROUND']=='yes':
					#print "BACKGROUND"
					generate_training_background(seg_image_list, images_list, error_image_list, args[1]['TRAINING_CLASSIFIED_DATA_DIR'])
				if args[1]['REMOVE_INTERMEDIATE_IMAGES']=='yes':
					os.system("rm "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.fits "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.cat "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.hdr "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.list")
				else:
					try:
						os.mkdir(args[1]['INTERMEDIATE_TRAINING_FILES'])
					except OSError:
						pass
					for band in bands:
						os.system("mv "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+"-"+band+"_reg.fits "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/"+args[0]+"-"+band+"_error.fits "+args[1]['INTERMEDIATE_TRAINING_FILES'])
						#os.system("rm "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.fits "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.cat "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.hdr "+args[1]['PROCESSING_DIR']+"/"+str(args[2])+"/*.list")
				if args[1]['TIME']=='yes':
					print (time.time()-start)/60
				pass

		logfileLinesSplit=[]
		length=len(logfileLines)
		proc=int(configOptions['N_PROCESSORS'])
		for i in range(proc):
			logfileLinesSplit.append(logfileLines[(i*length/proc):((i+1)*length/proc)])
		
		argsList=[]
		for i in range(proc):
			oneProcArg=[]
			for j in logfileLinesSplit[i]:
				oneProcOneArg=[j.rstrip(),configOptions,i]
				oneProcArg.append(oneProcOneArg)
			argsList.append(oneProcArg)

        try:
            commTrain=m.COMM_WORLD
            ids=commTrain.scatter(argsList, root=0)
            generate_training_data(ids)
        except:
            generate_training_data(oneProcArg)

		#**************************
		# Training has ended here.*
		#**************************

	if configOptions['CLEAN_AFTER_DONE']=='yes':
		os.system("rm -rf "+configOptions['PROCESSING_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TESTING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CATALOG_PROCESSED']+" "+configOptions['TESTING_CATALOG_PROCESSED'])
		os.system("rm -rf "+configOptions['LOGFILE'])
		os.system("rm -rf "+configOptions['TRAINING_DATA_FILE']+" "+configOptions['TRAINING_TARGET_FILE']+" "+configOptions['TESTING_DATA_FILE']+" "+configOptions['TESTING_TARGET_FILE']+" "+configOptions['TESTING_PREDICTION_FILE'])

	if configOptions['REMOVE_IMAGES_AFTER_DONE']=='yes':
		os.system("rm -rf "+configOptions['TRAINING_IMAGES_DIR'])
		os.system("rm -rf "+configOptions['TESTING_IMAGES_DIR'])

	if configOptions['TIME']=='yes':
		end=time.time()
		print end-start
	
except KeyboardInterrupt:
	if configOptions['CLEAN_ON_INTERRUPT']=='yes':
		os.system("rm -rf "+configOptions['PROCESSING_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TESTING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CATALOG_PROCESSED']+" "+configOptions['TESTING_CATALOG_PROCESSED'])
		os.system("rm -rf "+configOptions['LOGFILE'])
		os.system("rm -rf "+configOptions['TRAINING_DATA_FILE']+" "+configOptions['TRAINING_TARGET_FILE']+" "+configOptions['TESTING_DATA_FILE']+" "+configOptions['TESTING_TARGET_FILE']+" "+configOptions['TESTING_PREDICTION_FILE'])
		os.system("rm -rf "+configOptions['KNN_OUTPUT_FILE'])

	if configOptions['REMOVE_IMAGES_ON_INTERRUPT']=='yes':
		os.system("rm -rf "+configOptions['TRAINING_IMAGES_DIR'])
		os.system("rm -rf "+configOptions['TESTING_IMAGES_DIR'])
