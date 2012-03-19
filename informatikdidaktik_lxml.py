#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fabian Ehrentraud, 2012-03-19
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
import logging


#TODO
# make replacement rules more transparent and encapsulated
# when finally Tiss is updated to allow searching for old semesters' LVAs of a certain study code, incorporate the according scraping
# Interdisziplinäres Praktikum: Interaktionsdesign is wrongly assigned in Tiss (not to all according modules), fix this
# update date in an existing lva when any content has changed?
# support multiple professors
# scrape professors from Tiss
# LVA Wiki https://vowi.fsinf.at/wiki/Alle_LVAs_(TU_Wien)
# import argparse http://docs.python.org/library/argparse.html
# logging of Exceptions
# hover icon


studyname = "Informatikdidaktik"

xmlfilename = "informatikdidaktik.xml"
xmlcomment = "\nFabian Ehrentraud, 2011\ne0725639@mail.student.tuwien.ac.at\nhttps://github.com/fabb/Informatikdidaktik-Studienplan-Scraping\n"
rng = "stpl_collection.rng"
xslt = "informatikdidaktik.xslt"
xmlRootname = "stpl_collection"

rss_xslt = "informatikdidaktik_rss.xslt"
rss_xml = "informatikdidaktik_rss.xml"
backupfolder = "backup/" # needs trailing slash

#tiss = "https://tiss.tuwien.ac.at/curriculum/curriculumVersion.xhtml?locale=de&studyCode=066950&version=2009U.0"
tiss = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=56898&semester=CURRENT"
tiss_next = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=56898&semester=NEXT"

uniSemesterFrom = ("2009","W") #Informatikdidaktik exists since 2009W
#uniSemesterTo = ("2011","S") #use default currentSemester()
uni = "Uni"
tu = "TU"

legacyFile = "http://www.unet.univie.ac.at/~a0725639/informatikdidaktik/informatikdidaktik_tuwel_legacy_2010-09-02.txt"

newstuff = False


""" logging """

logger = logging.getLogger('informatikdidaktik')
logger.setLevel(logging.DEBUG)
#logging.basicConfig(filename='informatikdidaktik.log', level=logging.INFO) # level=logging.DEBUG # format='%(levelname)s:%(message)s'
consoleloghandler = logging.StreamHandler()
consoleloghandler.setLevel(logging.INFO)
fileloghandler = logging.FileHandler('informatikdidaktik.log')
fileloghandler.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s: %(message)s')
consoleloghandler.setFormatter(formatter)
fileloghandler.setFormatter(formatter)
logger.addHandler(consoleloghandler)
logger.addHandler(fileloghandler)



""" Classes """

class LVA:
	stpl = None
	stpl_version = None
	stpl_url = None
	modul1 = None
	modul1_iswahlmodulgruppe = None
	modul2 = None
	modul3 = None
	fach = None
	fach_type = None
	fach_sws = None
	fach_ects = None
	title = None
	type = None
	sws = None
	ects = None
	university = None
	key = None
	semester = None
	url = None
	professor = None
	info = None
	canceled = None # actually not stored, included in info
	
	def setStplAndForgetLowerHierarchy(self, stpl=None, stpl_version=None, stpl_url=None):
		self.setModul1AndForgetLowerHierarchy()
		self.stpl = stpl
		self.stpl_version = stpl_version
		self.stpl_url = stpl_url
	
	def setModul1AndForgetLowerHierarchy(self, modul1=None, modul1_iswahlmodulgruppe=None):
		self.setModul2AndForgetLowerHierarchy()
		self.modul1 = modul1
		self.modul1_iswahlmodulgruppe = modul1_iswahlmodulgruppe
	
	def setModul2AndForgetLowerHierarchy(self, modul2=None):
		self.setModul3AndForgetLowerHierarchy()
		self.modul2 = modul2
	
	def setModul3AndForgetLowerHierarchy(self, modul3=None):
		self.setFachAndForgetLowerHierarchy()
		self.modul3 = modul3
	
	def setFachAndForgetLowerHierarchy(self, fach=None, fach_type=None, fach_sws=None, fach_ects=None):
		self.setLvaAndForgetLowerHierarchy()
		self.fach = fach
		self.fach_type = fach_type
		self.fach_sws = fach_sws
		self.fach_ects = fach_ects
	
	def setLvaAndForgetLowerHierarchy(self, title=None, type=None, sws=None, ects=None, university=None, key=None, semester=None, url=None, professor=None, info=None, canceled=None):
		self.title = title
		self.type = type
		self.sws = sws
		self.ects = ects
		self.university = university
		self.key = key
		self.semester = semester
		self.url = url
		self.professor = professor
		self.info = info
		self.canceled = canceled
	
	def __str__(self):
		return """LVA:
	stpl: %s
	stpl_version: %s
	stpl_url: %s
	modul1: %s
	modul1_iswahlmodulgruppe: %s
	modul2: %s
	modul3: %s
	fach: %s
	fach_type: %s
	fach_sws: %s
	fach_ects: %s
	title: %s
	type: %s
	sws: %s
	ects: %s
	university: %s
	key: %s
	semester: %s
	url: %s
	professor: %s
	info: %s
	canceled: %s"""%(\
	self.stpl,\
	self.stpl_version,\
	self.stpl_url,\
	self.modul1,\
	self.modul1_iswahlmodulgruppe,\
	self.modul2,\
	self.modul3,\
	self.fach,\
	self.fach_type,\
	self.fach_sws,\
	self.fach_ects,\
	self.title,\
	self.type,\
	self.sws,\
	self.ects,\
	self.university,\
	self.key,\
	self.semester,\
	self.url,\
	self.professor,\
	self.info,\
	self.canceled)

class PathElementNotFoundException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class Scraper():
	def __init__(self):
		raise Exception("Abstract Function")
	def scrape(self):
		raise Exception("Abstract Function")


