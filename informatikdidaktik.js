/*
Fabian Ehrentraud, 2011-02-20
e0725639@mail.student.tuwien.ac.at
Licensed under the Open Software License (OSL 3.0)
*/

function hideshowDiv(id){
	if(document.getElementById(id).getAttribute("hide") == "true"){
		document.getElementById(id).setAttribute("hide","false");
	}else{
		document.getElementById(id).setAttribute("hide","true"); /*custom attribute which hides in css*/
	}
}

function hideshowDivNoprint(id,idPrint){
	if(document.getElementById(id).getAttribute("hide") == "true"){
		document.getElementById(id).setAttribute("hide","false");
		document.getElementById(idPrint).setAttribute("noPrint","true");
	}else{
		document.getElementById(id).setAttribute("hide","true"); /*custom attribute which hides in css*/
		document.getElementById(idPrint).setAttribute("noPrint","true");
	}
}

function hideAllDiv(name){ /*name can be modulgruppe, modul or fach*/
	var elements = document.getElementsByName(name);
	for (var i=0; i < elements.length; i++) {
		elements[i].setAttribute("hide","true");
	}
}

function showAllDiv(name){
	var elements = document.getElementsByName(name);
	for (var i=0; i < elements.length; i++) {
		elements[i].setAttribute("hide","false");
	}
}

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

function showOldestDate(showeverything, date){
	var rows = document.getElementsByName("lvarow");
	for (var i=0; i < rows.length; i++) {
		if(showeverything || rows[i].getAttribute("query_date") >= date) {
			rows[i].setAttribute("hiderow","false");
		} else {
			rows[i].setAttribute("hiderow","true");
		}
	}
	
	var tables = document.getElementsByName("lvatable");
	for (var i=0; i < tables.length; i++) {
		if(showeverything) {
			/*custom attribute which hides in css*/
			tables[i].parentNode.setAttribute("nocontent","false");
		} else {
			tables[i].parentNode.setAttribute("nocontent","true"); /*hide parent div*/
			var subrows = tables[i].firstChild.childNodes; //firstChild is tbody
			for (var j=0; j < subrows.length; j++) {
				if(subrows[j].hasChildNodes()  &&  subrows[j].getAttribute("hiderow") == "false") {
					tables[i].parentNode.setAttribute("nocontent","false");
					break;
				}
			}
		}
	}
}
