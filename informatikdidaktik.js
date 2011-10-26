/*
Fabian Ehrentraud, 2011-10-26
e0725639@mail.student.tuwien.ac.at
https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
Licensed under the Open Software License (OSL 3.0)
Utilizes html5 localStorage
*/

/*
could use utf-8 as it is inluded with charset="utf-8"
*/

/*
TODO
	instead of unsafe .parentNode use something more robust
*/


// initializations when window/body has been loaded
window.addEventListener("load", onLoad, false);


/*
code that should be executed when the document is loaded/refreshed
stores the current date in localStorage
note that localStorage is only meant to work when the document is loaded from a domain and not a file - but only IE8 is strict enough to follow this
*/
function onLoad() {
	document.controls.reset();
	
	init_controls();

	writeDate();
	
	var today = new Date();
	var year = String(today.getFullYear());
	var month = String("0").concat(String(today.getMonth()+1));
	month = month.substr(month.length-2);
	var day = String("0").concat(String(today.getDate()));
	day = day.substr(day.length-2);
	
	var date = year.concat("-").concat(month).concat("-").concat(day);
	
	if(localStorage) localStorage.visitdate = date;
	
	hideshowLiNoprint('quelle','quellen');
}

// initializes control elements
// not done in html code to separate code and content even more
function init_controls() {
	var nonprinters = document.querySelectorAll('*[data-name~="hider_nonprinter"]');
	for(var i = nonprinters.length; i--; ) {
		var handler = function(e){
			hideshowLiNoprint(e.currentTarget.getAttribute("data-hideshows"), e.currentTarget.getAttribute("data-nonprints"));
		};
		nonprinters[i].addEventListener("click", handler, false);
	}
	
	var hiders = document.querySelectorAll('*[data-name~="hider"]');
	for(var i = hiders.length; i--; ) {
		var handler = function(e){
			hideshowDiv(e.currentTarget.getAttribute("data-hideshows"))
		};
		hiders[i].addEventListener("click", handler, false);
	}
	
	var university_selects = document.querySelectorAll('*[name~="universitySelect"]');
	for(var i = university_selects.length; i--; ) {
		var handler = function(e){
			showUniversity(e.currentTarget.selectedIndex==0, e.currentTarget.options[e.currentTarget.selectedIndex].value);
		};
		university_selects[i].addEventListener("change", handler, false);
	}
	
	var semester_select = document.querySelectorAll('*[name~="semesterSelect"]');
	for(var i = semester_select.length; i--; ) {
		var handler = function(e){
			highlightDiv(e.currentTarget.options[e.currentTarget.selectedIndex].value);
			var hideolder_check = document.querySelectorAll('*[name~="hideolderCheck"]');
			if(hideolder_check.length > 0){
				hideold(hideolder_check[0].checked);
			}
		};
		semester_select[i].addEventListener("change", handler, false);
	}

	var hideolder_check = document.querySelectorAll('*[data-name~="hideolderCheck"]');
	for(var i = hideolder_check.length; i--; ) {
		var handler = function(e){
			var input = e.currentTarget.querySelector('input');
			if(!(e.target instanceof HTMLInputElement))
				input.checked = !input.checked;
			hideold(input.checked)
		};
		hideolder_check[i].addEventListener("click", handler, false);
	}
	
	var date_select = document.querySelectorAll('*[name~="dateSelect"]');
	for(var i = date_select.length; i--; ) {
		var handler = function(e){
			showOldestDate(e.currentTarget.selectedIndex==0, e.currentTarget.options[e.currentTarget.selectedIndex].value);
		};
		date_select[i].addEventListener("change", handler, false);
	}
	
	var hideheaders_check = document.querySelectorAll('*[data-name~="hideheadersCheck"]');
	for(var i = hideheaders_check.length; i--; ) {
		var handler = function(e){
			var input = e.currentTarget.querySelector('input');
			if(!(e.target instanceof HTMLInputElement))
				input.checked = !input.checked;
			hideheaders(input.checked)
		};
		hideheaders_check[i].addEventListener("click", handler, false);
	}
	
	var hideempty_check = document.querySelectorAll('*[data-name~="hideemptyCheck"]');
	for(var i = hideempty_check.length; i--; ) {
		var handler = function(e){
			var input = e.currentTarget.querySelector('input');
			if(!(e.target instanceof HTMLInputElement))
				input.checked = !input.checked;
			hideempty(input.checked)
		};
		hideempty_check[i].addEventListener("click", handler, false);
	}
	
	var hideuni_check = document.querySelectorAll('*[data-name~="hideuniCheck"]');
	for(var i = hideuni_check.length; i--; ) {
		var handler = function(e){
			var input = e.currentTarget.querySelector('input');
			if(!(e.target instanceof HTMLInputElement))
				input.checked = !input.checked;
			hideuni(input.checked)
		};
		hideuni_check[i].addEventListener("click", handler, false);
	}
	
	var modul1_button = document.querySelectorAll('*[name~="modul1Button"]');
	for(var i = modul1_button.length; i--; ) {
		var handler = function(e){
			var hideheaders_check = document.querySelectorAll('*[name~="hideheadersCheck"]');
			if(hideheaders_check.length == 0 || !hideheaders_check[0].checked){
				hideAllDiv('modul1');
				showAllDiv('modul2');
				showAllDiv('wahlmodul');
				showAllDiv('fach');
			}
		};
		modul1_button[i].addEventListener("click", handler, false);
	}
	
	var modul2_button = document.querySelectorAll('*[name~="modul2Button"]');
	for(var i = modul2_button.length; i--; ) {
		var handler = function(e){
			var hideheaders_check = document.querySelectorAll('*[name~="hideheadersCheck"]');
			if(hideheaders_check.length == 0 || !hideheaders_check[0].checked){
				showAllDiv('modul1');
				hideAllDiv('modul2');
				hideAllDiv('wahlmodul');
				showAllDiv('fach');
			}
		};
		modul2_button[i].addEventListener("click", handler, false);
	}
	
	var fach_button = document.querySelectorAll('*[name~="fachButton"]');
	for(var i = fach_button.length; i--; ) {
		var handler = function(e){
			var hideheaders_check = document.querySelectorAll('*[name~="hideheadersCheck"]');
			if(hideheaders_check.length == 0 || !hideheaders_check[0].checked){
				showAllDiv('modul1');
				showAllDiv('modul2');
				hideAllDiv('wahlmodul');
				hideAllDiv('fach');
			}
		};
		fach_button[i].addEventListener("click", handler, false);
	}
	
	var all_button = document.querySelectorAll('*[name~="allButton"]');
	for(var i = all_button.length; i--; ) {
		var handler = function(e){
			showAllDiv('modul1');
			showAllDiv('modul2');
			showAllDiv('wahlmodul');
			showAllDiv('fach');
		};
		all_button[i].addEventListener("click", handler, false);
	}
}