class TUScraper(Scraper):
	logger_ = None
	universityName_ = None

	def __init__(self, logger=logger, universityName=tu):
		self.logger_ = logger
		self.universityName_ = universityName
	
	def scrape(self, xml, url, createNonexistentNodes=False, getLvas=True, lva_stpl_version="2009U.0", reorderFach=False):
		#gets lvas from given url (Tiss) and writes to xml
		self.logger_.info("Scraping %s", url)
		lva = LVA()
		#doc = html.parse(url).getroot()

		#stupid workaround necessary
		html_ = urllib.urlopen(url)
		#xml = html.read()
		#doc = etree.fromstring(xml, base_url=url)
		doc = html.parse(html_).getroot()
		doc.make_links_absolute(url)
		
		#print(etree.tostring(doc))
		lva_university = self.universityName_
		founds = doc.xpath('//div[contains(@class,"nodeTable-level")]')

		if len(founds) == 0:
			raise Exception("No elements found in %s"%(url))

		xml.addSource(url, datetime.datetime.now().isoformat())
		lva_stpl_url = doc.xpath('//a[contains(@id,"legalTextLink")]')[0].attrib.get("href")

		for f in founds:
			#print(etree.tostring(f))
			if "nodeTable-level-0" in f.attrib.get("class"):
				lva_stpl = f.text + f.xpath('span')[0].text
				#lva_stpl_version = f.text.strip().partition(' ')[2] #TODO no more on website
				lva.setStplAndForgetLowerHierarchy(stpl=lva_stpl, stpl_version=None, stpl_url=lva_stpl_url)
				
				if not reorderFach:
					xml.getStpl(lva, createNonexistentNodes=createNonexistentNodes)
				#print("0: " + lva.stpl + "<>" + lva.stpl_version + "<")
			elif "nodeTable-level-1" in f.attrib.get("class"):
				lva_modul1_iswahlmodulgruppe = False

				lva_modul1 = f.xpath('span')[0].text
				"""
				#strip unnecessary "Modul" or similar
				if "Pflichtmodulgruppe" in lva.modul1:
					lva.modul1 = lva.modul1.partition("Pflichtmodulgruppe")[2]
				elif "Modulgruppe" in lva.modul1:
					lva.modul1 = lva.modul1.partition("Modulgruppe")[2]
				elif "Modul" in lva.modul1:
					lva.modul1 = lva.modul1.partition("Modul")[2]
				"""
				if "Wahlmodul" in lva_modul1:
					lva_modul1_iswahlmodulgruppe = True
				
				lva.setModul1AndForgetLowerHierarchy(modul1=lva_modul1, modul1_iswahlmodulgruppe=lva_modul1_iswahlmodulgruppe)
				
				if not reorderFach:
					xml.getModul1(lva, createNonexistentNodes)
				#print("1: " + lva.modul1 + "<")
			elif "nodeTable-level-2" in f.attrib.get("class") and "item" in f.attrib.get("class"):
				lva.setModul2AndForgetLowerHierarchy() #clear modul2 and below

				#lva.fach = f.text.partition(' ')[2]
				#lva.fach_type = f.text.partition(' ')[0]
				lva_fach = f.xpath('span')[0].text
				lva_fach_type = f.text
				#lva.fach_sws = f.xpath('../following-sibling::*[contains(@class,"nodeTableHoursColumn")]')[0].text
				#lva.fach_ects = f.xpath('../following-sibling::*[contains(@class,"nodeTableEctsColumn")]')[0].text
				lva_fach_sws = f.xpath('../following-sibling::td')[2].text
				lva_fach_ects = f.xpath('../following-sibling::td')[3].text
				
				lva.setFachAndForgetLowerHierarchy(fach=lva_fach, fach_type=lva_fach_type, fach_sws=lva_fach_sws, fach_ects=lva_fach_ects)
				
				if not reorderFach:
					xml.getFach(lva, createNonexistentNodes)
				else:
					self.checkAndMoveFach_(xml, lva)
					
				#xml.getFach(lva, True) #TODO
				#print("2i " + lva.modul2 + "<")
			elif "nodeTable-level-2" in f.attrib.get("class") and "item" not in f.attrib.get("class"):
				lva_modul2 = f.xpath('span')[0].text
				if "Infomatik" in lva_modul2:
					lva_modul2 = lva_modul2.replace("Infomatik","Informatik")
				
				lva.setModul2AndForgetLowerHierarchy(modul2=lva_modul2)
				
				if not reorderFach:
					xml.getModul2(lva, createNonexistentNodes)
				#print("2: " + lva.modul2 + "<")
			elif "nodeTable-level-3" in f.attrib.get("class") and "item" in f.attrib.get("class"):
				#lva_fach = f.text.partition(' ')[2]
				lva_fach = f.xpath('span')[0].text
				lva_fach_type = f.text

				if "Seminar aus Knowledge Management" not in lva_fach: #this fach is on level-3 instead of level-4
					lva.setModul3AndForgetLowerHierarchy() #clear modul3 and below
				
				if '"Grundl.u.Praxis d.eLearning" od. "eTutoring, Moderation von e-Learning"' in lva_fach:
					lva_fach = '"Grundlagen und Praxis des eLearning" oder "eTutoring, Moderation von e-Learning"'
				elif "Erwachsenenbildung und Lebenslanges Lernen" in lva_fach: #deprecated
					lva_fach = u'"Theorie und Praxis des Lehrens und Lernens" oder "Erwachsenenbildung und Lebenslanges Lernen"'
				elif u"(4) Experiment. Gestaltung von MM-Anwend. + Präsentationsstrategien 1" in lva_fach:
					lva_fach = u"(4) Experimentelle Gestaltung von MM-Anwendungen + Präsentationsstrategien 1"
				elif u"Grundlagen der Kommunikations- und Medientheorie" in lva_fach: #wrongly assigned in TISS
					lva_fach = u'"Medienpädagogik" oder "Grundlagen der Kommunikations- und Medientheorie"'
					lva_fach_type = "VO"
				#lva_fach_sws = f.xpath('../following-sibling::*[contains(@class,"nodeTableHoursColumn")]')[0].text
				#lva_fach_ects = f.xpath('../following-sibling::*[contains(@class,"nodeTableEctsColumn")]')[0].text
				lva_fach_sws = f.xpath('../following-sibling::td')[2].text
				lva_fach_ects = f.xpath('../following-sibling::td')[3].text
				
				lva.setFachAndForgetLowerHierarchy(fach=lva_fach, fach_type=lva_fach_type, fach_sws=lva_fach_sws, fach_ects=lva_fach_ects)

				if not reorderFach:
					if lva.modul1_iswahlmodulgruppe or "Media Technologies" in lva.modul2:
						#if getLvas: #don't add Fach at all when getLvas=False as Wahlmodule can contain *any* Fach which isn't important for the structure
						#problem with that: getFach does not work anymore
						xml.getFach(lva, createNonexistentNodes=True) #Vertiefungs Wahlmodule, is ok as an exception would have been thrown already by creating the modul if something was not found there
					else:
						xml.getFach(lva, createNonexistentNodes)
				else:
					self.checkAndMoveFach_(xml, lva)

				#print("3: " + lva.fach + "<:>" + lva.fach_type + "<")
			elif "nodeTable-level-3" in f.attrib.get("class") and "item" not in f.attrib.get("class"):
				lva_modul3 = f.xpath('span')[0].text
				
				lva.setModul3AndForgetLowerHierarchy(modul3=lva_modul3)

				if not reorderFach:
					if lva.modul1_iswahlmodulgruppe or "Media Understanding" in lva.modul3:
						xml.getModul3(lva, createNonexistentNodes=True)
					else:
						xml.getModul3(lva, createNonexistentNodes)
				#m3 = xml.getModul3(lva, True) #TODO
				#self.logger_.info("modul 3 found/created: %s",etree.tostring(m3)) #TODO
				#raise Exception("level 3 non-item in url %s: %s"%(url,etree.tostring(f)))
			elif "nodeTable-level-4" in f.attrib.get("class") and "item" in f.attrib.get("class"):
				lva_fach = f.xpath('span')[0].text
				lva_fach_type = f.text
				lva_fach_sws = f.xpath('../following-sibling::td')[2].text
				lva_fach_ects = f.xpath('../following-sibling::td')[3].text
				
				lva.setFachAndForgetLowerHierarchy(fach=lva_fach, fach_type=lva_fach_type, fach_sws=lva_fach_sws, fach_ects=lva_fach_ects)

				if not reorderFach:
					if lva.modul1_iswahlmodulgruppe or "Media Understanding" in lva.modul3:
						xml.getFach(lva, createNonexistentNodes=True)
					else:
						xml.getFach(lva, createNonexistentNodes)
				else:
					self.checkAndMoveFach_(xml, lva)
				
				#xml.getFach(lva, True) #TODO
				#raise Exception("level 4 item in url %s: %s"%(url,etree.tostring(f)))
			elif ("nodeTable-level-5" in f.attrib.get("class") and "course" in f.attrib.get("class")) or ("nodeTable-level-4" in f.attrib.get("class") and "course" in f.attrib.get("class")) or ("nodeTable-level-3" in f.attrib.get("class") and "course" in f.attrib.get("class")):
				if getLvas and not reorderFach:
					lva_key_type_sem = f.xpath('div')[0].text
					lva_key, lva_type, lva_semester = lva_key_type_sem.strip().split(' ')
					lva_title_url = f.xpath('div/a')[0]
					#lva.canceled = f.xpath('div/span')[0].text if f.xpath('div/span') is not None else ""
					lva_canceled = "abgesagt" if "canceled" in f.attrib.get("class").lower() else ""
					lva_url = self.sanitizeTUrl_(lva_title_url.attrib.get("href")) #.replace('&','&amp;')
					lva_title = lva_title_url.text
					#lva.info = f.xpath('../following-sibling::*[contains(@class,"nodeTableInfoColumn")]/div')[0].text #can be None
					lva_info = lva_canceled
					#lva.sws = f.xpath('../following-sibling::*[contains(@class,"nodeTableHoursColumn")]')[0].text
					#lva.ects = f.xpath('../following-sibling::*[contains(@class,"nodeTableEctsColumn")]')[0].text
					lva_sws = f.xpath('../following-sibling::td')[2].text
					lva_ects = f.xpath('../following-sibling::td')[3].text
					
					lva.setLvaAndForgetLowerHierarchy(title=lva_title, type=lva_type, sws=lva_sws, ects=lva_ects, university=lva_university, key=lva_key, semester=lva_semester, url=lva_url, professor=None, info=lva_info, canceled=lva_canceled)

					xml.addLva(lva, createNonexistentNodes=False)
					#print("4: " + lva.key + "," + lva.type + "," + lva.semester + "<:>" + lva.title + " - " + lva.url + "<")
			else:
				raise Exception("Unexpected element in url %s: %s"%(url,etree.tostring(f)))

	def checkAndMoveFach_(self, xml, lva):
		if self.existsFachAtPath_(xml, lva):
			return
		
		if not self.existsFachAnywhere_(xml, lva):
			#print("ignoring fach as it does not yet exists")
			return
		
		fach = xml.getMatchingFach(lva)
		self.logger_.info("Moving Fach: %s %s %s %s", lva.fach, lva.fach_type, lva.fach_sws, lva.fach_ects)

		oldparent = fach.getparent()
		oldparent.remove(fach)

		newparent = xml.getModulX(lva, True)
		newparent.append(fach)

		removeparent = oldparent
		while True:
			children = removeparent.xpath(".//modul1 | .//modul2 | .//modul3 | .//fach")
			print("\nchildren:\n%s"%(children))
			if len(children) == 0:
				self.logger_.info("Removing Empty Modul: %s", (removeparent.xpath("title")[0].text))
				removeelem = removeparent
				removeparent = removeparent.getparent()
				removeparent.remove(removeelem)
			else:
				break
			if removeparent is None:
				break

	def existsFachAtPath_(self, xml, lva):
		try:
			xml.getFach(lva, False)
			return True
		except PathElementNotFoundException as e:
			return False

	def existsFachAnywhere_(self, xml, lva):
		try:
			xml.getMatchingFach(lva)
			return True
		except PathElementNotFoundException as e:
			return False

	def sanitizeTUrl_(self, url):
		urlparts = url.split("?")
		if len(urlparts) == 1:
			return url
		if len(urlparts) == 2:
			cleanurl = urlparts[0] + "?"
			vars = urlparts[1].split("&")
			for v in vars:
				if not v.startswith(("windowId=")):
					cleanurl += v + "&"
			return cleanurl[:-1]
		else:
			raise Exception("Url has more than one ?: %s"%(url))


