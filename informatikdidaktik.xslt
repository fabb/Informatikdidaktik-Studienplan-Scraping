<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="xs fn">

<!--
Fabian Ehrentraud, 2011-03-20
e0725639@mail.student.tuwien.ac.at
https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
Licensed under the Open Software License (OSL 3.0)
-->

<!--
TODO
	save collapse state to localStorage
	checkboxes for done lvas, store to localStorage / loadable file
	show ects and contained elements in headers
-->

	<!-- use method html to avoid self closing tags; xslt 2.0 would support method xhtml -->
	<!-- media-type text/xml or application/xml or application/xhtml+xml does not allow to use the HTML DOM and breaks the used Javascript -->
	<!--xsl:output method="html" media-type="text/html" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" cdata-section-elements="script style" indent="yes" encoding="utf-8"/-->
	<!-- html5 has short doctype, not even doctype-system="about:legacy-compat" should be necessary, but is here as some XSLT processors hide the doctype as a whole if it is missing -->
	<!-- XHTML version of html5 should not need a doctype at all, but that leads to problems -->
	<xsl:output method="html" media-type="text/html" doctype-system="about:legacy-compat" cdata-section-elements="script style" indent="yes" encoding="utf-8"/>
	

	<!-- remove ", ', spaces, comma, braces and + from variable name -->
	<xsl:template name="removeSpecialChars">
		<xsl:param name="inputstring"/>
		
		<!-- workaround for XSLT 1.0 where handling both apostrophes and quotes in one string is a bit complicated -->
		<xsl:variable name="apos">'</xsl:variable>
		
		<xsl:value-of select="translate($inputstring,concat($apos,'&quot; ,()+'),'_______')"/>
	</xsl:template>


	<!-- calculate whether given fach contains only lvas at one university -->
	<xsl:template name="multipleUniversities">
		<xsl:param name="fachnodes"/>
		
		<!--xsl:value-of select="count(lva[not(university = preceding-sibling::lva/university)]) &gt; 1"/-->
		
		<!-- dirty XSLT1 hack to check if condition is true for all -->
		<xsl:variable name="multiList">
			<xsl:for-each select="$fachnodes">
				<xsl:value-of select="count(./lva[not(./university = ./preceding-sibling::lva/university)]) &gt; 1"/>
				<xsl:text> </xsl:text>
			</xsl:for-each>
		</xsl:variable>
		<xsl:value-of select="not(contains($multiList, 'false'))"/>
	</xsl:template>
		

	
	
	<xsl:template match="/">
	
		<!-- workaround for XSLT 1.0 where handling both apostrophes and quotes in one string is a bit complicated -->
		<!--xsl:variable name="apos">'</xsl:variable-->
	
		<xsl:variable name="latestQuerydate">
			<xsl:for-each select="/stpl_collection/source/query_date">
				<!--more complex version: <xsl:if test="count(../source[translate(./query_date, 'TZ:-', '') &gt; translate(current()/query_date, 'TZ:-', '')])=0">-->
				<xsl:sort select="." order="descending"/>
				<xsl:if test="position() = 1"><!--XSLT1 hack for getting string-maximum-->
					<xsl:value-of select="."/>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
	
		<!--this is additional to the interactive javascript selector - correct display of the page works without javascript-->
		<xsl:variable name="highlightSemester">
			<xsl:variable name="year">
				<xsl:value-of select="substring-before($latestQuerydate,'-')"/>
			</xsl:variable>
			<xsl:variable name="month">
				<xsl:value-of select="substring-before(substring-after($latestQuerydate,'-'),'-')"/>
			</xsl:variable>
			<xsl:choose>
				<!-- in first half of year, the summer semester will be selected, otherwise the winter semester -->
				<xsl:when test="$month &lt; 7">
					<xsl:value-of select="concat($year,'S')"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="concat($year,'W')"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		
		<xsl:variable name="yearBeforeHighlightSemester">
			<xsl:value-of select="concat(substring($highlightSemester,1,4)-1,substring($highlightSemester,5,1))"/>
		</xsl:variable>

		<xsl:variable name="firstStpl" select="stpl_collection/stpl[1]"/>
		
		<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="de">
			<head>
				<title>Studienplan <xsl:value-of select="$firstStpl/title"></xsl:value-of></title>
				<link rel="stylesheet" type="text/css" href="informatikdidaktik.css" />
				<link rel="alternate" type="application/rss+xml" title="LVA Feed" href="informatikdidaktik_rss.xml" />
				<script src="informatikdidaktik.js" type="text/javascript" charset="utf-8"></script>
				<meta charset="utf-8"/>
				<meta name="description" content="Zusammenfassung aller Lehrveranstaltungen des Studienplans Informatikdidaktik, welche an der TU WIen und Uni Wien abgehalten wurden und werden."/>
				<meta name="keywords" content="TU Wien, Uni Wien, LVAs, Lehrveranstaltungen, Studienplan, Informatikdidaktik, 950, Zusammenfassung, XSLT, XML" />
				<meta name="author" content="Fabian Ehrentraud" />
			</head>
			<body onload="document.controls.reset();onLoad();hideshowLiNoprint('quelle','quellen');">
				<div id="header">
					<h1>
						Studienplan <xsl:value-of select="$firstStpl/title"></xsl:value-of>
						<xsl:if test="count($firstStpl/version)!=0">
							(<xsl:value-of select="$firstStpl/version"/>)
						</xsl:if>
					</h1>
				</div>
				<div id="meta">
					<p class="meta-nonprint" data-name="data-meta-nonprint" onclick="hideshowLiNoprint(null,'meta');" tabindex="0">
						Diesen Abschnitt <span class="hideWhenNonprint">nicht </span>drucken
					</p>
					<p class="info">Kombination der abgehaltenen LVAs der <em>Uni Wien</em> und der <em>TU Wien</em> der vergangenen und kommenden Semester</p>
					<p class="info">Zusammengestellt von <span class="author">Fabian Ehrentraud (fabb)</span></p>
					<p class="version">
						Version vom 
						<xsl:choose>
							<xsl:when test="function-available('fn:format-dateTime')">
								<xsl:value-of select="fn:format-dateTime(xs:dateTime($latestQuerydate),'[D01].[M01].[Y0001], [H01]:[m01]:[s01]')"/>
							</xsl:when>
							<xsl:otherwise>
								<!--many browsers like FF3.6 or FF4 don't support XSLT 2.0 functions-->
								<!--<xsl:value-of select="concat(substring-before($latestQuerydate, 'T'),', ',substring-before(substring-after($latestQuerydate, 'T'), 'Z'))"/>-->
								<xsl:value-of select="concat(substring-before($latestQuerydate, 'T'),', ',substring-after($latestQuerydate, 'T'))"/>
							</xsl:otherwise>
						</xsl:choose>
					</p>
					<div id="quellen">
						<ul>
						<li class="list-header" onclick="hideshowLiNoprint('quelle','quellen');" tabindex="0">
							Quellen
						</li>
						<!--xsl:for-each select="stpl_collection/source"-->
						<!-- each source with same url only ONCE -->
						<!-- this method has complexity of n*n, Muenchian method would need more wiriting but have complexity of n log n -->
						<xsl:for-each select="stpl_collection/source[not (./url = preceding::*/url)]">
							<xsl:sort select="query_date" order="descending"/>
							<li data-name="quelle">
								<a>
									<xsl:attribute name="href">
										<xsl:value-of select="url"/>
									</xsl:attribute>
									<xsl:value-of select="url"/>
								</a>
							</li>
						</xsl:for-each>
						</ul>
					</div>
					<p class="stpl-pdf">
						<xsl:if test="count($firstStpl/url) &gt; 0 and string($firstStpl/url)">
							Studienplan PDF: 
							<a>
								<xsl:attribute name="href">
									<xsl:value-of select="$firstStpl/url"/>
								</xsl:attribute>
								<xsl:value-of select="$firstStpl/url"/>
							</a>
						</xsl:if>
					</p>
					<p class="informatikforum" data-noPrint="true">
						<xsl:if test="count($firstStpl/forum) &gt; 0 and string($firstStpl/forum)">
							Forum: 
							<a>
								<xsl:attribute name="href">
									<xsl:value-of select="$firstStpl/forum"/>
								</xsl:attribute>
								<xsl:value-of select="$firstStpl/forum"/>
							</a>
						</xsl:if>
					</p>
					<div class="controls">
						<form name="controls">
							<div>
								Nur LVAs der Uni anzeigen:
								<!--onchange does not fire in FF when changed with keyboard keys-->
								<select name="universitySelect" size="1" onchange="showUniversity(this.form.universitySelect.selectedIndex==0, this.form.universitySelect.options[this.form.universitySelect.selectedIndex].value)">
									<option selected="selected">
										Alle zeigen
									</option>
									<xsl:for-each select="$firstStpl/modulgruppe/modul/fach/lva/university">
										<xsl:sort select="." order="descending"/>
										<!-- this method has complexity of n*n, Muenchian method would need more wiriting but have complexity of n log n -->
										<xsl:if test="count(./preceding::university[current() = .])=0">
											<option>
												<!--xsl:value-of select="."/-->
												<xsl:value-of select="."/>
											</option>
										</xsl:if>
									</xsl:for-each>
								</select>
							</div>
							<div class="sidebyside">
								Semester 
								<span data-tooltip="tooltip-trigger" tabindex="0"><span class="highlightSem">hervorheben</span>
									<span data-tooltip="tooltip-pre"> - </span>
									<span data-tooltip="tooltip">Zusätzlich ist es bei LVAs die vor 2 Semestern stattgefunden haben möglich dass sie wieder im aktuellen Semester stattfinden werden, aber noch nicht angekündigt sind. Daher wird in diesem Fall das entsprechende Semester <span class="highlightPrevSem">hervorgehoben</span>.
									</span>
								</span>:
								<!--onchange does not fire in FF when changed with keyboard keys-->
								<select name="semesterSelect" size="1" onchange="highlightDiv(this.form.semesterSelect.options[this.form.semesterSelect.selectedIndex].value);hideold(this.form.hideolderCheck.checked);">
									<!-- this method has complexity of n*n, Muenchian method would need more wiriting but have complexity of n log n -->
									<xsl:for-each select="$firstStpl/modulgruppe/modul/fach/lva/semester[not (. = preceding::semester)]">
										<xsl:sort select="." order="descending"/>
										<option>
											<xsl:if test=".=$highlightSemester">
												<xsl:attribute name="selected">selected</xsl:attribute>
											</xsl:if>
											<xsl:value-of select="."/>
										</option>
									</xsl:for-each>
									<option>
										keines
									</option>
								</select>
							</div>
							<div class="sidebyside">
								<input name="hideolderCheck" type="checkbox" onclick="hideold(this.form.hideolderCheck.checked)"/> Verstecke ältere LVAs
							</div>
							<div class="sidebyside_linebreakdummy"></div>
							<div class="sidebyside">
								Anzeigen hinzugefügter LVAs seit:
								<!--onchange does not fire in FF when changed with keyboard keys-->
								<select name="dateSelect" size="1" onchange="showOldestDate(this.form.dateSelect.selectedIndex==0, this.form.dateSelect.options[this.form.dateSelect.selectedIndex].value)">
									<option selected="selected">
										Alle zeigen
									</option>
									<xsl:for-each select="$firstStpl/modulgruppe/modul/fach/lva/query_date">
										<xsl:sort select="." order="descending"/>
										<!-- this method has complexity of n*n, Muenchian method would need more wiriting but have complexity of n log n -->
										<xsl:if test="count(./preceding::query_date[name(..)='lva' and substring-before(current(), 'T') = substring-before(., 'T')])=0">
											<option>
												<!--xsl:value-of select="."/-->
												<xsl:value-of select="substring-before(., 'T')"/>
											</option>
										</xsl:if>
									</xsl:for-each>
								</select>
							</div>
							<div class="sidebyside lastvisit" data-name="lastvisitdate_div" hidden="hidden">
								Diese Seite wurde zuletzt besucht: 
								<span data-name="lastvisitdate"></span>
							</div>
							<div class="sidebyside_linebreakdummy"></div>
							<div class="sidebyside">
								<input name="hideheadersCheck" type="checkbox" onclick="hideheaders(this.form.hideheadersCheck.checked)"/> Verstecke Überschriften
							</div>
							<div class="sidebyside">
								<input name="hideemptyCheck" type="checkbox" onclick="hideempty(this.form.hideemptyCheck.checked)"/> Verstecke leere Kategorien
							</div>
							<div>
								<input name="hideuniCheck" type="checkbox" onclick="hideuni(this.form.hideuniCheck.checked)"/> Zeige nur Fächer, welche nur an <strong>einer</strong> Universität angeboten werden
							</div>
							<div>
								<button type="button" value="" onclick="if(!this.form.hideheadersCheck.checked){{hideAllDiv('modulgruppe');showAllDiv('modul');showAllDiv('wahlmodul');showAllDiv('fach');}}">
										<b>Zeige Modulgruppen</b>
								</button>
								<button type="button" value="" onclick="if(!this.form.hideheadersCheck.checked){{showAllDiv('modulgruppe');hideAllDiv('modul');hideAllDiv('wahlmodul');showAllDiv('fach');}}">
										<b>Zeige Module</b>
								</button>
								<button type="button" value="" onclick="if(!this.form.hideheadersCheck.checked){{showAllDiv('modulgruppe');showAllDiv('modul');hideAllDiv('wahlmodul');hideAllDiv('fach');}}">
										<b>Zeige Fächer</b>
								</button>
								<button type="button" value="" onclick="showAllDiv('modulgruppe');showAllDiv('modul');showAllDiv('wahlmodul');showAllDiv('fach');">
										<b>Zeige alles</b>
								</button>
							</div>
						</form>
					</div>
				</div>
				<div id="content">
					<xsl:for-each select="$firstStpl/modulgruppe">
						<div data-name="wholemodulgruppe">
							<xsl:attribute name="data-nolvas_static">
								<xsl:value-of select="count(.//lva)=0"/>
							</xsl:attribute>
							<xsl:choose>
								<xsl:when test="@wahlmodulgruppe = true()">
									<xsl:attribute name="data-wahlmodulgruppe">
										<xsl:text>true</xsl:text>
									</xsl:attribute>
								</xsl:when>
								<xsl:otherwise>
									<xsl:attribute name="data-multipleuniversities_static">
										<xsl:call-template name="multipleUniversities">
											<xsl:with-param name="fachnodes" select="./modul/fach"/>
										</xsl:call-template>
									</xsl:attribute>
								</xsl:otherwise>
							</xsl:choose>
							<xsl:variable name="modulgruppeID">
								<!-- remove ", ', spaces, comma, braces and + from variable name -->
								<!--xsl:value-of select="translate(./title,concat($apos,'&quot; ,()+'),'_______')"/-->
								<xsl:call-template name="removeSpecialChars">
									<xsl:with-param name="inputstring" select="./title"/>
								</xsl:call-template>
							</xsl:variable>
							<xsl:variable name="hasInfo" select="count(info) &gt; 0"/>
							<!-- warning: this way, no " and ' is allowed in the variable name -->
							<h2 onclick="hideshowDiv('{$modulgruppeID}')" tabindex="0">
								<xsl:if test="$hasInfo">
									<xsl:attribute name="data-tooltip">
										<xsl:text>tooltip-trigger</xsl:text>
									</xsl:attribute>
								</xsl:if>
								<xsl:value-of select="title"/>
								<xsl:if test="count(semester_suggestion) &gt; 0">
									<span class="semester_suggestions">
										<xsl:text> (</xsl:text>
										<xsl:for-each select="semester_suggestion">
											<xsl:sort select="." order="ascending"/>
											<xsl:if test="not(position() = 1)">
												<xsl:text> &amp; </xsl:text>
											</xsl:if>
											<xsl:value-of select="."/>
											<xsl:text>.</xsl:text>
										</xsl:for-each>
										<xsl:text> Semester)</xsl:text>
									</span>
								</xsl:if>
								<xsl:if test="$hasInfo">
									<span data-tooltip="tooltip-pre"> - </span>
									<span data-tooltip="tooltip">
										<xsl:value-of select="info"/>
									</span>
								</xsl:if>
							</h2>
							<div class="modulgruppe-body" data-name="modulgruppe">
								<xsl:attribute name="id">
									<xsl:value-of select="$modulgruppeID"/>
								</xsl:attribute>
								<xsl:for-each select="modul">
									<div data-name="wholemodul">
										<xsl:attribute name="data-nolvas_static">
											<xsl:value-of select="count(.//lva)=0"/>
										</xsl:attribute>
										<xsl:choose>
											<xsl:when test="@wahlmodulgruppe = true()">
											</xsl:when>
											<xsl:otherwise>
												<xsl:attribute name="data-multipleuniversities_static">
													<xsl:call-template name="multipleUniversities">
														<xsl:with-param name="fachnodes" select="./fach"/>
													</xsl:call-template>
												</xsl:attribute>
											</xsl:otherwise>
										</xsl:choose>
										<xsl:variable name="modulID">
											<!-- remove ", ', spaces, comma, braces and + from variable name -->
											<!--xsl:value-of select="translate(./title,concat($apos,'&quot; ,()+'),'_______')"/-->
											<xsl:call-template name="removeSpecialChars">
												<xsl:with-param name="inputstring" select="./title"/>
											</xsl:call-template>
										</xsl:variable>
										<!-- warning: this way, no "and ' is allowed in the variable name -->
										<h3 onclick="hideshowDiv('{$modulID}')" tabindex="0">
											<xsl:value-of select="title"/>
											<xsl:if test="count(semester_suggestion) &gt; 0">
												<span class="semester_suggestions">
													<xsl:text> (</xsl:text>
													<xsl:for-each select="semester_suggestion">
														<xsl:sort select="." order="ascending"/>
														<xsl:if test="not(position() = 1)">
															<xsl:text> &amp; </xsl:text>
														</xsl:if>
														<xsl:value-of select="."/>
														<xsl:text>.</xsl:text>
													</xsl:for-each>
													<xsl:text> Semester)</xsl:text>
												</span>
											</xsl:if>
										</h3>
										<div class="modul-body" data-name="modul">
											<xsl:attribute name="id">
												<xsl:value-of select="$modulID"/>
											</xsl:attribute>
											
											<xsl:choose>
												<xsl:when test="ancestor::modulgruppe[@wahlmodulgruppe = true()]">
												
													<!-- overwrite data-name -->
													<xsl:attribute name="data-name">
														<xsl:text>wahlmodul</xsl:text>
													</xsl:attribute>
												
													<!--div class="fach" data-name="wholefach"-->
													<div class="fach"><!--just for styling-->
														<xsl:attribute name="data-nolvas_static">
															<xsl:value-of select="count(..//lva)=0"/>
														</xsl:attribute>
														<div class="lvas" data-name="wahlfach">
														<!--div class="lvas"-->
															<xsl:choose>
																<xsl:when test="count(fach/lva)=0">
																	<p class="nolvas">Keine LVAs zu diesem Modul</p>
																</xsl:when>
																<xsl:otherwise>
																	<xsl:call-template name="lvatable">
																		<xsl:with-param name="lvas" select="fach/lva"/>
																		<xsl:with-param name="highlightSemester" select="$highlightSemester"/>
																		<xsl:with-param name="yearBeforeHighlightSemester" select="$yearBeforeHighlightSemester"/>
																		<xsl:with-param name="groupUniversities" select="true()"/>
																		<xsl:with-param name="sws1_5ects" select="true()"/>
																	</xsl:call-template>
																</xsl:otherwise>
															</xsl:choose>
														</div>
													</div>
													
												</xsl:when>
												<xsl:otherwise>
												
													<xsl:for-each select="fach">
														<div class="fach" data-name="wholefach">
															<xsl:attribute name="data-nolvas_static">
																<xsl:value-of select="count(.//lva)=0"/>
															</xsl:attribute>
															<xsl:attribute name="data-multipleuniversities_static">
																<xsl:call-template name="multipleUniversities">
																	<xsl:with-param name="fachnodes" select="."/>
																</xsl:call-template>
															</xsl:attribute>
															<xsl:variable name="fachID">
																<!-- remove ", ', spaces, comma, braces and + from variable name -->
																<!-- add modulID to the fachID as a fach can appear in several wahlmoduls -->
																<!--xsl:value-of select="translate(./title,concat($apos,'&quot; ,()+'),'_______')"/>_<xsl:value-of select="type"/-->
																<xsl:call-template name="removeSpecialChars">
																	<xsl:with-param name="inputstring" select="./title"/>
																</xsl:call-template>
																<xsl:text>_</xsl:text>
																<xsl:value-of select="type"/>
															</xsl:variable>
															<!-- warning: this way, no " and ' is allowed in the variable name -->
															<h4 onclick="hideshowDiv('{$fachID}')" tabindex="0">
																<xsl:value-of select="title"/>, <xsl:value-of select="type"/>
															</h4>
															<div class="lvas" data-name="fach">
																<xsl:attribute name="id">
																	<xsl:value-of select="$fachID"/>
																</xsl:attribute>
																<xsl:choose>
																	<xsl:when test="count(lva)=0">
																		<p class="nolvas">Keine LVAs zu diesem Fach</p>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:call-template name="lvatable">
																			<xsl:with-param name="lvas" select="lva"/>
																			<xsl:with-param name="highlightSemester" select="$highlightSemester"/>
																			<xsl:with-param name="yearBeforeHighlightSemester" select="$yearBeforeHighlightSemester"/>
																		</xsl:call-template>
																	</xsl:otherwise>
																</xsl:choose>
															</div>
														</div>
													</xsl:for-each>
													
												</xsl:otherwise>
											</xsl:choose>

										</div>
									</div>
								</xsl:for-each>
							</div>
						</div>
					</xsl:for-each>
				</div>
				<div id="footer">
					<p>
						<span>Valid HTML5. Tested with Opera, Firefox, Internet Explorer 8, Chrome and Safari.</span>
					</p>
					<p>
						<span>Project Homepage: <a href="https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping">https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping</a></span>
						<span>Fabian Ehrentraud 2011</span>
					</p>
				</div>
			</body>
		</html>
	</xsl:template>
	
	
	<!-- make a table of given lvas -->
	<xsl:template name="lvatable">
		<xsl:param name="lvas"/>
		<xsl:param name="highlightSemester"/>
		<xsl:param name="yearBeforeHighlightSemester"/>
		<xsl:param name="groupUniversities" select="false()"/>
		<xsl:param name="sws1_5ects" select="false()"/>
		
		<table data-name="lvatable">
			<tbody>
				<xsl:for-each select="$lvas">
				
					<!-- XSLT 1 trick for different sortings -->
					<xsl:sort select="university[$groupUniversities = true()]" order="ascending"/>
					<xsl:sort select="semester" order="descending"/>
					<xsl:sort select="university[$groupUniversities = false()]" order="ascending"/>
					<xsl:sort select="key" order="ascending"/>
				
					<xsl:variable name="similarLvaSet" select="../lva[./title=current()/title and ./university=current()/university and ./type=current()/type and (./university='Uni' or ./key=current()/key)]"/>
					<!--only display LVA when it has the highest semester; it is assumed that there is only one such LVA -->
					<!-- at TU there is always the same key, not on the Uni -->
					<xsl:if test="count($similarLvaSet[translate(./semester,'SW','05') &gt; translate(current()/semester,'SW','05')])=0">
						<tr data-name="lvarow">
							<xsl:if test="semester=$highlightSemester">
								<xsl:attribute name="class">
									<xsl:text>currentlva</xsl:text>
								</xsl:attribute>
							</xsl:if>
							<xsl:attribute name="data-query_date"><!--custom attribute-->
								<xsl:for-each select="$similarLvaSet/query_date">
									<xsl:sort select="." order="descending"/>
									<xsl:if test="position() = 1"><!--XSLT1 hack for getting string-maximum-->
										<xsl:value-of select="substring-before(., 'T')"/>
									</xsl:if>
								</xsl:for-each>
							</xsl:attribute>
							<td class="lvauniversity" data-name="university"><xsl:value-of select="university"/></td>
							<!--<td><xsl:value-of select="semester"/></td>-->
							<td class="lvasemester" data-name="semesters">
								<xsl:variable name="newestSemester"><xsl:value-of select="semester"/></xsl:variable>
								<xsl:for-each select="$similarLvaSet">
									<xsl:sort select="semester" order="descending"/>
									<xsl:if test="not(position() = 1)">, </xsl:if>
									<span data-name="semester">
										<!-- problematic when $newestSemester is greater than $highlightSemester -->
										<xsl:if test="$newestSemester != $highlightSemester and ./semester = $yearBeforeHighlightSemester">
											<xsl:attribute name="class">probableLva</xsl:attribute>
										</xsl:if>
										<xsl:value-of select="semester"/>
									</span>
								</xsl:for-each>
							</td>
							<td class="lvakey"><xsl:value-of select="key"/></td>
							<td class="lvatype"><xsl:value-of select="type"/></td>
							<td class="lvatitle">
								<xsl:choose>
									<xsl:when test="count(url)=0 or url=''">
										<xsl:value-of select="title"/>
									</xsl:when>
									<xsl:otherwise>
										<a>
											<xsl:attribute name="href">
												<xsl:value-of select="url"/>
											</xsl:attribute>
											<xsl:value-of select="title"/>
										</a>
									</xsl:otherwise>
								</xsl:choose>
							</td>
							<td class="lvacredits">
								<xsl:text>(</xsl:text>
								<span class="sws">
									<xsl:value-of select="sws"/>
									<xsl:text> SWS</xsl:text>
								</span>
								<xsl:text> / </xsl:text>
								<span class="ects">
									<xsl:if test="$sws1_5ects and (1.5*sws != ects)">
										<xsl:attribute name="class">
											<xsl:text>ects_incorrect</xsl:text>
										</xsl:attribute>
										<xsl:attribute name="title">
											<!-- TODO this is data that should be stored in xml file -->
											<xsl:text>Diese ECTS sind falsch eingetragen, da laut TU-Dekanat mit 1.5 umgerechnet werden sollte.</xsl:text>
										</xsl:attribute>
									</xsl:if>
									<xsl:value-of select="ects"/>
									<xsl:text> ECTS</xsl:text>
								</span>
								<xsl:text>)</xsl:text>
							</td>
							<td class="lvainfo">
								<xsl:if test="info = ''">
									<xsl:attribute name="class">
										<xsl:text>lvainfo_empty</xsl:text>
									</xsl:attribute>
								</xsl:if>
								<xsl:if test="string(info)">
									Info: <xsl:value-of select="info"/>
								</xsl:if>
							</td>
						</tr>
					</xsl:if>
				</xsl:for-each>
			</tbody>
		</table>
	</xsl:template>

</xsl:stylesheet>
