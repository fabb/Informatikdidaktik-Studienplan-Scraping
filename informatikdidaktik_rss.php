<!--
Fabian Ehrentraud, 2011-02-24
e0725639@mail.student.tuwien.ac.at
https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
Licensed under the Open Software License (OSL 3.0)
Needs PHP compiled with XML and XSL support
Transforms the given XML file via XSLT to an RSS feed
Generating the RSS feed statically when generating the original XML file should be considered as the PHP method unnecessarily uses server resources
-->


<?php 

//allocate a new XSLT processor 
$xh = xslt_create(); 

//process the document, returning the result into the $result variable 
$result = xslt_process($xh, 'informatikdidaktik.xml', 'informatikdidaktik_rss.xslt'); 
if ($result) { 
    print $result; 
} 
else { 
    print "Transformation error: " . xslt_error($xh) .  
    print ", error code: " . xslt_errno($xh); 
} 

xslt_free($xh); 

?>