#!/usr/bin/python
import string
import re
import dircache
import os.path
import subprocess
import os


def load_flist(sdir,flist):
	list = dircache.listdir(sdir)
	for item in list:
		fqn = ( "%s/%s" % ( sdir, item ))
		if os.path.isfile(fqn) and re.match("[0-9]*.html",item):
			flist[item] = fqn

def do_sub(sdir,flist):
	dlist = dircache.listdir(sdir)
	for item in dlist:
		path = ( "%s/%s" % ( sdir, item))
		if os.path.isdir(path) and re.match("[12][0-9][0-9][0-9]-",item):
			load_flist(path,flist)

def load_drupal(sdir,flist):
	keys = flist.keys()
	keys.sort()
	i=0
	for key in keys:
		i+=1
		fd1 = open(flist[key], 'r')
		farray = fd1.readlines()
		show=0
		findname=1
		findtitle=1
		titlesearch=0
		body=[]
		title=''
		for line in farray:
			# Get the postdate
			if re.search("<I>",line):
				temp = line
				left = string.find(temp,'<I>')+3
				right = string.rfind(temp,'</I>')
				postdate = line[left:right]

			# Get the name of the poster
			if findname and re.search('<B>',line):
				findname = 0
				temp = line
				left = string.find(temp,'<B>')+3
				right = string.rfind(temp,'</B>')
				name = line[left:right]
				titlesearch = 1
				
			# Get the email of the poster
			if titlesearch and re.search('">',line):
				titlesearch=0			
				temp = line
				# left = string.find(temp,title)+len(title)+2
				left = string.find(temp,">")+1
				email = temp[left:].replace(' at ','@').rstrip('\n')

			# Get the Title of the post
			if findtitle and re.search("<TITLE>", line):
				findtitle = 0
				temp = line
				left = string.find(temp,'<TITLE>')+7
				title = line[left:].strip()
				stitle = title.replace('[','\[').replace(']','\]')
			
			if re.match("<!--endarticle-->", line):
				show=0

			# Get the body of the post.
			if show:
				body.append(line)

			if re.match("<!--beginarticle-->", line):
				show=1

		print "Processing:", sdir, "	", key, " - ", name, " - ", email, " - ", title
		fd1.close()
		fd2 = open('/tmp/listservmov', 'w')
		fd2.write( flist[key][:flist[key].find("/")]+'\n' )
		fd2.write( flist[key]+'\n' )
		fd2.write( flist[key][flist[key].rfind("/")+1:]+'\n' )
		fd2.write( postdate+'\n' )
		fd2.write( name+'\n' )
		fd2.write( email+'\n' )
		fd2.write( title+'\n' )
		for line in body:
			fd2.write( line )
		fd2.close()
		cur = os.getcwd()
		os.chdir('/var/www/html/mtest/sites/default')
		p1 = subprocess.call(['/usr/bin/drush', '-u', '1', 'scr', 'drush_mailman'])
		os.chdir(cur)


dlist = dircache.listdir(".")
for dir in dlist:
	if os.path.isdir(dir):
		flist = {}
		do_sub(dir,flist)
		load_drupal(dir,flist)