/*
this is an expensive workaround for correctly redrawing in IE and Safari
*/
function redrawFix() {
	var element = document.getElementsByTagName("body")[0];
	element.className = element.className;
}

/*
writes the last visit date from localStorage to a div in the document
*/
function writeDate() {
	if(localStorage && localStorage.visitdate){
		document.querySelector('*[data-name~="lastvisitdate_div"]').removeAttribute("hidden");
		document.querySelector('*[data-name~="lastvisitdate"]').appendChild(document.createTextNode(localStorage.visitdate));
	}

	redrawFix();
}

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

	redrawFix();
}

/*
hides or shows the elements with the first given name
by assigning a custom attribute which is hidden by css
inverts the current visibility
also assigns an attribute to the second given ID
which will then not be printed if the first element is hidden
*/
function hideshowLiNoprint(name,idPrint){
	if(document.getElementById(idPrint).getAttribute("data-no_print") == "true"){
		if(name){
			var elements = document.querySelectorAll('*[data-name~="' + name + '"]');
			for (var i=0; i < elements.length; i++) {
				elements[i].setAttribute("data-hide","false");
			}
		}
		document.getElementById(idPrint).setAttribute("data-no_print","false");
	}else{
		if(name){
			var elements = document.querySelectorAll('*[data-name~="' + name + '"]');
			for (var i=0; i < elements.length; i++) {
				elements[i].setAttribute("data-hide","true");
			}
		}
		document.getElementById(idPrint).setAttribute("data-no_print","true");
	}

	redrawFix();
}

/*
hides all elements with the given NAME
by assigning a custom attribute which is hidden by css
element does not necessarily have to be a DIV
*/
function hideAllDiv(name){ /*name can be modul1, modul2 or fach*/
	var elements = document.querySelectorAll('*[data-name~="' + name + '"]');
	for (var i=0; i < elements.length; i++) {
		elements[i].setAttribute("data-hide","true");
	}

	redrawFix();
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

	redrawFix();
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

	redrawFix();
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
	var wholemodul2s = document.querySelectorAll('*[data-name~="wholemodul2"]');
	for (var i=0; i < wholemodul2s.length; i++) {
		wholemodul2s[i].setAttribute("data-nolvas","true");
	}
	var wholemodul1s = document.querySelectorAll('*[data-name~="wholemodul1"]');
	for (var i=0; i < wholemodul1s.length; i++) {
		wholemodul1s[i].setAttribute("data-nolvas","true");
	}

	var tables = document.querySelectorAll('*[data-name~="lvatable"]');
	for (var i=0; i < tables.length; i++) {
		if(showeverything) {
			//TODO parentNode method not very change-proof (XPath?)
			tables[i].parentNode.setAttribute("data-nocontent","false"); /*fach*/
			tables[i].parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholefach*/
			tables[i].parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodul2*/
			tables[i].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodul1*/
		} else {
			var subrows = tables[i].firstChild.childNodes; //firstChild is tbody
			for (var j=0; j < subrows.length; j++) {
				if(subrows[j].hasChildNodes()  &&  subrows[j].getAttribute("data-hiderow_date") != "true" && subrows[j].getAttribute("data-hiderow_semester") != "true" && subrows[j].getAttribute("data-hiderow_university") != "true") {
					//TODO parentNode method not very change-proof (XPath?)
					tables[i].parentNode.setAttribute("data-nocontent","false"); /*fach*/
					tables[i].parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholefach*/
					tables[i].parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodul2*/
					tables[i].parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.setAttribute("data-nolvas","false"); /*wholemodul1*/
					break;
				}
			}
		}
	}

	redrawFix();
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

	redrawFix();
}

/*
assigngs a custom attribute to the ID "content"
which hides/shows (according to the given parameter hide) by css all child elements which have got certain other attributes
*/
function hideuni(hide) {
	if(hide){
		document.getElementById("content").setAttribute("data-hideuni","true");
	}else{
		document.getElementById("content").setAttribute("data-hideuni","false");
	}

	redrawFix();
}

/*
assigngs a custom attribute to the ID "content"
which hides/shows (according to the given parameter hide) by css all child elements which are headers
*/
function hideheaders(hide) {
	if(hide){
		showAllDiv('modul1');
		showAllDiv('modul2');
		showAllDiv('fach');
		document.getElementById("content").setAttribute("data-hideheaders","true");
	}else{
		document.getElementById("content").setAttribute("data-hideheaders","false");
	}
	
	redrawFix();
}
