# Setup script for image-photo-z. Assuming a Debian-like operating system.

import os
os.system("reset")

# Let's have some colors and graphics
class echo_colors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

dim=os.popen('stty size', 'r').read().split()
rows=int(dim[0])
cols=int(dim[1])

def hashLine():
	a=''
	for i in range(cols):
		a=a+'#'
	print echo_colors.WARNING+a+echo_colors.ENDC
		
hashLine()
print echo_colors.WARNING+"Welcome to Image Photo-Z."+echo_colors.ENDC
hashLine()
print echo_colors.WARNING+"Before you get started with the package, we need to get some stuff out of the way:\n"+echo_colors.ENDC


# Setup your SDSS-III CasJobs account
while 1:
	flag=raw_input(echo_colors.OKBLUE+"[QUES] Do you have an account on CasJobs? [y/n/q(quit)]: "+echo_colors.ENDC)

	if flag=='q':
		exit(0)
	elif flag=='n':
		import webbrowser
		print echo_colors.WARNING+"[INFO] Create an account on CasJobs at http://skyserver.sdss3.org/CasJobs/CreateAccount.aspx"+echo_colors.ENDC
		gotoCasJobs=raw_input(echo_colors.WARNING+"[INFO] Enter y to be redirected there: "+echo_colors.ENDC)
		if gotoCasJobs=='y':
			webbrowser.open_new("http://skyserver.sdss3.org/CasJobs/CreateAccount.aspx")
			done=raw_input(echo_colors.OKBLUE+"[QUES] Done? Press any key to continue: "+echo_colors.ENDC)
		else:
			exit(0)
	elif flag=='y':
		import getpass
		configTemplate=open("generate_training/CasJobsCL/CasJobs.config.template", "r")
		configLines=configTemplate.readlines()
		configTemplate.close()
		
		configOptions={}

		for line in configLines:
			if line[0]=='#' or line[0]=='\n':
				pass
			else:
				try:
					configOptions[line.split('=')[0]]=line.split('=')[1].rstrip()
				except IndexError:
					pass
		print configOptions

		configOptions['wsid']=raw_input(echo_colors.OKBLUE+"[QUES] You can find your WSID on the top of the page here after signing in: http://skyserver.sdss3.org/CasJobs/changedetails.aspx\n[QUES] Enter your WSID: "+echo_colors.ENDC)
		configOptions['password']=getpass.getpass(echo_colors.OKBLUE+"[QUES] Enter your account password: "+echo_colors.ENDC)
		proxy=raw_input(echo_colors.OKBLUE+"[QUES] Do you use a proxy on your network? [y/n] "+echo_colors.ENDC)
		if proxy=='y':
			configOptions['proxyHost']=raw_input(echo_colors.OKBLUE+"[QUES] Enter proxy hostname: "+echo_colors.ENDC)	
			configOptions['proxyPort']=raw_input(echo_colors.OKBLUE+"[QUES] Enter proxy port: "+echo_colors.ENDC)
			configOptions['proxySet']='true'
		break
	else:
		print echo_colors.FAIL+"[ERR ] That wasn't a valid response. Try again:"+echo_colors.ENDC


# Get global data into your myDB


# Test your SDSS-III CasJobs account
test=raw_input(echo_colors.WARNING+"[INFO] Done setting up account! Press y to test: "+echo_colors.ENDC)
if test=='y':
	# Put test routine here
	pass
