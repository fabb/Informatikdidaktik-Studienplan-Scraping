/*
Fabian Ehrentraud, 2011-02-19
e0725639@mail.student.tuwien.ac.at
Licensed under the Open Software License (OSL 3.0)
*/

function hideshowDiv(id){
	if(document.getElementById(id).style.display == "none"){
		document.getElementById(id).style.display = "block";
	}else{
		document.getElementById(id).style.display = "none";
	}
}

function hideAllDiv(name){ /*name can be modulgruppe, modul or fach*/
	var elements = document.getElementsByName(name);
	for (var i=0; i < elements.length; i++) {
		elements[i].style.display = "none";
	}
}

function showAllDiv(name){
	var elements = document.getElementsByName(name);
	for (var i=0; i < elements.length; i++) {
		elements[i].style.display = "block";
	}
}

function highlightDiv(semester){
	var yearBeforeSemester = String((parseInt(semester.substring(0,4)) - 1)).concat(semester.substring(4,5));

	var elements = document.getElementsByName("semesters");
	for (var i=0; i < elements.length; i++) {
		semesters = elements[i].childNodes;
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
