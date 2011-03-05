#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fabian Ehrentraud, 2011-03-05
# e0725639@mail.student.tuwien.ac.at
# https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
# Licensed under the Open Software License (OSL 3.0)
# Scrapes Uni and TU websites for LVAs from Informatikdidaktik and stores them in an XML
# needs Python 2.7 and library lxml

import datetime
from collections import OrderedDict
from lxml import etree
from lxml import html
import difflib
import urllib
import os.path


#TODO
# make replacement rules more transparent and encapsulated
# cache old semesters which will not change anymore and don't read them in
# when finally Tiss is updated to allow searching for old semesters' LVAs of a certain study code, incorporate the according scraping
# Interdisziplinäres Praktikum: Interaktionsdesign is wrongly assigned in Tiss (not to all according modules), fix this
# update date in an existing lva when any content has changed?


studyname = "Informatikdidaktik"

xmlfilename = "informatikdidaktik.xml"
xmlcomment = "\nFabian Ehrentraud, 2011\ne0725639@mail.student.tuwien.ac.at\nhttps://github.com/fabb/Informatikdidaktik-Studienplan-Scraping\n"
xsd = "stpl_collection.xsd"
xslt = "informatikdidaktik.xslt"
xmlRootname = "stpl_collection"

rss_xslt = "informatikdidaktik_rss.xslt"
rss_xml = "informatikdidaktik_rss.xml"

tiss = "https://tiss.tuwien.ac.at/curriculum/curriculumVersion.xhtml?locale=de&studyCode=066950&version=2009U.0"

uniSemesterFrom = ("2009","W") #Informatikdidaktik exists since 2009W
#uniSemesterTo = ("2011","S") #use default currentSemester()
uni = "Uni"
tu = "TU"

legacyFile = "http://web.student.tuwien.ac.at/~e0725639/informatikdidaktik/informatikdidaktik_tuwel_legacy_2010-09-02.txt"



""" create xml """

def makeRoot(rootname=xmlRootname, schema=xsd, comment=xmlcomment, xsltstylesheet=xslt):
	#creates an stpl xml with xslt PI
	root = etree.Element(rootname, nsmap={"xsi": "http://www.w3.org/2001/XMLSchema-instance"}, attrib={"{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": schema})
	#root.append( etree.Element("child1") )

	# root.insert(0, etree.Element("child0"))
	# root.text = "TEXT"

	#root.getparent().insert(0, etree.Comment("\nFabian Ehrentraud, 2011\ne0725639@mail.student.tuwien.ac.at\n"))
	root.addprevious(etree.Comment(comment))

	root.addprevious(etree.PI("xml-stylesheet", 'type="text/xsl" href="%s"'%(xsltstylesheet)))

	return(root)

def getStpl(xml_root, lva_stpl,lva_stpl_version, lva_stpl_url="", createNonexistentNodes=False):
	#gets the given stpl in the xml or creates it

	#stpl_s = xml_root.xpath('stpl')
	stpl_s = xml_root.findall("stpl")
	for s in stpl_s:
		#print(etree.tostring(s))
		stplB = fuzzyEq(lva_stpl, s.find("title").text)
		stpl_versionB = fuzzyEq(lva_stpl_version, s.find("version").text)

		if(stplB and stpl_versionB):
			if lva_stpl_url: #does not let through ""
				#insert url after version (or title if it does not exist)
				if s.find("url") is not None:
					stpl_url_ = s.find("url")
				else:
					previous = s.find("version") if s.find("version") is not None else s.find("title")
					stpl_url_ = etree.Element("url")
					previous.addnext(stpl_url_)
				stpl_url_.text = lva_stpl_url.strip()
				
			return(s) #return first matching

	if createNonexistentNodes:
		stpl = etree.SubElement(xml_root, "stpl")
		stpl_title_ = etree.SubElement(stpl, "title")
		stpl_title_.text = (lva_stpl or "").strip()
		stpl_version_ = etree.SubElement(stpl, "version")
		stpl_version_.text = (lva_stpl_version or "").strip()
		stpl_url_ = etree.SubElement(stpl, "url")
		stpl_url_.text = (lva_stpl_url or "").strip()

		return(stpl)
	else:
		raise Exception("STPL %s %s not found"%(lva_stpl,lva_stpl_version))

def getModulgruppe(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe, createNonexistentNodes=False):
	#gets the given modulgruppe in the xml or creates it
	stpl = getStpl(xml_root, lva_stpl,lva_stpl_version, lva_stpl_url="", createNonexistentNodes=createNonexistentNodes)

	#modulgruppe_s = stpl.xpath('modulgruppe')
	modulgruppe_s = stpl.findall("modulgruppe")
	for m in modulgruppe_s:
		#print(etree.tostring(m))
		modulgruppeB = fuzzyEq(lva_modulgruppe, m.find("title").text)

		if(modulgruppeB):
			return(m) #return first matching

	if createNonexistentNodes:
		modulgruppe = etree.SubElement(stpl, "modulgruppe")
		modulgruppe_title_ = etree.SubElement(modulgruppe, "title")
		modulgruppe_title_.text = (lva_modulgruppe or "").strip()
	
		return(modulgruppe)
	else:
		#print("Modulgruppe %s not found"%(lva_modulgruppe))
		raise Exception("Modulgruppe %s not found"%(lva_modulgruppe))

