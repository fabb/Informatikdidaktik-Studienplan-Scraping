/*
Fabian Ehrentraud, 2011-02-24
e0725639@mail.student.tuwien.ac.at
https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
Licensed under the Open Software License (OSL 3.0)
*/

/*
could use utf-8
*/

/*
TODO
	instead of unsafe .parentNode use something more robust
*/

/*
hides or shows the element with the given ID
by assigning a custom attribute which is hidden by css
inverts the current visibility
element does not necessarily have to be a DIV
*/
function hideshowDiv(id){
	if(document.getElementById(id).getAttribute("hide") == "true"){
		document.getElementById(id).setAttribute("hide","false");
	}else{
		document.getElementById(id).setAttribute("hide","true");
	}
}

/*
hides or shows the element with the first given ID
by assigning a custom attribute which is hidden by css
inverts the current visibility
element does not necessarily have to be a DIV
also assigns an attribute to the second given ID
which will then not be printed if the first element is hidden
*/
function hideshowDivNoprint(id,idPrint){
	if(document.getElementById(id).getAttribute("hide") == "true"){
		document.getElementById(id).setAttribute("hide","false");
		document.getElementById(idPrint).setAttribute("noPrint","false");
	}else{
		document.getElementById(id).setAttribute("hide","true");
		document.getElementById(idPrint).setAttribute("noPrint","true");
	}
}

/*
hides all elements with the given NAME
by assigning a custom attribute which is hidden by css
element does not necessarily have to be a DIV
*/
function hideAllDiv(name){ /*name can be modulgruppe, modul or fach*/
	var elements = document.getElementsByName(name);
	for (var i=0; i < elements.length; i++) {
		elements[i].setAttribute("hide","true");
	}
}

/*
shows all elements with the given NAME
by assigning a custom attribute which is (not) hidden by css
element does not necessarily have to be a DIV
*/
function showAllDiv(name){
	var elements = document.getElementsByName(name);
	for (var i=0; i < elements.length; i++) {
		elements[i].setAttribute("hide","false");
	}
}

/*
highlights all rows which enclose the given semester
by assigning a class attribute which is hidden by css
element does not necessarily have to be a DIV
also directly underlines all semester strings one year before the given one
*/
function highlightDiv(semester){
	var yearBeforeSemester = String((parseInt(semester.substring(0,4)) - 1)).concat(semester.substring(4,5));

	var elements = document.getElementsByName("semesters");
	for (var i=0; i < elements.length; i++) {
		var semesters = elements[i].childNodes;
		var highlight = false;
		for (var j=0; j < semesters.length; j++) {
			if(semesters[j].hasChildNodes()  &&  semesters[j].getAttribute("name") == "semester") {
				if(semesters[j].firstChild.nodeValue == semester) {
					highlight = true;
				}
				
				if(highlight == false  &&  semesters[j].firstChild.nodeValue == yearBeforeSemester) {
					semesters[j].setAttribute("class","probableLva");
				} else {
					semesters[j].setAttribute("class","");
				}
			}
		}
		if(highlight) {
			elements[i].parentNode.setAttribute("class","currentlva");
		} else {
			elements[i].parentNode.setAttribute("class","");
		}
	}
}

/*
hides older lvas than given date
assigns a custom attribute to elements in the DOM hierarchy
to indicate that they do/don't contain lvas
used for hiding empty categories
*/
function showOldestDate(showeverything, date){
	var rows = document.getElementsByName("lvarow");
	for (var i=0; i < rows.length; i++) {
		if(showeverything || rows[i].getAttribute("query_date") >= date) {
			rows[i].setAttribute("hiderow_date","false");
		} else {
			rows[i].setAttribute("hiderow_date","true");
		}
	}
	
	propagateVisibility(false);
}

