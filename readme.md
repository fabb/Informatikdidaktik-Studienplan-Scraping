Informatikdidaktik Studienplan Scraping
====================

Scrapes Uni and TU Vienna websites for courses from study Informatikdidaktik and stores them in an XML which can be viewed in the browser due to XSLT.


Prerequisites
---------------------

For running the Python script, *Python 2.7* is necessary (maybe a lower version works too) and the Python library *lxml*.

The generated xml file can be viewed in IE, Firefox, Opera, Safari or Chrome. Due to a bug in Chrome, it only works if the xml is located on a web url. The javascript uses standard conform DOM, so IE7 or lower are *not* supported for the interactive parts.

Printing the page in the webbrowser will be done in an inksaving manner with custom CSS code. Printing is *not* recommended with Chrome or Safari.


Used Technologies
---------------------

+ Python 2.7
+ Scraping with Python Library *lxml*
+ XML
+ XML Schema
+ XPath
+ XSLT 1.0 - unfortunately the current browsers do not support XSLT 2.0 which would provide relieving functions for string comparison and the like
+ XHTML
+ CSS
+ JavaScript and DOM
+ RSS
+ (PHP)
+ (soon) Cookies