class TULegacyScraper(Scraper):
	logger_ = None
	filename_ = None
	universityName_ = None

	def __init__(self, logger=logger, filename=legacyFile, universityName=tu):
		self.logger_ = logger
		self.filename_ = filename
		self.universityName_ = universityName
		
	def scrape(self, xml):
		#retrieves lvas from old python script output file and writes to xml
		
		if xml.wasUrlScraped(self.filename_):
			return #nothing to do
		
		self.logger_.info("Scraping %s", self.filename_)
		
		if self.filename_.startswith("http"):
			f = urllib.urlopen(self.filename_)
		else:
			f = open(self.filename_, 'r')
		
		#lines = f.readlines() deprecated
		
		lva = LVA()
		xml.addSource(self.filename_, datetime.datetime.now().isoformat()) #TODO external filename
		
		for l in f:
			cells = l.split(" - ")
			
			#print(cells)
			
			lva_university = self.universityName_
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
			
			#print(lva.fach)
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
			elif u"Analyse von Algorithmen" in lva_fach:
				lva_fach = u"Analysis of Algorithms"
			elif u"Advanced Software Engineering" in lva_fach:
				self.createWahlFachHelper_(xml,"Advanced Software Engineering",None, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Mobile and Pervasive Computing" in lva_fach:
				self.createWahlFachHelper_(xml,"Distributed und Mobile Computing",None, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Advanced Internet Security" in lva_fach:
				self.createWahlFachHelper_(xml,"Netzwerke und Security",None, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Entwurfsmethoden für verteilte Systeme" in lva_fach:
				self.createWahlFachHelper_(xml,"Netzwerke und Security",None, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Distributed Systems Technologies" in lva_fach:
				self.createWahlFachHelper_(xml,"Netzwerke und Security",None, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Advanced Distributed Systems" in lva_fach:
				self.createWahlFachHelper_(xml,"Netzwerke und Security",None, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Programmiersprachen" in lva_fach:
				self.createWahlFachHelper_(xml,"Programmiersprachen","Computersprachen und Programmierung", lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Fortgeschrittene logikorientierte Programmierung" in lva_fach:
				self.createWahlFachHelper_(xml,"Programmiersprachen","Computersprachen und Programmierung", lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Fortgeschrittene funktionale Programmierung" in lva_fach:
				self.createWahlFachHelper_(xml,"Programmiersprachen","Computersprachen und Programmierung", lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Seminar aus Visualisierung" in lva_fach:
				self.createWahlFachHelper_(xml,"Informationsvisualisierung",'entweder aus Modul "Visualisierung Vertiefung"', lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Forschungsseminar aus Computergraphik und digitaler Bildverarbeitung" in lva_fach:
				self.createWahlFachHelper_(xml,"Computergrafik",'Computergraphik - Vertiefung', lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Algorithmische Geometrie" in lva_fach:
				lva_fach = u"Algorithmic Geometry"
			elif u"Effiziente Algorithmen" in lva_fach:
				lva_fach = u"Efficient Algorithms"
			elif u"Algorithmen auf Graphen" in lva_fach:
				self.createWahlFachHelper_(xml,"Algorithmen",'Algorithmik', lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Seminar aus Computergraphik" in lva_fach:
				self.createWahlFachHelper_(xml,"Computergrafik",'Computergraphik - Vertiefung', lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Computergraphik 2" in lva_fach:
				self.createWahlFachHelper_(xml,"Computergrafik",'Computergraphik - Vertiefung', lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Multimedia Produktion 2: Interaktionsdesign" in lva_fach:
				self.createMediaFachHelper_(xml, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Interdisziplinäres Praktikum: Interaktionsdesign" in lva_fach:
				self.createMediaFachHelper_(xml, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Online Communities und E-Commerce" in lva_fach:
				self.createWahlFachHelper_(xml,"e-Business",None, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
			elif u"Knowledge Management" in lva_fach:
				self.createWahlFachHelper_(xml,"Knowledge Engineering",'oder aus Modul "Knowledge Management"', lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects)
				
			lva.setFachAndForgetLowerHierarchy(fach=lva_fach, fach_type=lva_fach_type, fach_sws=lva_fach_sws, fach_ects=lva_fach_ects)
			lva.setLvaAndForgetLowerHierarchy(title=lva_title, type=lva_type, sws=lva_sws, ects=lva_ects, university=lva_university, key=lva_key, semester=lva_semester, url=lva_url, professor=lva_professor, info=lva_info, canceled=None)

			xml.addLva(lva, createNonexistentNodes=False, searchMatchingFach=True)

		f.close()

	def createWahlFachHelper_(self, xml,lva_modul2,lva_modul3, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects):
		xml.createWahlFach(lva_stpl=None,lva_stpl_version=None,lva_modul1=u"Modulgruppe Vertiefung Informatik, Wahlmodule (2 sind zu wählen)",lva_modul2=lva_modul2,lva_modul3=lva_modul3, lva_fach=lva_fach,lva_fach_type=lva_fach_type,lva_fach_sws=lva_fach_sws,lva_fach_ects=lva_fach_ects)

	def createMediaFachHelper_(self, xml, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects):
		xml.createMediaLegacyModul(lva_stpl=None,lva_stpl_version=None,lva_modul1=u"Pflichtmodulgruppe Informationstechnologien zur Wissensvermittlung",lva_modul2=u"Media Technologies - Eine der Varianten (1-4) ist zu wählen",lva_modul3=u"früheres Modul (2)")
		xml.createWahlFach(lva_stpl=None,lva_stpl_version=None,lva_modul1=u"Pflichtmodulgruppe Informationstechnologien zur Wissensvermittlung",lva_modul2=u"Media Technologies - Eine der Varianten (1-4) ist zu wählen",lva_modul3=u"früheres Modul (2)", lva_fach=lva_fach,lva_fach_type=lva_fach_type,lva_fach_sws=lva_fach_sws,lva_fach_ects=lva_fach_ects)


class UniScraper(Scraper):
	logger_ = None
	uniSemesterFrom_ = None
	studyname_ = None
	universityName_ = None
	
	def __init__(self, logger=logger, uniSemesterFrom=uniSemesterFrom, studyname=studyname, universityName=uni):
		self.logger_ = logger
		self.uniSemesterFrom_ = uniSemesterFrom
		self.studyname_ = studyname
		self.universityName_ = universityName
	
	def scrape(self, xml, createNonexistentNodes=False):
		#gets lvas from uni and writes to xml
		#s_from = ("2011","S")
		#s_to = ("2011","S")
		#uniurls = self.getUniUrls_(s_from, s_to)
		uniurls = self.getUniUrls_(self.uniSemesterFrom_,  self.currentSemester_())
		
		pruned_uniurls = self.pruneUni_(xml, uniurls)
		
		unicontenturls = self.fetchAllUrls_(pruned_uniurls,self.studyname_)
		for sem,(referring_url,url) in unicontenturls.items():
			#print(sem[0] + sem[1] + "<>" + url + "<")
			self.uniExtract_(xml, sem, url, referring_url, self.universityName_, createNonexistentNodes=createNonexistentNodes)

	def getUniUrls_(self, (from_year,from_semester), (to_year,to_semester)):
		#builds urls of websites with all studies of the given semester range
		uniurl = "http://online.univie.ac.at/vlvz?fakultaet=-1&semester=%s"
		urls = OrderedDict([(sem,uniurl%(''.join(sem[::-1]))) for sem in self.srange_((from_year,from_semester),(to_year,to_semester))])
		return urls

	def srange_(self, (from_year,from_semester),(to_year,to_semester)):
		#generates a list of the semesters in the range from-to, sorted chronologically, format ["W2009","S2010",..]
		ws = ["S","W"]
		try:
			y_f = int(from_year)
			y_t = int(to_year)
			if not from_semester in ws or not to_semester in ws:
				raise Exception()
		except (TypeError, ValueError, OverflowError, Exception): #int conversion failed
			return []

		yy = range(y_f,y_t+1)

		combin = [(str(y),s) for y in yy for s in ws]
		
		try:
			if from_semester == ws[1]:
				combin.pop(0)
			if to_semester == ws[0]:
				combin.pop()
		except IndexError:
			return []
		
		return combin

	def pruneUni_(self, xml, uniurls):
		#removes all urls which do not need to be scraped
		uniurls2 = uniurls.copy()
		current_sem = self.currentSemester_(True)
		
		for sem,referring_url in uniurls2.items():
			if self.smallerSem_(sem, current_sem) and self.hasRecentDate_(xml, referring_url, sem):
				del uniurls2[sem]
		
		return uniurls2

	def currentSemester_(self, realCurrent=False):
		#calculates the current semester - from january on, the following summer semester will be output, from july on, the following winter semester
		year = datetime.datetime.now().year
		month = datetime.datetime.now().month
		current_year = str(year)
		if realCurrent: #new semester only when it really has begun
			current_sem = "S" if month < 10 and month > 2 else "W"
		else:
			current_sem = "S" if month < 7 else "W"
			#TODO this gets the summer courses in january which might be a bit late
		return (current_year,current_sem)

	def smallerSem_(self, sem1, sem2):
		#returns whether the first semester tuple is smaller than the second
		(year1,sumwint1) = sem1
		(year2,sumwint2) = sem2
		if year1 < year2:
			return True
		elif year1 > year2:
			return False
		elif year1 == year2 and sumwint1 < sumwint2: #S<W
			return True
		else:
			return False

	def hasRecentDate_(self, xml, referring_url, sem):
		#checks whether the given referring_url was checked after the semester was over
		#TODO get rid of sem
		newestDate = xml.newestDate(referring_url)
		if newestDate:
			return self.dateAfterSemester_(newestDate, sem)
		else:
			return False

	def dateAfterSemester_(self, date, semester):
		#returns whether the given date is located in the given semester (or before the next one has started)
		if date is None or semester is None:
			return False
		dateS = date.split('-')
		year = dateS[0]
		month = dateS[1]
		if int(month) < 10 and int(month) > 2:
			dateSumWint = "S"
		else:
			dateSumWint = "W"
			year = str(int(year) - 1)
		dateSem = (year,dateSumWint)
		return self.smallerSem_(semester, dateSem)

	def fetchAllUrls_(self, uniurls, studyname):
		#resolves all urls in the dictionary with the function fetchUrl_
		uniurls2 = uniurls.copy()
		for semester, url in uniurls2.items():
			uniurls2[semester] = (url,self.fetchUrl_(url,studyname))
		return uniurls2

	def fetchUrl_(self, url, studyname):
		#gets the url in the <a> tag that is next to the studyname
		
		self.logger_.info("Querying %s", url)
		
		doc = html.parse(url).getroot()
		doc.make_links_absolute(url)
		#<div class="vlvz_kurz"><a href="/vlvz?kapitel=510&amp;semester=S2011">5.10</a> Master Informatikdidaktik</div>
		link = doc.xpath('//div[contains(@class,"vlvz_kurz") and contains(.,"%s")]/a'%studyname)[0].attrib.get("href") #lxml only is capable of XPath, thus no lower-case() function available for a case insensitive search
		return link

	def uniExtract_(self, xml, semester,url, referring_url, universityName, createNonexistentNodes=False):
		#extracts lvas from given url (uni) and writes to xml
		self.logger_.info("Scraping %s", url)
		doc = html.parse(url).getroot()
		#print(etree.tostring(doc))
		lva = LVA()
		lva_university = universityName
		founds = doc.xpath('//h3[contains(@class,"chapter")] | //div[contains(@class,"vlvz_langtitel")]')

		if len(founds) == 0:
			raise Exception("No elements found in %s"%(url))

		xml.addSource(url, datetime.datetime.now().isoformat(), referring_url)
		lva_semester = semester[0] + semester[1]
		
		for f in founds:
			#print(etree.tostring(f))
			if "chapter2" in f.attrib.get("class"): #studium
				lva_stpl = f.text.strip().partition(' ')[2].strip().partition(' ')[2]
				lva_stpl_version = "2009U.0" #TODO
				lva.setStplAndForgetLowerHierarchy(stpl=lva_stpl, stpl_version=lva_stpl_version, stpl_url=None)
				xml.getStpl(lva, createNonexistentNodes=createNonexistentNodes)
				#print("2: " + lva.stpl + " " + lva.stpl_version + "<")
			elif "chapter3" in f.attrib.get("class"): #modul1
				#.strip().partition(' ')[2]
				lva_modul1 = f.text.strip().partition(' ')[2].strip().partition('(')[0]
				#remove unnecessary words
				if "Modul" in lva_modul1:
					lva_modul1 = lva_modul1.partition("Modul")[2]
				lva.setModul1AndForgetLowerHierarchy(modul1=lva_modul1, modul1_iswahlmodulgruppe=False)
				"""
				#remove unnecessary words
				if "Pflichtmodulgruppe" in lva.modul1:
					lva.modul1 = lva.modul1.partition("Pflichtmodulgruppe")[2]
				elif "Modulgruppe" in lva.modul1:
					lva.modul1 = lva.modul1.partition("Modulgruppe")[2]
				"""
				#Vertiefung Informatik, Wahlmodule (2 sind zu wählen)
				if "Vertiefung Informatik" not in lva.modul1: #TODO
					xml.getModul1(lva, createNonexistentNodes)
				#print("3: " + lva.modul1 + "<")
			elif "chapter4" in f.attrib.get("class"): #modul2
				lva_modul2 = f.text.strip().partition(' ')[2]
				if "ECTS" in lva_modul2:
					if "(" in lva_modul2:
						lva_modul2 = lva_modul2.strip().partition('(')[0]
					else:
						lva_modul2 = lva_modul2.strip().rpartition(',')[0]
				lva.setModul2AndForgetLowerHierarchy(modul2=lva_modul2)
				lva_url = f.base + "#" + f.attrib.get("id")
				#print(lva_url)
				#http://online.univie.ac.at/vlvz?kapitel=510&semester=S2011#510_3
				#<h3 class="chapter4" id="510_3">Modul...
				lva.modul1_iswahlmodulgruppe = False
				if "Pflichtmodul" not in lva.modul2 and "Wahlmodul" not in lva.modul2:
					xml.getModul2(lva, createNonexistentNodes) #TODO
				elif "Vertiefung Informatik" in lva.modul1:
					if "Pflichtmodul" in lva.modul2:
						lva.setModul1AndForgetLowerHierarchy(modul1=u"Modulgruppe Vertiefung Informatik, Pflichtmodul", modul1_iswahlmodulgruppe=False)
					elif "Wahlmodul" in lva.modul2:
						lva.setModul1AndForgetLowerHierarchy(modul1=u"Modulgruppe Vertiefung Informatik, Wahlmodule (2 sind zu wählen)", modul1_iswahlmodulgruppe=True)
					xml.getModul1(lva, createNonexistentNodes)
				#print("4: " + lva.modul2 + "<")
			elif "chapter5" in f.attrib.get("class"): #modul bei vertiefungs-modulgruppe
				lva_modul2 = f.text.strip().partition(' ')[2].strip().partition('(')[0].strip().partition(',')[0]
				
				if u"ICT-Infrastruktur für Bildungsaufgaben" in lva_modul2:
					lva.setModul2AndForgetLowerHierarchy(modul2=None)
				else:
					lva.setModul2AndForgetLowerHierarchy(modul2=lva_modul2)
					xml.getModul2(lva, createNonexistentNodes) #TODO
				#print("5: " + lva.modul2 + "<")
			elif "vlvz_langtitel" in f.attrib.get("class"):
				lva_key = f.text
				#print(lva.key)
				
				lva_type = f.xpath('abbr')[0].text
				#print(lva.type)
				
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
				#print(lva.sws)

				lva_ects = f.xpath('../div[contains(@class,"vlvz_wochenstunden")]')[0].getchildren()[0].tail.strip().partition(' ')[2]
				#print(lva.ects)

				lva_professors = map(lambda e: e.text, f.xpath('../div[contains(@class,"vlvz_vortragende")]/a'))
				lva_professor = ', '.join([x.strip() for x in lva_professors])
				#print(lva.professor)

				lva_info = "" #FIXME
				
				#print(lva.title)
				lva_fach = lva_title #TODO
				lva_fach_type = lva_type #TODO
				lva_fach_sws = lva_sws #TODO
				lva_fach_ects = lva_ects #TODO
				
				if "Theorie und Praxis des Lehrens und Lernens" in lva_fach: #problem: non-matching type SE, replace it
					lva_fach = u"Theorie und Praxis des Lehrens und Lernens"
					lva_fach_type = "VU"
				elif "Studieneingangsphase" in lva_fach:
					lva_fach = u"Einführung in professionalisiertes pädagogisches Handeln"
				elif u"Computerunterstütztes Lernen" in lva_fach or "Vernetztes Lernen" in lva_fach:
					lva_fach_ects = "3.0"
				elif "Unterrichtspraktikum Informatikdidaktik" in lva_fach: #at Uni, this course is split into two semesters
					lva_fach_sws = ""
					lva_fach_ects = ""
				
				lva.setFachAndForgetLowerHierarchy(fach=lva_fach, fach_type=lva_fach_type, fach_sws=lva_fach_sws, fach_ects=lva_fach_ects)
				lva.setLvaAndForgetLowerHierarchy(title=lva_title, type=lva_type, sws=lva_sws, ects=lva_ects, university=lva_university, key=lva_key, semester=lva_semester, url=lva_url, professor=lva_professor, info=lva_info, canceled=None)
				
				if "Wahlmodul" in lva.modul1 or u"Freifächer" in lva.modul1:
					xml.getFach(lva, createNonexistentNodes=True) #Vertiefungs Wahlmodule, is ok as an exception would have been thrown already by creating the modul if something was not found there
				elif u"Modulgruppe Vertiefung Informatik, Pflichtmodul" in lva.modul1:
					xml.getFach(lva, createNonexistentNodes=True) #Vertiefungs Wahlmodule, is ok as an exception would have been thrown already by creating the modul if something was not found there
				else:
					xml.getFach(lva, createNonexistentNodes)
				
				xml.addLva(lva, createNonexistentNodes=False)
				
				#print("X: " + lva.key + "," + lva.type + "," + lva.semester + "<:>" + lva.title + " - " + lva_url + "<")
			else:
				raise Exception("Unexpected element in url %s: %s"%(url,etree.tostring(f)))


class STPLXML():
	didChange = False # True when something has changed - can be set to False from outside
	xml_root_ = None
	logger_ = None
	rootname_ = None
	schema_ = None
	comment_ = None
	xsltstylesheet_ = None
	rss_xslt_ = None

	def __init__(self, logger=logger, rootname=xmlRootname, schema=rng, comment=xmlcomment, xsltstylesheet=xslt, rss_xslt=rss_xslt):
		self.logger_ = logger
		self.rootname_ = rootname
		self.schema_ = schema
		self.comment_ = comment
		self.xsltstylesheet_ = xsltstylesheet
		self.rss_xslt_ = rss_xslt

	def loadXml(self, xmlfilename, loadExisting=True, checkXmlSchema=False):
		#open existing file if it exists or create new xml
		#check xml only when file is opened
		if loadExisting and os.path.exists(xmlfilename):
			#open existing file
			self.xml_root_ = self.readXml_(xmlfilename, checkXmlSchema)
		else:
			#create xml
			self.makeRoot_()
		
		#self.didChange = True

	def readXml_(self, filename, checkXmlSchema=False):
		self.logger_.info("Reading in existing XML file %s", filename)
		
		parser = etree.XMLParser(remove_blank_text=True) #read in a pretty printed xml and don't interpret whitespaces as meaningful data => this allows correct output pretty printing
		xml_root = etree.parse(filename, parser).getroot()

		#print(etree.tostring(xml_root))
		
		if checkXmlSchema:
			if not self.checkSchema_(xml_root):
				raise Exception("Verifying XML Schema failed")
		
		return xml_root

	def makeRoot_(self):
		#creates an stpl xml with xslt PI
		self.xml_root_ = etree.Element(self.rootname_)
		#self.xml_root_.append( etree.Element("child1") )

		# self.xml_root_.insert(0, etree.Element("child0"))
		# self.xml_root_.text = "TEXT"

		#self.xml_root_.getparent().insert(0, etree.Comment("\nFabian Ehrentraud, 2011\ne0725639@mail.student.tuwien.ac.at\n"))
		self.xml_root_.addprevious(etree.Comment(self.comment_))

		self.xml_root_.addprevious(etree.PI("xml-stylesheet", 'type="text/xsl" href="%s"'%(self.xsltstylesheet_)))

	def isFreshXml(self):
		#true if xml already contains study structure
		if self.xml_root_.find("stpl") is None:
			return True
		else:
			return False

	def wasUrlScraped(self, url):
		#checks whether given url was somewhen scraped already
		sources = self.xml_root_.findall("source")
		for s in sources:
			url_ = s.find("url")
			if url_ is not None and url_.text == url:
				return True #could also check whether query_date elements exists, but is not necessary
		return False

	def newestDate(self, referring_url):
		#gets the newest date of the given referring url
		sources = self.xml_root_.findall("source")
		for s in sources:
			ref_url = s.find("referring_url")
			if ref_url is not None and ref_url.text == referring_url:
				query_dates = s.findall("query_date")
				newestDate = None
				for d in query_dates:
					if newestDate == None or d.text > newestDate: #TODO make time stamp comparison more sophisticated FIXME
						newestDate = d.text
				return newestDate
		return None

	def checkSchema(self):
		#checks whether the given xml is correct according to the schema
		return self.checkSchema_(self.xml_root_)

	def checkSchema_(self, xml_root):
		#checks whether the given xml is correct according to the schema
		
		relaxng_doc = etree.parse(self.schema_)
		relaxng = etree.RelaxNG(relaxng_doc)

		#print(xmlschema.validate(doc))
		try:
			relaxng.assertValid(xml_root)
			return True
		except etree.DocumentInvalid:
			self.logger_.warning(relaxng.error_log)
			return False

	def writeXml(self, filename, backupfolder):
		#writes xml to the given filename
		self.writeXml_(self.xml_root_, filename, backupfolder)

	def writeXml_(self, xml_root, filename, backupfolder):
		#writes xml to the given filename
		self.logger_.info("Writing XML file %s backups", filename)
		xml = etree.tostring(xml_root.getroottree(), pretty_print=True, xml_declaration=True, encoding="utf-8")
		#print(xml) #unicode problem
		writedate = str(datetime.datetime.now()).replace(":",".").replace(" ","_")
		basename, extension = os.path.splitext(filename)
		
		#backup of original if it exists
		if os.path.exists(filename):
			os.renames(filename, backupfolder + basename + "_" + writedate + "_old" + extension)
		
		#write new
		f = open(filename, 'w')
		f.write(xml)
		f.close()
		
		#write backup of new
		f = open(backupfolder + basename + "_" + writedate + extension, "w")
		f.write(xml)
		f.close()

	def generateRss(self, rssfilename, backupfolder):
		result_tree = self.transformXslt_(self.rss_xslt_, backupfolder)
		self.writeXml_(result_tree, rssfilename, backupfolder)

	def transformXslt_(self, xsltfilename, backupfolder):
		xslt_root = self.readXml_(xsltfilename)
		transform = etree.XSLT(xslt_root)
		return transform(self.xml_root_).getroot()

	def getStpl(self, lva, createNonexistentNodes=False):
		#gets the given stpl in the xml or creates it

		#stpl_s = self.xml_root_.xpath('stpl')
		stpl_s = self.xml_root_.findall("stpl")
		for s in stpl_s:
			#print(etree.tostring(s))
			stplB = self.fuzzyEq_(lva.stpl, s.find("title").text)
			stpl_versionB = self.fuzzyEq_(lva.stpl_version, s.find("version").text)

			if(stplB and stpl_versionB):
				if lva.stpl_url: #does not let through ""
					#insert url after version (or title if it does not exist)
					if s.find("url") is not None:
						stpl_url_ = s.find("url")
					else:
						previous = s.find("version") if s.find("version") is not None else s.find("title")
						stpl_url_ = etree.Element("url")
						previous.addnext(stpl_url_)
					stpl_url_.text = lva.stpl_url.strip()
					
					self.didChange = True
					
				return s #return first matching
		
		if createNonexistentNodes:
			stpl = etree.SubElement(self.xml_root_, "stpl")
			stpl_title_ = etree.SubElement(stpl, "title")
			stpl_title_.text = (lva.stpl or "").strip()
			stpl_version_ = etree.SubElement(stpl, "version")
			stpl_version_.text = (lva.stpl_version or "").strip()
			stpl_url_ = etree.SubElement(stpl, "url")
			stpl_url_.text = (lva.stpl_url or "").strip()
			
			self.didChange = True

			return stpl
		else:
			raise PathElementNotFoundException("STPL %s %s not found"%(lva.stpl,lva.stpl_version))

	def getModul1(self, lva, createNonexistentNodes=False):
		#gets the given modul1 in the xml or creates it
		stpl = self.getStpl(lva, createNonexistentNodes=createNonexistentNodes)

		#modul1_s = stpl.xpath('modul1')
		modul1_s = stpl.findall("modul1")
		for m in modul1_s:
			#print(etree.tostring(m))
			modul1B = self.fuzzyEq_(lva.modul1, m.find("title").text)

			if(modul1B):
				if lva.modul1_iswahlmodulgruppe: #for inserting afterwards
					m.set("wahlmodulgruppe", "true")
					
					self.didChange = True
				
				return m #return first matching
				
		if createNonexistentNodes:
			modul1 = etree.SubElement(stpl, "modul1")
			if lva.modul1_iswahlmodulgruppe:
				modul1.set("wahlmodulgruppe", "true")
			modul1_title_ = etree.SubElement(modul1, "title")
			modul1_title_.text = (lva.modul1 or "").strip()
			
			self.didChange = True
		
			return modul1
		else:
			#print("Modul1%s not found"%(lva.modul1))
			raise PathElementNotFoundException("Modul1 %s not found"%(lva.modul1))

	def getModul2(self, lva, createNonexistentNodes=False):
		#gets the given modul2 in the xml or creates it
		modul1 = self.getModul1(lva, createNonexistentNodes)

		#modul2_s = modul1.xpath('modul2')
		modul2_s = modul1.findall("modul2")
		for m in modul2_s:
			#print(etree.tostring(m))
			modul2B = self.fuzzyEq_(lva.modul2, m.find("title").text)

			if(modul2B):
				return m #return first matching

		if createNonexistentNodes:
			modul2 = etree.SubElement(modul1, "modul2")
			modul2_title_ = etree.SubElement(modul2, "title")
			modul2_title_.text = (lva.modul2 or "").strip()
			
			self.didChange = True
		
			return modul2
		else:
			raise PathElementNotFoundException("Modul2 %s not found"%(lva.modul2))

	def getModul3(self, lva, createNonexistentNodes=False):
		#gets the given modul2 in the xml or creates it
		modul2 = self.getModul2(lva, createNonexistentNodes)

		#modul3_s = modul2.xpath('modul3')
		modul3_s = modul2.findall("modul3")
		for m in modul3_s:
			#print(etree.tostring(m))
			modul3B = self.fuzzyEq_(lva.modul3, m.find("title").text)

			if(modul3B):
				return m #return first matching

		if createNonexistentNodes:
			modul3 = etree.SubElement(modul2, "modul3")
			modul3_title_ = etree.SubElement(modul3, "title")
			modul3_title_.text = (lva.modul3 or "").strip()
			
			self.didChange = True
		
			return modul3
		else:
			raise PathElementNotFoundException("Modul3 %s not found"%(lva.modul3))

	def getModulX(self, lva, createNonexistentNodes=False):
		if lva.modul3:
			return self.getModul3(lva, createNonexistentNodes)
		elif lva.modul2:
			return self.getModul2(lva, createNonexistentNodes)
		elif lva.modul1:
			return self.getModul1(lva, createNonexistentNodes)
		else:
			raise Exception("No Modul for Fach %s %s (%s %s) not found"%(lva.fach,lva.fach_type,lva.fach_sws,lva.fach_ects))

	def getFach(self, lva, createNonexistentNodes=False):
		modul = self.getModulX(lva, createNonexistentNodes)

		#fach_s = modul.xpath('fach')
		fach_s = modul.findall("fach")
		for f in fach_s:
			#print(etree.tostring(f))
			fachB = self.fuzzyEq_(lva.fach, f.find("title").text, substringmatch=False)
			fach_typeB = self.fuzzyEq_(lva.fach_type, f.find("type").text)
			fach_swsB = self.fuzzyEq_(lva.fach_sws, f.find("sws").text)
			#fach_ectsB = self.fuzzyEq_(lva.fach_ects, f.find("ects").text)

			if(fachB and fach_typeB and fach_swsB): #ignore ects
			
				#update type, ects and sws - they must already exist
				fach_type_ = f.find("type")
				old_fach_type = fach_type_.text
				fach_type_.text = (lva.fach_type or "").strip()
				if fach_type_.text is None or fach_type_.text == "":
					fach_type_.text = old_fach_type #don't delete already existing content
				
				fach_sws_ = f.find("sws")
				old_fach_sws = fach_sws_.text
				fach_sws_.text = (lva.fach_sws or "").strip().replace(",",".")
				if len(fach_sws_.text) == 1:
					fach_sws_.text += ".0"
				if fach_sws_.text is None or fach_sws_.text == "":
					fach_sws_.text = old_fach_sws #don't delete already existing content
				
				fach_ects_ = f.find("ects")
				old_fach_ects = fach_ects_.text
				fach_ects_.text = (lva.fach_ects or "").strip().replace(",",".")
				if len(fach_ects_.text) == 1:
					fach_ects_.text += ".0"
				if fach_ects_.text is None or fach_ects_.text == "":
					fach_ects_.text = old_fach_ects #don't delete already existing content
				
				if old_fach_type != fach_type_.text or old_fach_sws != fach_sws_.text or old_fach_ects != fach_ects_.text: #TODO more than just type, SWS and ECTS
					self.logger_.info("Fach updated: %s %s %s %s", f.find("title").text, f.find("type").text, fach_sws_.text, fach_ects_.text)
					
					self.didChange = True
				
				return f #return first matching

		if createNonexistentNodes:
			fach = etree.SubElement(modul, "fach")
			fach_title_ = etree.SubElement(fach, "title")
			fach_title_.text = (lva.fach or "").strip()
			fach_type_ = etree.SubElement(fach, "type")
			fach_type_.text = (lva.fach_type or "").strip()
			fach_sws_ = etree.SubElement(fach, "sws")
			fach_sws_.text = (lva.fach_sws or "").strip().replace(",",".")
			if len(fach_sws_.text) == 1:
				fach_sws_.text += ".0"
			fach_ects_ = etree.SubElement(fach, "ects")
			fach_ects_.text = (lva.fach_ects or "").strip().replace(",",".")
			if len(fach_ects_.text) == 1:
				fach_ects_.text += ".0"

			self.logger_.info("New Fach: %s %s %s %s", fach_title_.text, fach_type_.text, fach_sws_.text, fach_ects_.text)
			
			self.didChange = True

			return fach
		else:
			raise PathElementNotFoundException("Fach %s %s (%s %s) not found"%(lva.fach,lva.fach_type,lva.fach_sws,lva.fach_ects))


	def getMatchingFach(self, lva):
		#searches a matching fach anywhere in the given xml
		#for legacy files, no need to provide lva.stpl,lva.stpl_version,lva.modul1,lva.modul2
		
		fach_s = self.xml_root_.xpath('//fach')
		for f in fach_s:
			#print(etree.tostring(f))
			fachB = self.fuzzyEq_(lva.fach, f.find("title").text, substringmatch=False)
			fach_typeB = self.fuzzyEq_(lva.fach_type, f.find("type").text, threshold=1.0)
			fach_swsB = self.fuzzyEq_(lva.fach_sws, f.find("sws").text)
			#fach_ectsB = self.fuzzyEq_(lva.fach_ects, f.find("ects").text)

			if(fachB and fach_typeB and fach_swsB): #ignore ects
				return f #return first matching

		raise PathElementNotFoundException("Fach %s %s (%s %s) not found"%(lva.fach,lva.fach_type,lva.fach_sws,lva.fach_ects))

	def createWahlFach(self, lva_stpl,lva_stpl_version,lva_modul1,lva_modul2,lva_modul3, lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects):
		xpath = "stpl"
		
		if lva_modul1:
			xpath += "/modul1[contains(title,'%s')]"%(lva_modul1)
		else:
			xpath += "/modul1"
		
		if lva_modul2:
			xpath += "/modul2[contains(title,'%s')]"%(lva_modul2)
		else:
			if lva_modul3:
				xpath += "/modul2"
		
		if lva_modul3:
			xpath += "/modul3[contains(title,'%s')]"%(lva_modul3)
		
		modul_s = self.xml_root_.xpath(xpath)
		#print(xpath)
		#print(modul_s)
		for m in modul_s:
			#print(etree.tostring(m))
			# TODO unify with same code in getFach

			fach_s = m.findall("fach")
			for f in fach_s:
				#print(etree.tostring(f))
				fachB = self.fuzzyEq_(lva_fach, f.find("title").text, substringmatch=False)
				fach_typeB = self.fuzzyEq_(lva_fach_type, f.find("type").text)
				fach_swsB = self.fuzzyEq_(lva_fach_sws, f.find("sws").text)
				#fach_ectsB = self.fuzzyEq_(lva_fach_ects, f.find("ects").text)

				if(fachB and fach_typeB and fach_swsB): #ignore ects
					return f

			fach = etree.SubElement(m, "fach")
			fach_title_ = etree.SubElement(fach, "title")
			fach_title_.text = (lva_fach or "").strip()
			fach_type_ = etree.SubElement(fach, "type")
			fach_type_.text = (lva_fach_type or "").strip()
			fach_sws_ = etree.SubElement(fach, "sws")
			fach_sws_.text = (lva_fach_sws or "").strip().replace(",",".")
			if len(fach_sws_.text) == 1:
				fach_sws_.text += ".0"
			fach_ects_ = etree.SubElement(fach, "ects")
			fach_ects_.text = (lva_fach_ects or "").strip().replace(",",".")
			if len(fach_ects_.text) == 1:
				fach_ects_.text += ".0"

			self.logger_.info("New Fach: %s %s %s %s", fach_title_.text, fach_type_.text, fach_sws_.text, fach_ects_.text)
			
			self.didChange = True

			return fach

		raise PathElementNotFoundException("Fach %s %s (%s %s) not found"%(lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects))

	def createMediaLegacyModul(self, lva_stpl,lva_stpl_version,lva_modul1,lva_modul2,lva_modul3):
		xpath = "stpl"
		
		if lva_modul1:
			xpath += "/modul1[contains(title,'%s')]"%(lva_modul1)
		else:
			xpath += "/modul1"
		
		if lva_modul2:
			xpath += "/modul2[contains(title,'%s')]"%(lva_modul2)
		else:
			xpath += "/modul2"
		
		modul_s = self.xml_root_.xpath(xpath)
		#print(xpath)
		#print(modul_s)
		for m in modul_s:
			m3_s = m.xpath("modul3[contains(title,'%s')]"%(lva_modul3))
			if len(m3_s) > 0:
				return m3_s[0]

			#print(etree.tostring(m))
			# TODO unify with same code in getModul3
			modul3 = etree.SubElement(m, "modul3")
			modul3_title_ = etree.SubElement(modul3, "title")
			modul3_title_.text = (lva_modul3 or "").strip()
			
			self.didChange = True

			return modul3

		raise PathElementNotFoundException("Fach %s %s (%s %s) not found"%(lva_fach,lva_fach_type,lva_fach_sws,lva_fach_ects))

	def addLva(self, lva, createNonexistentNodes=False, searchMatchingFach=False):
		""" adds an lva to the given xml """
		
		if searchMatchingFach:
			fach = self.getMatchingFach(lva) # TODO clear unneeded info for safety
		else:
			fach = self.getFach(lva, createNonexistentNodes) # TODO clear unneeded info for safety
		
		#for non-given lva.ects, search from fach
		lva.ects = lva.ects or fach.find("ects").text

		found_lva = None
		#lva_s = fach.xpath('lva')
		lva_s = fach.findall("lva")
		for l in lva_s:
			#print(etree.tostring(f))
			universityB = self.fuzzyEq_(lva.university, l.find("university").text)
			semesterB = self.fuzzyEq_(lva.semester, l.find("semester").text)
			titleB = self.fuzzyEq_(lva.title, l.find("title").text, substringmatch=False)
			keyB = self.fuzzyEq_(lva.key, l.find("key").text)
			typeB = self.fuzzyEq_(lva.type, l.find("type").text, threshold=1.0)
			#swsB = self.fuzzyEq_(lva.sws, l.find("sws").text, threshold=0.0)
			#ectsB = self.fuzzyEq_(lva.ects, l.find("ects").text, threshold=0.0)
			#infoB = self.fuzzyEq_(lva.info, l.find("info").text, threshold=0.0)
			#urlB = self.fuzzyEq_(lva.url, l.find("url").text, threshold=0.0)
			#professorB = self.fuzzyEq_(lva.professor, l.find("professor").text, threshold=0.0)
			if(universityB and semesterB and titleB and keyB and typeB): # ignore sws, ects, info, url and prof
				found_lva = l
				break #return first matching
				#return l

		#lva_e = found_lva or etree.SubElement(fach, "lva") #or: update existing lva #__nonzero__ will be changed in ElementTree
		lva_e = found_lva if found_lva is not None else etree.SubElement(fach, "lva") #or: update existing lva #__nonzero__ will be changed in ElementTree
		#lva_university_ = lva_e.find("university") or etree.SubElement(lva_e, "university") #or: update existing subelement #__nonzero__ will be changed in ElementTree
		lva_university_ = lva_e.find("university") if lva_e.find("university") is not None else etree.SubElement(lva_e, "university")
		lva_university_.text = (lva.university or "").strip()
		lva_semester_ = lva_e.find("semester") if lva_e.find("semester") is not None else etree.SubElement(lva_e, "semester")
		lva_semester_.text = (lva.semester or "").strip()
		lva_title_ = lva_e.find("title") if lva_e.find("title") is not None else etree.SubElement(lva_e, "title")
		lva_title_.text = (lva.title or "").strip()
		lva_key_ = lva_e.find("key") if lva_e.find("key") is not None else etree.SubElement(lva_e, "key")
		lva_key_.text = (lva.key or "").strip()
		lva_type_ = lva_e.find("type") if lva_e.find("type") is not None else etree.SubElement(lva_e, "type")
		lva_type_.text = (lva.type or "").strip()
		lva_sws_ = lva_e.find("sws") if lva_e.find("sws") is not None else etree.SubElement(lva_e, "sws")
		old_lva_sws = lva_sws_.text
		lva_sws_.text = (lva.sws or "").strip().replace(",",".")
		if len(lva_sws_.text) == 1:
			lva_sws_.text += ".0"
		lva_ects_ = lva_e.find("ects") if lva_e.find("ects") is not None else etree.SubElement(lva_e, "ects")
		old_lva_ects = lva_ects_.text
		lva_ects_.text = (lva.ects or "").strip().replace(",",".")
		if len(lva_ects_.text) == 1:
			lva_ects_.text += ".0"
		lva_info_ = lva_e.find("info") if lva_e.find("info") is not None else etree.SubElement(lva_e, "info")
		if "manuell" in (lva_info_.text or ""):
			self.logger_.info("Manually registered LVA overwritten")
			found_lva = None #to print out LVA details in the end of the function and update the query date
		if (lva_info_.text or "") != "" and (lva.info or "").strip() != "":
			self.logger_.info(u"Existing Info will be lost for Fach %s %s: %s", lva_title_.text, lva_type_.text, lva_info_.text)
			lva_info_.text = (lva.info or "").strip()
			self.logger_.info(u"New Info: %s", lva_info_.text)
			self.didChange = True
		lva_url_ = lva_e.find("url") if lva_e.find("url") is not None else etree.SubElement(lva_e, "url")
		lva_url_.text = (lva.url or "").strip()
		lva_professor_ = lva_e.find("professor") if lva_e.find("professor") is not None else etree.SubElement(lva_e, "professor")
		lva_professor_.text = (lva.professor or "").strip()
		
		#TODO this does not update the query date if some fields of an existing lva are updated. but would that be wanted?
		if found_lva is None or lva_e.find("query_date") is None:
			lva_query_date_ = lva_e.find("query_date") if lva_e.find("query_date") is not None else etree.SubElement(lva_e, "query_date")
			lva_query_date_.text = datetime.datetime.now().isoformat()
		
		if found_lva is None:
			self.logger_.info("New LVA: %s %s %s %s %s %s %s %s %s", lva_university_.text, lva_semester_.text, lva_title_.text, lva_key_.text, lva_type_.text, lva_sws_.text, lva_ects_.text, lva_info_.text, lva_professor_.text)
			self.didChange = True
		elif old_lva_sws != lva_sws_.text or old_lva_ects != lva_ects_.text: #TODO more than just SWS and ECTS
			self.logger_.info("LVA updated: %s %s %s %s %s %s %s %s %s", lva_university_.text, lva_semester_.text, lva_title_.text, lva_key_.text, lva_type_.text, lva_sws_.text, lva_ects_.text, lva_info_.text, lva_professor_.text)
			self.didChange = True
		"""
		else: #FIXME only for debugging
			raise Exception("Existing LVA: %s"%(lva_university_.text + " " + lva_semester_.text + " " + lva_title_.text + " " + lva_key_.text + " " + lva_type_.text + " " + lva_sws_.text + " " + lva_ects_.text + " " + lva_info_.text + " " + lva_professor_.text))
		"""

		return lva_e

	def addSource(self, url, query_date, referring_url=None):
		#adds an url source entry in the given xml
		
		found_source = None
		source_s = self.xml_root_.findall("source")
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
			self.xml_root_.insert(0, source)
			url_ = source.find("url") if source.find("url") is not None else etree.SubElement(source, "url")
			url_.text = (url or "")
			
			self.didChange = True
		
		if referring_url is not None:
			ref_url = source.find("referring_url")
			if ref_url is None:
				ref_url = etree.Element("referring_url")
				
				url_ = source.find("url")
				if source.find("url") is not None:
					url_.addnext(ref_url)
				else: #should not happen
					raise Exception("No URL element present in XML for %s"%(url))
			
				self.didChange = True
			
			ref_url.text = (referring_url or "")
		
		query_date_ = etree.SubElement(source, "query_date")
		query_date_.text = (query_date or "")


	""" fuzzy matching """

	def fuzzyEq_(self, wantedStr, compStr, threshold=0.89, substringmatch=True): #FIXME threshold
		#compares the two strings for approximate equalness
		#substringmatch=False still matches substrings that are contained between quotes
		
		#"E-Tutoring, Moderation von E-Learning" vs "eTutoring, Moderation von e-Learning" => ratio of 0.93
		#"Experimentelle Gestaltung von MM-Anwendungen + Präsentationsstrategien 1" vs "(4) Experiment. Gestaltung von MM-Anwend. + Präsentationsstrategien 1"  => ratio of 0.895
		#"Experimentelle Gestaltung von MM-Anwendungen + Präsentationsstrategien 2", "(4) Experiment. Gestaltung von MM-Anwend. + Präsentationsstrategien 1" => ratio of 0.88
		
		wantedStr = (wantedStr or "").strip().lower()
		compStr = (compStr or "").strip().lower()
		
		if (wantedStr == "vo" and compStr == "vu") or (wantedStr == "vu" and compStr == "vo"):
			return True # VO and VU are equivalent
		
		#numbers must be preserved except in Unterrichtspraktikum
		if "unterrichtspraktikum" not in wantedStr and "unterrichtspraktikum" not in compStr \
				and u"präsentationsstrategien 2" not in wantedStr and u"präsentationsstrategien 2" not in compStr:
			for s in wantedStr.split():
				try:
					i = int(s)
					if s not in compStr:
						return False
				except ValueError:
					pass

			for s in compStr.split():
				try:
					i = int(s)
					if s not in wantedStr:
						return False
				except ValueError:
					pass
		
		#warning: lvas "Unterrichtspraktikum Informatikdidaktik 1" and "Unterrichtspraktikum Informatikdidaktik 2" are both for fach "Unterrichtspraktikum Informatikdidaktik"
		fixes_wanted = ["(1)","(2)","(3)","(4)"] #(1)-(4) could lead to problems if those lvas were provided by Uni which does not categorize into fach
		for f in fixes_wanted:
			if f in wantedStr and f not in compStr: #but NOT the other way around
				return False

		#warning: "Knowledge Management" does not fit to "Knowledge Management im Bildungsbereich"
		fixes_comp = ["bildungsbereich"]
		for f in fixes_comp:
			if f in compStr and f not in wantedStr: #but NOT the other way around
				return False

		subfach = compStr.split('"')
		if len(subfach) >= 5:
			subfach1 = subfach[1]
			subfach2 = subfach[3]
			if difflib.SequenceMatcher(None, subfach1, wantedStr).ratio() >= threshold or difflib.SequenceMatcher(None, subfach2, wantedStr).ratio() >= threshold:
				return True
		
		#return(wantedStr.strip() == compStr.strip())
		if difflib.SequenceMatcher(None, wantedStr, compStr).ratio() >= threshold:
			return True

		#substringmatch because of:
		# "E-Commerce", "Online Communities und E-Commerce", "Secure E-commerce" are not the same
		# "Seminar aus Computergraphik", "Forschungsseminar aus Computergraphik und digitaler Bildverarbeitung" are not the same 
		# "Kommunikation", "Kommunikation und Moderation" are not the same
		if substringmatch and (wantedStr in compStr or compStr in wantedStr): #FIXME does not take account for spelling errors; problem with "E-Commerce"
			return True
		
		return False

			
""" program script """


"""
x="Bla %s"%(u"ÄäÖöÜüß")
print(x)
raise Exception(x) #FIXME no unicode exception messages
"""

#raise Exception()

logger.info("*** Informatikdidaktik Scraping started ***")

xml = STPLXML()

uniScraper = UniScraper()
tuScraper = TUScraper()
tuLegacyScraper = TULegacyScraper()

#open existing file if it exists or create new xml
xml.loadXml(xmlfilename, loadExisting=True, checkXmlSchema=True) #TODO loadExisting=True

#get structure
if xml.isFreshXml():
	tuScraper.scrape(xml, tiss, createNonexistentNodes=True, getLvas=False)

#getTU(xml, tiss, createNonexistentNodes=False, getLvas=False, reorderFach=True)

#get legacy lvas before adding other lvas
tuLegacyScraper.scrape(xml)

#get lvas from TU
tuScraper.scrape(xml, tiss, createNonexistentNodes=False)
tuScraper.scrape(xml, tiss_next, createNonexistentNodes=False)

#get lvas from Uni
uniScraper.scrape(xml, createNonexistentNodes=False)

"""
#check if generated xml is correct regarding rng
if(xml.checkSchema()):
	print("XML is valid")
else:
	print("XML is NOT valid")
"""

if xml.didChange:
	logger.info("Something has changed")
	#TODO send mail or something when special flag has been set

save = raw_input("Should the results be saved? (yes, no)\n")
save = (save or "").strip().lower()

if save == "y" or save == "yes":

	#write xml to file + backupfile
	xml.writeXml(filename=xmlfilename, backupfolder=backupfolder)

	#generate and write rss to file + backupfile
	xml.generateRss(rssfilename=rss_xml, backupfolder=backupfolder)