def getModul(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul, createNonexistentNodes=False):
	#gets the given modul in the xml or creates it
	modulgruppe = getModulgruppe(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe, createNonexistentNodes)

	#modul_s = modulgruppe.xpath('modul')
	modul_s = modulgruppe.findall("modul")
	for m in modul_s:
		#print(etree.tostring(m))
		modulB = fuzzyEq(lva_modul, m.find("title").text)

		if(modulB):
			return(m) #return first matching

	if createNonexistentNodes:
		modul = etree.SubElement(modulgruppe, "modul")
		modul_title_ = etree.SubElement(modul, "title")
		modul_title_.text = (lva_modul or "").strip()
	
		return(modul)
	else:
		raise Exception("Modul %s not found"%(lva_modul))

def getFach(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects, createNonexistentNodes=False):
	#gets the given fach in the xml or creates it
	modul = getModul(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul, createNonexistentNodes)

	#fach_s = modul.xpath('fach')
	fach_s = modul.findall("fach")
	for f in fach_s:
		#print(etree.tostring(f))
		fachB = fuzzyEq(lva_fach, f.find("title").text)
		fach_typeB = fuzzyEq(lva_fach_type, f.find("type").text)
		#fach_swsB = fuzzyEq(lva_fach_sws, f.find("sws").text)
		#fach_ectsB = fuzzyEq(lva_fach_ects, f.find("ects").text)

		if(fachB and fach_typeB): #ignore sws and ects
		
			#update ects and sws - they must already exist
			fach_sws_ = f.find("sws")
			fach_sws_.text = (lva_fach_sws or "").strip().replace(",",".")
			if len(fach_sws_.text) == 1:
				fach_sws_.text += ".0"
			fach_ects_ = f.find("ects")
			fach_ects_.text = (lva_fach_ects or "").strip().replace(",",".")
			if len(fach_ects_.text) == 1:
				fach_ects_.text += ".0"
			
			return(f) #return first matching

	if createNonexistentNodes:
		fach = etree.SubElement(modul, "fach")
		fach_title_ = etree.SubElement(fach, "title")
		fach_title_.text = (lva_fach or "").strip()
		fach_type_ = etree.SubElement(fach, "type")
		fach_type_.text = (lva_fach_type or "").strip()
		fach_sws_ = etree.SubElement(fach, "sws")
		old_fach_sws = fach_sws_.text
		fach_sws_.text = (lva_fach_sws or "").strip().replace(",",".")
		if len(fach_sws_.text) == 1:
			fach_sws_.text += ".0"
		fach_ects_ = etree.SubElement(fach, "ects")
		old_fach_sws = fach_sws_.text
		fach_ects_.text = (lva_fach_ects or "").strip().replace(",",".")
		if len(fach_ects_.text) == 1:
			fach_ects_.text += ".0"
		
		if old_fach_sws != fach_sws_.text or old_fach_ects != fach_ects_.text: #TODO more than just SWS and ECTS
			print("Fach updated: %s"%(fach_title_.text + " " + fach_type_.text + " " + fach_sws_.text + " " + fach_ects_.text))

		print("New Fach: %s"%(fach_title_.text + " " + fach_type_.text + " " + fach_sws_.text + " " + fach_ects_.text))

		return(fach)
	else:
		raise Exception("Fach %s %s (%s %s) not found"%(lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects))


def getMatchingFach(xml_root, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects):
	#searches a matching fach anywhere in the given xml
	#for legacy files, no need to provide lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul
	
	fach_s = xml_root.xpath('//fach')
	for f in fach_s:
		#print(etree.tostring(f))
		fachB = fuzzyEq(lva_fach, f.find("title").text)
		fach_typeB = fuzzyEq(lva_fach_type, f.find("type").text, threshold=1.0)
		#fach_swsB = fuzzyEq(lva_fach_sws, f.find("sws").text)
		#fach_ectsB = fuzzyEq(lva_fach_ects, f.find("ects").text)

		if(fachB and fach_typeB): #ignore sws and ects
			return(f) #return first matching

	raise Exception("Fach %s %s (%s %s) not found"%(lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects))

