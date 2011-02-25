/*
Fabian Ehrentraud, 2011-02-25
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

	document.querySelectorAll('.mygroup') //returns all elements with class="mygroup"
	document.querySelectorAll('option[selected="selected"]') //returns the default selected option within each SELECT menu
	document.querySelectorAll('#mytable tr>td:nth-of-type(1)') //returns the first cell within each table row of "mytable"
	document.querySelectorAll('#biography, #gallery') //returns both elements "#biography" and "#gallery" (inclusive)
	
	getElementsByName
	querySelectorAll("*[name~="XXX"]")
	querySelectorAll('*[name~="' + name + '"]')
*/

/*
hides or shows the element with the given ID
by assigning a custom attribute which is hidden by css
inverts the current visibility
element does not necessarily have to be a DIV
*/
function hideshowDiv(id){
	if(document.getElementById(id).getAttribute("data-hide") == "true"){
		document.getElementById(id).setAttribute("data-hide","false");
	}else{
		document.getElementById(id).setAttribute("data-hide","true");
	}
}

/*
hides or shows the elements with the first given name
by assigning a custom attribute which is hidden by css
inverts the current visibility
also assigns an attribute to the second given ID
which will then not be printed if the first element is hidden
*/
function hideshowLiNoprint(name,idPrint){
	if(document.getElementById(idPrint).getAttribute("data-noPrint") == "true"){
		var elements = document.querySelectorAll('*[data-name~="' + name + '"]');
		for (var i=0; i < elements.length; i++) {
			elements[i].setAttribute("data-hide","false");
		}
		document.getElementById(idPrint).setAttribute("data-noPrint","false");
	}else{
		var elements = document.querySelectorAll('*[data-name~="' + name + '"]');
		for (var i=0; i < elements.length; i++) {
			elements[i].setAttribute("data-hide","true");
		}
		document.getElementById(idPrint).setAttribute("data-noPrint","true");
	}
}

/*
hides all elements with the given NAME
by assigning a custom attribute which is hidden by css
element does not necessarily have to be a DIV
*/
function hideAllDiv(name){ /*name can be modulgruppe, modul or fach*/
	var elements = document.querySelectorAll('*[data-name~="' + name + '"]');
	for (var i=0; i < elements.length; i++) {
		elements[i].setAttribute("data-hide","true");
	}
}

/*
shows all elements with the given NAME
by assigning a custom attribute which is (not) hidden by css
element does not necessarily have to be a DIV
*/
function showAllDiv(name){
	var elements = document.querySelectorAll('*[data-name~="' + name + '"]');
	for (var i=0; i < elements.length; i++) {
		elements[i].setAttribute("data-hide","false");
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

	var elements = document.querySelectorAll('*[data-name~="semesters"]');
	for (var i=0; i < elements.length; i++) {
		var semesters = elements[i].childNodes;
		var highlight = false;
		for (var j=0; j < semesters.length; j++) {
			if(semesters[j].hasChildNodes()  &&  semesters[j].getAttribute("data-name") == "semester") {
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
	var rows = document.querySelectorAll('*[data-name~="lvarow"]');
	for (var i=0; i < rows.length; i++) {
		if(showeverything || rows[i].getAttribute("data-query_date") >= date) {
			rows[i].setAttribute("data-hiderow_date","false");
		} else {
			rows[i].setAttribute("data-hiderow_date","true");
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
	var elements = document.querySelectorAll('*[data-name~="university"]');
	for (var i=0; i < elements.length; i++) {
		if(showeverything || (elements[i].hasChildNodes() && elements[i].firstChild.nodeValue == university)) {
			elements[i].parentNode.setAttribute("data-hiderow_university","false");
		} else {
			elements[i].parentNode.setAttribute("data-hiderow_university","true");
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
	var rows = document.querySelectorAll('*[data-name~="lvarow"]');
	for (var i=0; i < rows.length; i++) {
		if(hide && String(rows[i].getAttribute("class")).indexOf("currentlva") == -1) {
			rows[i].setAttribute("data-hiderow_semester","true");
		} else {
			rows[i].setAttribute("data-hiderow_semester","false");
		}
	}	
	
	propagateVisibility(false);
}

/*
assigns a custom attribute to elements in the DOM hierarchy
to indicate that they do/don't contain lvas
used for hiding empty categories
hides all categories containing hidden lvas either by data-hiderow_date or data-hiderow_semester or data-hiderow_university
showeverything should not be used with true unless it can safely be said that all occurrences of data-hiderow_* are false
*/
function propagateVisibility(showeverything) {	
	/*at first hide everything*/
	var fachs = document.querySelectorAll('*[data-name~="fach"]');
	for (var i=0; i < fachs.length; i++) {
		fachs[i].setAttribute("data-nocontent","true");
	}
	var wholefachs = document.querySelectorAll('*[data-name~="wholefach"]');
	for (var i=0; i < wholefachs.length; i++) {
		wholefachs[i].setAttribute("data-nolvas","true");
	}
	var wholemoduls = document.querySelectorAll('*[data-name~="wholemodul"]');
	for (var i=0; i < wholemoduls.length; i++) {
		wholemoduls[i].setAttribute("data-nolvas","true");
	}
	var wholemodulgruppes = document.querySelectorAll('*[data-name~="wholemodulgruppe"]');
	for (var i=0; i < wholemodulgruppes.length; i++) {
		wholemodulgruppes[i].setAttribute("data-nolvas","true");
	}

	var tables = document.querySelectorAll('*[data-name~="lvatable"]');
	for (var i=0; i < tables.length; i++) {
		if(showeverything) {
			//TODO parentNode method not very change-proof (XPath?)
			tables[i].parentNode.setAttribute("data-nocontent","false"); /*fach*/
			tables[i].parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholefach*/
			tables[i].parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodul*/
			tables[i].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodulgruppe*/
		} else {
			var subrows = tables[i].firstChild.childNodes; //firstChild is tbody
			for (var j=0; j < subrows.length; j++) {
				if(subrows[j].hasChildNodes()  &&  subrows[j].getAttribute("data-hiderow_date") != "true" && subrows[j].getAttribute("data-hiderow_semester") != "true" && subrows[j].getAttribute("data-hiderow_university") != "true") {
					//TODO parentNode method not very change-proof (XPath?)
					tables[i].parentNode.setAttribute("data-nocontent","false"); /*fach*/
					tables[i].parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholefach*/
					tables[i].parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodul*/
					tables[i].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodulgruppe*/
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
		document.getElementById("content").setAttribute("data-hideempty","true");
	}else{
		document.getElementById("content").setAttribute("data-hideempty","false");
	}
}
