<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="xs fn">

<!--
Fabian Ehrentraud, 2011-03-03
e0725639@mail.student.tuwien.ac.at
https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
Licensed under the Open Software License (OSL 3.0)
-->

<!--
TODO
	save collapse state to localStorage
	checkboxes for done lvas, store to localStorage / loadable file
-->

	<!-- use method html to avoid self closing tags; xslt 2.0 would support method xhtml -->
	<!-- media-type text/xml or application/xml or application/xhtml+xml does not allow to use the HTML DOM and breaks the used Javascript -->
	<!--xsl:output method="html" media-type="text/html" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" cdata-section-elements="script style" indent="yes" encoding="utf-8"/-->
	<!-- html5 has short doctype, not even doctype-system="about:legacy-compat" should be necessary, but is here as some XSLT processors hide the doctype as a whole if it is missing -->
	<!-- XHTML version of html5 should not need a doctype at all, but that leads to problems -->
	<xsl:output method="html" media-type="text/html" doctype-system="about:legacy-compat" cdata-section-elements="script style" indent="yes" encoding="utf-8"/>
	
	<xsl:template match="/">
	
		<!-- workaround for XSLT 1.0 where handling both apostrophes and quotes in one string is a bit complicated -->
		<xsl:variable name="apos">'</xsl:variable>
	
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
		
		<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="de">
			<head>
				<title>Studienplan <xsl:value-of select="stpl_collection/stpl/title"></xsl:value-of></title>
				<link rel="stylesheet" type="text/css" href="informatikdidaktik.css" />
				<link rel="alternate" type="application/rss+xml" title="LVA Feed" href="informatikdidaktik_rss.xml" />
				<script src="informatikdidaktik.js" type="text/javascript" charset="utf-8"></script>
				<meta charset="utf-8"/>
				<meta name="description" content="Zusammenfassung aller Lehrveranstaltungen des Studienplans Informatikdidaktik, welche an der TU WIen und Uni Wien abgehalten wurden und werden."/>
				<meta name="keywords" content="TU Wien, Uni Wien, LVAs, Lehrveranstaltungen, Studienplan, Informatikdidaktik, 950, Zusammenfassung, XSLT, XML" />
				<meta name="author" content="Fabian Ehrentraud" />
			</head>
			<body onload="document.controls.reset();onLoad();">
				<div id="header">
					<h1>
						Studienplan <xsl:value-of select="stpl_collection/stpl/title"></xsl:value-of>
						<xsl:if test="count(stpl_collection/stpl/version)!=0">
							(<xsl:value-of select="stpl_collection/stpl/version"/>)
						</xsl:if>
					</h1>
				</div>
				<div id="meta">
					<p class="meta-nonprint" data-name="data-meta-nonprint" onclick="hideshowLiNoprint(null,'meta');">
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
						<li class="list-header" onclick="hideshowLiNoprint('quelle','quellen');">
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
						<xsl:if test="count(stpl_collection/stpl/url) &gt; 0 and string(stpl_collection/stpl/url)">
							Studienplan PDF: 
							<a>
								<xsl:attribute name="href">
									<xsl:value-of select="stpl_collection/stpl/url"/>
								</xsl:attribute>
								<xsl:value-of select="stpl_collection/stpl/url"/>
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
									<xsl:for-each select="stpl_collection/stpl/modulgruppe/modul/fach/lva/university">
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
								Semester hervorheben:
								<!--onchange does not fire in FF when changed with keyboard keys-->
								<select name="semesterSelect" size="1" onchange="highlightDiv(this.form.semesterSelect.options[this.form.semesterSelect.selectedIndex].value);hideold(this.form.hideolderCheck.checked);">
									<!-- this method has complexity of n*n, Muenchian method would need more wiriting but have complexity of n log n -->
									<xsl:for-each select="stpl_collection/stpl/modulgruppe/modul/fach/lva/semester[not (. = preceding::semester)]">
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
									<xsl:for-each select="stpl_collection/stpl/modulgruppe/modul/fach/lva/query_date">
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
								<button type="button" value="" onclick="if(!this.form.hideheadersCheck.checked){{hideAllDiv('modulgruppe');showAllDiv('modul');showAllDiv('fach');}}">
										<b>Zeige Modulgruppen</b>
								</button>
								<button type="button" value="" onclick="if(!this.form.hideheadersCheck.checked){{showAllDiv('modulgruppe');hideAllDiv('modul');showAllDiv('fach');}}">
										<b>Zeige Module</b>
								</button>
								<button type="button" value="" onclick="if(!this.form.hideheadersCheck.checked){{showAllDiv('modulgruppe');showAllDiv('modul');hideAllDiv('fach');}}">
										<b>Zeige Fächer</b>
								</button>
								<button type="button" value="" onclick="showAllDiv('modulgruppe');showAllDiv('modul');showAllDiv('fach');">
										<b>Zeige alles</b>
								</button>
							</div>
						</form>
					</div>
				</div>
				<div id="content">
					<xsl:for-each select="stpl_collection/stpl/modulgruppe">
						<div data-name="wholemodulgruppe">
							<xsl:attribute name="data-nolvas_static">
								<xsl:value-of select="count(.//lva)=0"/>
							</xsl:attribute>
							<xsl:variable name="modulgruppeID">
								<!-- remove ", ', spaces, comma, braces and + from variable name -->
								<xsl:value-of select="translate(./title,concat($apos,'&quot; ,()+'),'_______')"/>
							</xsl:variable>
							<!-- warning: this way, no " and ' is allowed in the variable name -->
							<h2 onclick="hideshowDiv('{$modulgruppeID}')">
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
										<xsl:variable name="modulID">
											<!-- remove ", ', spaces, comma, braces and + from variable name -->
											<xsl:value-of select="translate(./title,concat($apos,'&quot; ,()+'),'_______')"/>
										</xsl:variable>
										<!-- warning: this way, no "and ' is allowed in the variable name -->
										<h3 onclick="hideshowDiv('{$modulID}')">
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
											<xsl:for-each select="fach">
												<div class="fach" data-name="wholefach">
													<xsl:attribute name="data-nolvas_static">
														<xsl:value-of select="count(.//lva)=0"/>
													</xsl:attribute>
													<xsl:variable name="fachID">
														<!-- remove ", ', spaces, comma, braces and + from variable name -->
														<!-- add modulID to the fachID as a fach can appear in several wahlmoduls -->
														<xsl:value-of select="translate(./title,concat($apos,'&quot; ,()+'),'_______')"/>_<xsl:value-of select="type"/>
													</xsl:variable>
													<!-- warning: this way, no " and ' is allowed in the variable name -->
													<h4 onclick="hideshowDiv('{$fachID}')">
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
																<table data-name="lvatable">
																	<tbody>
																		<xsl:for-each select="lva">
																			<xsl:sort select="semester" order="descending"/>
																			<xsl:sort select="university" order="ascending"/>
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
																							<xsl:when test="url='' or count(url)=0">
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
																						(<xsl:value-of select="sws"/> SWS / <xsl:value-of select="ects"/> ECTS)
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
															</xsl:otherwise>
														</xsl:choose>
													</div>
												</div>
											</xsl:for-each>
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
</xsl:stylesheet>