def addLva(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects,lva_university,lva_semester,lva_title,lva_key,lva_type,lva_sws,lva_ects,lva_info,lva_url, lva_professor=None, createNonexistentNodes=False, searchMatchingFach=False):
	""" adds an lva to the given xml """
	
	if searchMatchingFach:
		fach = getMatchingFach(xml_root, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
	else:
		fach = getFach(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects, createNonexistentNodes)
	
	#for non-given lva_ects, search from fach
	lva_ects = lva_ects or fach.find("ects").text

	found_lva = None
	#lva_s = fach.xpath('lva')
	lva_s = fach.findall("lva")
	for l in lva_s:
		#print(etree.tostring(f))
		universityB = fuzzyEq(lva_university, l.find("university").text)
		semesterB = fuzzyEq(lva_semester, l.find("semester").text)
		titleB = fuzzyEq(lva_title, l.find("title").text)
		keyB = fuzzyEq(lva_key, l.find("key").text)
		typeB = fuzzyEq(lva_type, l.find("type").text, threshold=1.0)
		#swsB = fuzzyEq(lva_sws, l.find("sws").text, threshold=0.0)
		#ectsB = fuzzyEq(lva_ects, l.find("ects").text, threshold=0.0)
		#infoB = fuzzyEq(lva_info, l.find("info").text, threshold=0.0)
		#urlB = fuzzyEq(lva_url, l.find("url").text, threshold=0.0)
		#professorB = fuzzyEq(lva_professor, l.find("professor").text, threshold=0.0)
		if(universityB and semesterB and titleB and keyB and typeB): # ignore sws, ects, info, url and prof
			found_lva = l
			break #return first matching
			#return(l)

	#lva = found_lva or etree.SubElement(fach, "lva") #or: update existing lva #__nonzero__ will be changed in ElementTree
	lva = found_lva if found_lva is not None else etree.SubElement(fach, "lva") #or: update existing lva #__nonzero__ will be changed in ElementTree
	#lva_university_ = lva.find("university") or etree.SubElement(lva, "university") #or: update existing subelement #__nonzero__ will be changed in ElementTree
	lva_university_ = lva.find("university") if lva.find("university") is not None else etree.SubElement(lva, "university")
	lva_university_.text = (lva_university or "").strip()
	lva_semester_ = lva.find("semester") if lva.find("semester") is not None else etree.SubElement(lva, "semester")
	lva_semester_.text = (lva_semester or "").strip()
	lva_title_ = lva.find("title") if lva.find("title") is not None else etree.SubElement(lva, "title")
	lva_title_.text = (lva_title or "").strip()
	lva_key_ = lva.find("key") if lva.find("key") is not None else etree.SubElement(lva, "key")
	lva_key_.text = (lva_key or "").strip()
	lva_type_ = lva.find("type") if lva.find("type") is not None else etree.SubElement(lva, "type")
	lva_type_.text = (lva_type or "").strip()
	lva_sws_ = lva.find("sws") if lva.find("sws") is not None else etree.SubElement(lva, "sws")
	old_lva_sws = lva_sws_.text
	lva_sws_.text = (lva_sws or "").strip().replace(",",".")
	if len(lva_sws_.text) == 1:
		lva_sws_.text += ".0"
	lva_ects_ = lva.find("ects") if lva.find("ects") is not None else etree.SubElement(lva, "ects")
	old_lva_ects = lva_ects_.text
	lva_ects_.text = (lva_ects or "").strip().replace(",",".")
	if len(lva_ects_.text) == 1:
		lva_ects_.text += ".0"
	lva_info_ = lva.find("info") if lva.find("info") is not None else etree.SubElement(lva, "info")
	if "manuell" in (lva_info_.text or ""):
		print("Manually registered LVA overwritten")
		found_lva = None #to print out LVA details in the end of the function and update the query date
	lva_info_.text = (lva_info or "").strip()
	lva_url_ = lva.find("url") if lva.find("url") is not None else etree.SubElement(lva, "url")
	lva_url_.text = (lva_url or "").strip()
	lva_professor_ = lva.find("professor") if lva.find("professor") is not None else etree.SubElement(lva, "professor")
	lva_professor_.text = (lva_professor or "").strip()
	
	#TODO this does not update the query date if some fields of an existing lva are updated. but would that be wanted?
	if found_lva is None or lva.find("query_date") is None:
		lva_query_date_ = lva.find("query_date") if lva.find("query_date") is not None else etree.SubElement(lva, "query_date")
		lva_query_date_.text = datetime.datetime.now().isoformat()
	
	if old_lva_sws != lva_sws_.text or old_lva_ects != lva_ects_.text: #TODO more than just SWS and ECTS
		print("LVA updated: %s"%(lva_university_.text + " " + lva_semester_.text + " " + lva_title_.text + " " + lva_key_.text + " " + lva_type_.text + " " + lva_sws_.text + " " + lva_ects_.text + " " + lva_info_.text + " " + lva_professor_.text))
	
	if found_lva is None:
		print("New LVA: %s"%(lva_university_.text + " " + lva_semester_.text + " " + lva_title_.text + " " + lva_key_.text + " " + lva_type_.text + " " + lva_sws_.text + " " + lva_ects_.text + " " + lva_info_.text + " " + lva_professor_.text))
	"""
	else: #FIXME only for debugging
		raise Exception("Existing LVA: %s"%(lva_university_.text + " " + lva_semester_.text + " " + lva_title_.text + " " + lva_key_.text + " " + lva_type_.text + " " + lva_sws_.text + " " + lva_ects_.text + " " + lva_info_.text + " " + lva_professor_.text))
	"""

	return(lva)

def addSource(xml_root, url, query_date):
	#adds an url source entry in the given xml
	
	found_source = None
	source_s = xml_root.findall("source")
	for s in source_s:
		if(s.find("url").text == url):
			found_source = s
			#print("found source: " + s.find("url").text)
			break #return first matching
		#print("source " + url + " not matching to " + s.find("url").text)

	if found_source is not None: #__nonzero__ will be changed in ElementTree
		source = found_source
	else:
		source = etree.Element("source")
		xml_root.insert(0, source)
		url_ = source.find("url") if source.find("url") is not None else etree.SubElement(source, "url")
		url_.text = (url or "")
	
	query_date_ = etree.SubElement(source, "query_date")
	query_date_.text = (query_date or "")

def checkSchema(xml_root, xsd=xsd):
	#checks whether the given xml is correct according to the schema
	
	#TODO extract schema from xml
	
	xmlschema_doc = etree.parse(xsd)
	xmlschema = etree.XMLSchema(xmlschema_doc)

	#print(xmlschema.validate(doc))
	try:
		xmlschema.assertValid(xml_root)
		return(True)
	except etree.DocumentInvalid:
		print(xmlschema.error_log)
		return(False)

def writeXml(xml_root, filename=xmlfilename):
	#writes xml to the given filename
	
	print("Writing XML file " + filename + " + backups")
	
	xml = etree.tostring(xml_root.getroottree(), pretty_print=True, xml_declaration=True, encoding="utf-8")

	#print(xml) #unicode problem
	
	writedate = str(datetime.datetime.now()).replace(":",".").replace(" ","_")

	basename, extension = os.path.splitext(filename)
	
	#backup of original if it exists
	if os.path.exists(filename):
		os.rename(filename, basename + "_" + writedate + "_old" + extension)
	
	#write new
	f = open(filename, 'w')
	f.write(xml)
	f.close()
	
	#write backup of new
	f = open(basename + "_" + writedate + extension, "w")
	f.write(xml)
	f.close()

def readXml(filename, checkXmlSchema=False):
	
	print("Reading in existing XML file " + filename)
	
	parser = etree.XMLParser(remove_blank_text=True) #read in a pretty printed xml and don't interpret whitespaces as meaningful data => this allows correct output pretty printing
	xml_root = etree.parse(filename, parser).getroot()

	#print(etree.tostring(xml_root))
	
	if checkXmlSchema:
		if not checkSchema(xml_root):
			raise Exception("Verifying XML Schema failed")
	
	return(xml_root)

def loadXml(xmlfilename, xmlRootname=xmlRootname, xsd=xsd, loadExisting=True, checkXmlSchema=False):
	#open existing file if it exists or create new xml
	#check xml only when file is opened
	if loadExisting and os.path.exists(xmlfilename):
		#open existing file
		return(readXml(xmlfilename, checkXmlSchema))
	else:
		#create xml
		return(makeRoot(xmlRootname, xsd))

def isFreshXml(xml_root):
	#true if xml already contains study structure
	if xml_root.find("stpl") is None:
		return True
	else:
		return False

""" generate rss """


def transformXslt(xml_root, xsltfilename=rss_xslt):
	xslt_root = readXml(xsltfilename)
	transform = etree.XSLT(xslt_root)
	return(transform(xml_root).getroot())

def generateRss(xml_root, rssfilename=rss_xml):
	result_tree = transformXslt(xml_root)
	writeXml(result_tree, rssfilename)


""" fuzzy matching """

def fuzzyEq(wantedStr, compStr, threshold=0.89): #FIXME
	#compares the two strings for approximate equalness
	
	#"E-Tutoring, Moderation von E-Learning" vs "eTutoring, Moderation von e-Learning" => ratio of 0.93
	#"Experimentelle Gestaltung von MM-Anwendungen + Präsentationsstrategien 1" vs "(4) Experiment. Gestaltung von MM-Anwend. + Präsentationsstrategien 1"  => ratio of 0.895
	#"Experimentelle Gestaltung von MM-Anwendungen + Präsentationsstrategien 2", "(4) Experiment. Gestaltung von MM-Anwend. + Präsentationsstrategien 1" => ratio of 0.88
	
	wantedStr = (wantedStr or "").strip().lower()
	compStr = (compStr or "").strip().lower()
	
	#warning: lvas "Unterrichtspraktikum Informatikdidaktik 1" and "Unterrichtspraktikum Informatikdidaktik 2" are both for fach "Unterrichtspraktikum Informatikdidaktik"
	fixes_wanted = ["(1)","(2)","(3)","(4)","seminar 1","seminar 2","logik","systeme 1","systeme 2"] #(1)-(4) could lead to problems if those lvas were provided by Uni which does not categorize into fach
	for f in fixes_wanted:
		if f in wantedStr and f not in compStr: #but NOT the other way around
			return(False)

	#warning: "Knowledge Management" does not fit to "Knowledge Management im Bildungsbereich"
	fixes_comp = ["bildungsbereich"]
	for f in fixes_comp:
		if f in compStr and f not in wantedStr: #but NOT the other way around
			return(False)
	
	if wantedStr in compStr or compStr in wantedStr: #FIXME does not take account for spelling errors
		return(True)
	
	subfach = compStr.split('"')
	if len(subfach) > 1:
		subfach1 = subfach[1]
		subfach2 = subfach[3]
		return(difflib.SequenceMatcher(None, subfach1, wantedStr).ratio() >= threshold or difflib.SequenceMatcher(None, subfach2, wantedStr).ratio() >= threshold)
	
	#return(wantedStr.strip() == compStr.strip())
	return(difflib.SequenceMatcher(None, wantedStr, compStr).ratio() >= threshold)



""" uni scrape """

def srange((from_year,from_semester),(to_year,to_semester)):
	#generates a list of the semesters in the range from-to, sorted chronologically, format ["W2009","S2010",..]
	ws = ["S","W"]
	try:
		y_f = int(from_year)
		y_t = int(to_year)
		if not from_semester in ws or not to_semester in ws:
			raise Exception()
	except (TypeError, ValueError, OverflowError, Exception): #int conversion failed
		return([])

	yy = range(y_f,y_t+1)

	combin = [(str(y),s) for y in yy for s in ws]
	
	try:
		if from_semester == ws[1]:
			combin.pop(0)
		if to_semester == ws[0]:
			combin.pop()
	except IndexError:
		return([])
	
	return(combin)

def currentSemester():
	#calculates the current semester - from january on, the following summer semester will be output, from july on, the following winter semester
	year = datetime.datetime.now().year
	month = datetime.datetime.now().month
	current_year = str(year)
	current_sem = "S" if month < 7 else "W"
	#TODO this gets the summer courses in january which might be a bit late
	return(current_year,current_sem)

def getUniUrls((from_year,from_semester)=uniSemesterFrom, (to_year,to_semester)=currentSemester()):
	#builds urls of websites with all studies of the given semester range
	uniurl = "http://online.univie.ac.at/vlvz?fakultaet=-1&semester=%s"
	urls = OrderedDict([(sem,uniurl%(''.join(sem[::-1]))) for sem in srange((from_year,from_semester),(to_year,to_semester))])
	return(urls)

def fetchUrl(url, studyname=studyname):
	#gets the url in the <a> tag that is next to the studyname
	
	print("Querying %s"%(url))
	
	doc = html.parse(url).getroot()
	doc.make_links_absolute(url)
	#<div class="vlvz_kurz"><a href="/vlvz?kapitel=510&amp;semester=S2011">5.10</a> Master Informatikdidaktik</div>
	link = doc.xpath('//div[contains(@class,"vlvz_kurz") and contains(.,"%s")]/a'%studyname)[0].attrib.get("href") #lxml only is capable of XPath, thus no lower-case() function available for a case insensitive search
	return(link)

def fetchAllUrls(uniurls, studyname=studyname):
	#resolves all urls in the dictionary with the function fetchUrl
	uniurls2 = uniurls.copy()
	for semester, url in uniurls2.items():
		uniurls2[semester] = fetchUrl(url,studyname)
	return(uniurls2)

def uniExtract(xml_root, semester,url, universityName=uni, createNonexistentNodes=False):
	#extracts lvas from given url (uni) and writes to xml
	
	print("Scraping %s"%(url))
	
	doc = html.parse(url).getroot()

	#print(etree.tostring(doc))
	
	lva_university = universityName
	
	founds = doc.xpath('//h3[contains(@class,"chapter")] | //div[contains(@class,"vlvz_langtitel")]')

	if len(founds) == 0:
		raise Exception("No elements found in %s"%(url))

	addSource(xml_root, url, datetime.datetime.now().isoformat())

	#print(founds)
	
	lva_semester = semester[0] + semester[1]
	#print(lva_sem)
	
	for f in founds:
		#print(etree.tostring(f))
		if "chapter2" in f.attrib.get("class"): #studium
			lva_stpl = f.text.strip().partition(' ')[2].strip().partition(' ')[2]
			lva_stpl_version = "2009U.0" #TODO
			lva_modulgruppe, lva_modul, lva_anchor, lva_modul2 = "", "", "", ""
			getStpl(xml_root, lva_stpl,lva_stpl_version, lva_stpl_url="", createNonexistentNodes=createNonexistentNodes)
			#print("2: " + lva_studium + "<")
		elif "chapter3" in f.attrib.get("class"): #modulgruppe
			#.strip().partition(' ')[2]
			lva_modulgruppe = f.text.strip().partition(' ')[2].strip().partition('(')[0]
			lva_modul, lva_anchor, lva_modul2 = "", "", ""
			"""
			#remove unnecessary words
			if "Pflichtmodulgruppe" in lva_modulgruppe:
				lva_modulgruppe = lva_modulgruppe.partition("Pflichtmodulgruppe")[2]
			elif "Modulgruppe" in lva_modulgruppe:
				lva_modulgruppe = lva_modulgruppe.partition("Modulgruppe")[2]
			"""
			#Vertiefung Informatik, Wahlmodule (2 sind zu wählen)
			if "Vertiefung Informatik" not in lva_modulgruppe: #TODO
				getModulgruppe(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe, createNonexistentNodes)
			#print("3: " + lva_modulgruppe + "<")
		elif "chapter4" in f.attrib.get("class"): #modul
			lva_modul = f.text.strip().partition(' ')[2]
			if "ECTS" in lva_modul:
				if "(" in lva_modul:
					lva_modul = lva_modul.strip().partition('(')[0]
				else:
					lva_modul = lva_modul.strip().rpartition(',')[0]
			lva_modul2 = ""
			#remove unnecessary words
			if "Modul" in lva_modulgruppe:
				lva_modulgruppe = lva_modulgruppe.partition("Modul")[2]
			lva_url = f.base + "#" + f.attrib.get("id")
			#print(lva_anchor)
			#http://online.univie.ac.at/vlvz?kapitel=510&semester=S2011#510_3
			#<h3 class="chapter4" id="510_3">Modul...
			if "Pflichtmodul" not in lva_modul and "Wahlmodul" not in lva_modul:
				getModul(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul, createNonexistentNodes) #TODO
			elif "Vertiefung Informatik" in lva_modulgruppe:
				if "Pflichtmodul" in lva_modul:
					lva_modulgruppe = u"Modulgruppe Vertiefung Informatik, Pflichtmodul"
				if "Wahlmodul" in lva_modul:
					lva_modulgruppe = u"Modulgruppe Vertiefung Informatik, Wahlmodule (2 sind zu wählen)"
				getModulgruppe(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe, createNonexistentNodes)
			#print("4: " + lva_modul + "<")
		elif "chapter5" in f.attrib.get("class"): #modul bei vertiefungs-modulgruppe
			#lva_modul2 = f.text.strip().partition(' ')[2].strip().partition('(')[0].strip().partition(',')[0].strip()
			lva_modul = f.text.strip().partition(' ')[2].strip().partition('(')[0].strip().partition(',')[0]
			#getModul(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul2, createNonexistentNodes) #TODO
			getModul(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul, createNonexistentNodes) #TODO
			#print("5: " + lva_modul2 + "<")
		elif "vlvz_langtitel" in f.attrib.get("class"):
			lva_key = f.text
			#print(lva_num)
			
			lva_type = f.xpath('abbr')[0].text
			#print(lva_type)
			
			lva_title = f.xpath('span')[0].text
			
			#clean title from stuff like "PI.WI1.GK.VU"
			if "." in lva_title.strip().partition(" ")[0]:
				lva_title = lva_title.strip().partition(" ")[2]
			#and "PAED - "
			if "PAED -" in lva_title:
				lva_title = lva_title.partition("PAED -")[2]
			if "AMT" in lva_title:
				lva_title = lva_title.partition("AMT")[2]
			
			lva_sws = f.xpath('../div[contains(@class,"vlvz_wochenstunden")]')[0].text
			#print(lva_sws)

			lva_ects = f.xpath('../div[contains(@class,"vlvz_wochenstunden")]')[0].getchildren()[0].tail.strip().partition(' ')[2]
			#print(lva_ects)

			lva_info = "" #FIXME
			
			#print(lva_title)
			lva_fach = lva_title #TODO
			lva_fach_type = lva_type #TODO
			lva_fach_sws = lva_sws #TODO
			lva_fach_ects = lva_ects #TODO
			
			if "Theorie und Praxis des Lehrens und Lernens" in lva_fach: #problem: non-matching type SE, replace it
				lva_fach = u"Theorie und Praxis des Lehrens und Lernens"
				lva_fach_type = "VU"
			elif "Studieneingangsphase" in lva_fach:
				lva_fach = u"Einführung in professionalisiertes pädagogisches Handeln"
			
			if "Wahlmodul" in lva_modulgruppe:
				getFach(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects, createNonexistentNodes=True) #Vertiefungs Wahlmodule, is ok as an exception would have been thrown already by creating the modul if something was not found there
			else:
				getFach(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects, createNonexistentNodes)
			
			addLva(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects,lva_university,lva_semester,lva_title,lva_key,lva_type,lva_sws,lva_ects,lva_info,lva_url, createNonexistentNodes=False)
			
			#print("X: " + lva_key + "," + lva_type + "," + lva_semester + "<:>" + lva_title + " - " + lva_anchor + "<")
		else:
			raise Exception("Unexpected element in url %s: %s"%(url,etree.tostring(f)))

def getUni(xml_root, createNonexistentNodes=False):
	#gets lvas from uni and writes to xml
	#s_from = ("2011","S")
	#s_to = ("2011","S")
	#uniurls = getUniUrls(s_from, s_to)
	uniurls = getUniUrls()
	#TODO remove cached urls
	unicontenturls = fetchAllUrls(uniurls,studyname)
	for sem,url in unicontenturls.items():
		#print(sem[0] + sem[1] + "<>" + url + "<")
		uniExtract(xml_root, sem, url, createNonexistentNodes=createNonexistentNodes)


""" TU scraping """

def getTU(xml_root, url, universityName=tu, createNonexistentNodes=False, getLvas=True):
	#gets lvas from given url (Tiss) and writes to xml
	
	print("Scraping %s"%(url))

	#doc = html.parse(url).getroot()

	#stupid workaround necessary
	html_ = urllib.urlopen(url)
	#xml = html.read()
	#doc = etree.fromstring(xml, base_url=url)
	doc = html.parse(html_).getroot()
	doc.make_links_absolute(url)
	
	#print(etree.tostring(doc))

	lva_university = universityName
	
	founds = doc.xpath('//div[contains(@class,"nodeTable-level")]')

	if len(founds) == 0:
		raise Exception("No elements found in %s"%(url))

	addSource(xml_root, url, datetime.datetime.now().isoformat())
	
	lva_stpl_url = doc.xpath('//a[contains(@id,"legalTextLink")]')[0].attrib.get("href")
	#print(stpl_link)

	#print(founds)

	for f in founds:
		#print(etree.tostring(f))
		if "nodeTable-level-0" in f.attrib.get("class"):
			lva_stpl = f.text.strip().partition(' ')[0]
			lva_stpl_version = f.text.strip().partition(' ')[2]
			lva_modulgruppe, lva_modul = "", ""
			getStpl(xml_root, lva_stpl,lva_stpl_version, lva_stpl_url, createNonexistentNodes=createNonexistentNodes)
			#print("0: " + lva_stpl + "<>" + lva_stpl_version + "<")
		elif "nodeTable-level-1" in f.attrib.get("class"):
			lva_modulgruppe = f.text
			"""
			#strip unnecessary "Modul" or similar
			if "Pflichtmodulgruppe" in lva_modulgruppe:
				lva_modulgruppe = lva_modulgruppe.partition("Pflichtmodulgruppe")[2]
			elif "Modulgruppe" in lva_modulgruppe:
				lva_modulgruppe = lva_modulgruppe.partition("Modulgruppe")[2]
			elif "Modul" in lva_modulgruppe:
				lva_modulgruppe = lva_modulgruppe.partition("Modul")[2]
			"""
			lva_modul = ""
			getModulgruppe(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe, createNonexistentNodes)
			#print("1: " + lva_modulgruppe + "<")
		elif "nodeTable-level-2" in f.attrib.get("class") and "item" in f.attrib.get("class"):
			lva_modul = u"ICT-Infrastruktur für Bildungsaufgaben" #TODO
			lva_fach = f.text.partition(' ')[2]
			lva_fach_type = f.text.partition(' ')[0]
			lva_fach_sws = f.xpath('../following-sibling::*[contains(@class,"nodeTableHoursColumn")]')[0].text
			lva_fach_ects = f.xpath('../following-sibling::*[contains(@class,"nodeTableEctsColumn")]')[0].text
			getModul(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul, createNonexistentNodes) #could be leaved alone with the current createNonexistentNodes
			getFach(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects, createNonexistentNodes)
			#print("2i " + lva_modul + "<")
		elif "nodeTable-level-2" in f.attrib.get("class") and "item" not in f.attrib.get("class"):
			lva_modul = f.text
			if "Infomatik" in lva_modul:
				lva_modul = lva_modul.replace("Infomatik","Informatik")
			getModul(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul, createNonexistentNodes)
			#print("2: " + lva_modul + "<")
		elif "nodeTable-level-3" in f.attrib.get("class") and "item" in f.attrib.get("class"):
			lva_fach = f.text.partition(' ')[2]
			if '"Grundl.u.Praxis d.eLearning" od. "eTutoring, Moderation von e-Learning"' in lva_fach:
				lva_fach = '"Grundlagen und Praxis des eLearning" oder "eTutoring, Moderation von e-Learning"'
			elif "Erwachsenenbildung und Lebenslanges Lernen" in lva_fach: #deprecated
				lva_fach = u'"Theorie und Praxis des Lehrens und Lernens" (veraltet) oder "Erwachsenenbildung und Lebenslanges Lernen"'
			elif u"(4) Experiment. Gestaltung von MM-Anwend. + Präsentationsstrategien 1" in lva_fach:
				lva_fach = u"(4) Experimentelle Gestaltung von MM-Anwendungen + Präsentationsstrategien 1"
			lva_fach_type = f.text.partition(' ')[0]
			lva_fach_sws = f.xpath('../following-sibling::*[contains(@class,"nodeTableHoursColumn")]')[0].text
			lva_fach_ects = f.xpath('../following-sibling::*[contains(@class,"nodeTableEctsColumn")]')[0].text

			if "Wahlmodul" in lva_modulgruppe:
				#if getLvas: #don't add Fach at all when getLvas=False as Wahlmodule can contain *any* Fach which isn't important for the structure
				#problem with that: getFach does not work anymore
				getFach(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects, createNonexistentNodes=True) #Vertiefungs Wahlmodule, is ok as an exception would have been thrown already by creating the modul if something was not found there
			else:
				getFach(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects, createNonexistentNodes)
			#print("3: " + lva_fach + "<:>" + lva_fach_type + "<")
		elif ("nodeTable-level-4" in f.attrib.get("class") and "course" in f.attrib.get("class")) or ("nodeTable-level-3" in f.attrib.get("class") and "course" in f.attrib.get("class")):
			if getLvas:
				lva_key_type_sem = f.xpath('div')[0].text
				lva_key, lva_type, lva_semester = lva_key_type_sem.strip().split(' ')
				lva_title_url = f.xpath('div/a')[0]
				lva_url = lva_title_url.attrib.get("href") #.replace('&','&amp;')
				lva_title = lva_title_url.text
				lva_info = f.xpath('../following-sibling::*[contains(@class,"nodeTableInfoColumn")]/div')[0].text #can be None
				lva_sws = f.xpath('../following-sibling::*[contains(@class,"nodeTableHoursColumn")]')[0].text
				lva_ects = f.xpath('../following-sibling::*[contains(@class,"nodeTableEctsColumn")]')[0].text
				
				addLva(xml_root, lva_stpl,lva_stpl_version,lva_modulgruppe,lva_modul,lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects,lva_university,lva_semester,lva_title,lva_key,lva_type,lva_sws,lva_ects,lva_info,lva_url, createNonexistentNodes=False)
				#print("4: " + lva_key + "," + lva_type + "," + lva_semester + "<:>" + lva_title + " - " + lva_url + "<")
		else:
			raise Exception("Unexpected element in url %s: %s"%(url,etree.tostring(f)))

			
""" parse legacy file """

def getFile(xml_root, filename=legacyFile, universityName=tu):
	#retrieves lvas from old python script output file and writes to xml
	if filename.startswith("http"):
		f = urllib.urlopen(filename)
	else:
		f = open(filename, 'r')
	
	#lines = f.readlines() deprecated
	
	addSource(xml_root, filename, datetime.datetime.now().isoformat()) #TODO external filename
	
	for l in f:
		cells = l.split(" - ")
		
		#print(cells)
		
		lva_university = universityName
		lva_semester = cells[4].strip()
		lva_title = unicode(cells[3].strip(), "utf-8")
		lva_key = cells[0].strip()
		lva_type = cells[1].strip()
		lva_sws = cells[5].strip()
		lva_ects=""
		lva_info=""
		lva_url = ""
		lva_professor = unicode(cells[6].strip().capitalize(), "utf-8")
		
		lva_fach = lva_title
		lva_fach_type = lva_type
		lva_fach_sws = lva_sws
		lva_fach_ects = lva_ects
		
		#print(lva_fach)
		#print(cells[3])
		
		if "Theorie und Praxis des Lehrens und Lernens" in lva_fach: #problem: non-matching type SE
			#lva_fach = u"Theorie und Praxis des Lehrens und Lernens"
			lva_fach_type = "VU"
		elif "Vernetztes Lernen" in lva_fach:
			lva_fach_type = "VU"
		elif "Spezielle Kapitel der Schulinformatik" in lva_fach:
			lva_fach = "Kernthemen der Fachdidaktik Informatik"
		elif u"Kommunikation und Präsentation" in lva_fach:
			lva_fach = u"Präsentation und Moderation"
			lva_fach_type = "VU"

		addLva(xml_root, lva_stpl=None,lva_stpl_version=None,lva_modulgruppe=None,lva_modul=None,lva_fach=lva_fach,lva_fach_type=lva_fach_type,lva_fach_sws=lva_fach_sws,lva_fach_ects=lva_fach_ects,lva_university=lva_university,lva_semester=lva_semester,lva_title=lva_title,lva_key=lva_key,lva_type=lva_type,lva_sws=lva_sws,lva_ects=lva_ects,lva_info=lva_info,lva_url=lva_url, lva_professor=lva_professor, createNonexistentNodes=False, searchMatchingFach=True)

	f.close()
			
			
""" program script """


"""
x="Bla %s"%(u"ÄäÖöÜüß")
print(x)
raise Exception(x) #FIXME no unicode exception messages
"""

#raise Exception()

#open existing file if it exists or create new xml
xml_root = loadXml(xmlfilename, loadExisting=True, checkXmlSchema=True) #TODO loadExisting=True

#get structure
if isFreshXml(xml_root):
	getTU(xml_root, tiss, createNonexistentNodes=True, getLvas=False)

#get legacy lvas before adding other lvas
getFile(xml_root)

#get lvas from TU
getTU(xml_root, tiss, createNonexistentNodes=False)

#get lvas from Uni
getUni(xml_root, createNonexistentNodes=False)

"""
#check if generated xml is correct regarding xsd
if(checkSchema(xml_root)):
	print("XML is valid")
else:
	print("XML is NOT valid")
"""

#write xml to file + backupfile
writeXml(xml_root, filename=xmlfilename)

#generate and write rss to file + backupfile
generateRss(xml_root)