/*
hides lvas from other universities than the given one
assigns a custom attribute to elements in the DOM hierarchy
to indicate that they do/don't contain lvas
*/
function showUniversity(showeverything, university){
	var elements = document.getElementsByName("university");
	for (var i=0; i < elements.length; i++) {
		if(showeverything || (elements[i].hasChildNodes() && elements[i].firstChild.nodeValue == university)) {
			elements[i].parentNode.setAttribute("hiderow_university","false");
		} else {
			elements[i].parentNode.setAttribute("hiderow_university","true");
		}
	}
	
	propagateVisibility(false);
}

/*
hides non-highlighted lvas
assigns a custom attribute to elements in the DOM hierarchy
to indicate that they do/don't contain lvas
used for hiding empty categories
*/
function hideold(hide) {
	var rows = document.getElementsByName("lvarow");
	for (var i=0; i < rows.length; i++) {
		if(hide && String(rows[i].getAttribute("class")).indexOf("currentlva") == -1) {
			rows[i].setAttribute("hiderow_semester","true");
		} else {
			rows[i].setAttribute("hiderow_semester","false");
		}
	}	
	
	propagateVisibility(false);
}

/*
assigns a custom attribute to elements in the DOM hierarchy
to indicate that they do/don't contain lvas
used for hiding empty categories
hides all categories containing hidden lvas either by hiderow_date or hiderow_semester
showeverything should not be used with true unless it can safely be said that all occurrences of hiderow_* are false
*/
function propagateVisibility(showeverything) {	
	/*at first hide everything*/
	var fachs = document.getElementsByName("fach");
	for (var i=0; i < fachs.length; i++) {
		fachs[i].setAttribute("nocontent","true");
	}
	var wholefachs = document.getElementsByName("wholefach");
	for (var i=0; i < wholefachs.length; i++) {
		wholefachs[i].setAttribute("nolvas","true");
	}
	var wholemoduls = document.getElementsByName("wholemodul");
	for (var i=0; i < wholemoduls.length; i++) {
		wholemoduls[i].setAttribute("nolvas","true");
	}
	var wholemodulgruppes = document.getElementsByName("wholemodulgruppe");
	for (var i=0; i < wholemodulgruppes.length; i++) {
		wholemodulgruppes[i].setAttribute("nolvas","true");
	}

	var tables = document.getElementsByName("lvatable");
	for (var i=0; i < tables.length; i++) {
		if(showeverything) {
			//TODO parentNode method not very change-proof (XPath?)
			tables[i].parentNode.setAttribute("nocontent","false"); /*fach*/
			tables[i].parentNode.parentNode.setAttribute("nolvas","false"); /*wholefach*/
			tables[i].parentNode.parentNode.parentNode.parentNode.setAttribute("nolvas","false"); /*wholemodul*/
			tables[i].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.setAttribute("nolvas","false"); /*wholemodulgruppe*/
		} else {
			var subrows = tables[i].firstChild.childNodes; //firstChild is tbody
			for (var j=0; j < subrows.length; j++) {
				if(subrows[j].hasChildNodes()  &&  subrows[j].getAttribute("hiderow_date") != "true" && subrows[j].getAttribute("hiderow_semester") != "true" && subrows[j].getAttribute("hiderow_university") != "true") {
					//TODO parentNode method not very change-proof (XPath?)
					tables[i].parentNode.setAttribute("nocontent","false"); /*fach*/
					tables[i].parentNode.parentNode.setAttribute("nolvas","false"); /*wholefach*/
					tables[i].parentNode.parentNode.parentNode.parentNode.setAttribute("nolvas","false"); /*wholemodul*/
					tables[i].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.setAttribute("nolvas","false"); /*wholemodulgruppe*/
					break;
				}
			}
		}
	}
}

/*
assigngs a custom attribute to the ID "content"
which hides/shows (according to the given parameter hide) by css all child elements which have got certain other attributes
*/
function hideempty(hide) {
	if(hide){
		document.getElementById("content").setAttribute("hideempty","true");
	}else{
		document.getElementById("content").setAttribute("hideempty","false");
	}
}
