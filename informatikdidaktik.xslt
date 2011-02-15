<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions">

<!--
Fabian Ehrentraud, 2011-02-15
e0725639@mail.student.tuwien.ac.at
-->
	
	<xsl:output method="html" media-type="text/html" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="DTD/xhtml1-strict.dtd" cdata-section-elements="script style" indent="yes" encoding="UTF-8"/>
	
	<xsl:template match="/">
	
		<xsl:variable name="latestQuerydate">
			<xsl:for-each select="/stpl_collection/source">
				<!--more complex version: <xsl:if test="count(../source[translate(./query_date, 'TZ:-', '') &gt; translate(current()/query_date, 'TZ:-', '')])=0">-->
				<xsl:sort select="query_date" order="descending"/>
				<xsl:if test="position() = 1">
					<xsl:value-of select="query_date"/>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
	
		<!--TODO interactive javascript selector instead? or query current date?-->
		<xsl:variable name="highlightSemester">
			<xsl:variable name="year">
				<xsl:value-of select="substring-before($latestQuerydate,'-')"/>
			</xsl:variable>
			<xsl:variable name="month">
				<xsl:value-of select="substring-before(substring-after($latestQuerydate,'-'),'-')"/>
			</xsl:variable>
			<xsl:choose>
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
				<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
				<meta name="description" content="Zusammenfassung aller Lehrveranstaltungen des Studienplans Informatikdidaktik, welche an der TU WIen und Uni Wien abgehalten wurden und werden." />
			</head>
			<body>
				<div id="header">
					<h1>
						Studienplan <xsl:value-of select="stpl_collection/stpl/title"></xsl:value-of>
						<xsl:if test="count(stpl_collection/stpl/version)!=0">
							(<xsl:value-of select="stpl_collection/stpl/version"/>)
						</xsl:if>
					</h1>
				</div>
				<div id="meta">
					<p class="info">Kombination der abgehaltenen LVAs der <em>Uni Wien</em> und der <em>TU Wien</em> der vergangenen und kommenden Semester</p>
					<p class="info">Zusammengestellt von <span class="author">Fabian Ehrentraud (fabb)</span></p>
					<p class="version">
						Version vom 
						<xsl:choose>
							<xsl:when test="function-available('fn:format-dateTime')">
								<xsl:value-of select="fn:format-dateTime(xs:dateTime($latestQuerydate),'[D01].[M01].[Y0001], [H01]:[m01]:[s01]')"/>
							</xsl:when>
							<xsl:otherwise>
								<!--FF3.6 does not support XSLT 2.0 functions-->
								<!--<xsl:value-of select="concat(substring-before($latestQuerydate, 'T'),', ',substring-before(substring-after($latestQuerydate, 'T'), 'Z'))"/>-->
								<xsl:value-of select="concat(substring-before($latestQuerydate, 'T'),', ',substring-after($latestQuerydate, 'T'))"/>
							</xsl:otherwise>
						</xsl:choose>
					</p>
					<p>
						<ul>
						<li class="list-header">
							Quellen:
						</li>
							<!--xsl:for-each select="stpl_collection/source"-->
							<!-- each source with same url only ONCE -->
							<xsl:for-each select="stpl_collection/source[not (./url = preceding::*/url)]">
								<xsl:sort select="query_date" order="descending"/>
								<li>
									<a>
										<xsl:attribute name="href">
											<xsl:value-of select="url"/>
										</xsl:attribute>
										<xsl:attribute name="target">new</xsl:attribute>
										<xsl:value-of select="url"/>
									</a>
								</li>
							</xsl:for-each>
						</ul>
					</p>
					<p class="stpl-pdf">
						<xsl:if test="count(stpl_collection/stpl/url) &gt; 0 and string(stpl_collection/stpl/url)">
							Studienplan PDF: 
							<a>
								<xsl:attribute name="href">
									<xsl:value-of select="stpl_collection/stpl/url"/>
								</xsl:attribute>
								<xsl:attribute name="target">new</xsl:attribute>
								<xsl:value-of select="stpl_collection/stpl/url"/>
							</a>
						</xsl:if>
					</p>
				</div>
				<div id="content">
					<xsl:for-each select="stpl_collection/stpl/modulgruppe">
						<h2><xsl:value-of select="title"/></h2>
						<xsl:for-each select="modul">
							<h3><xsl:value-of select="title"/></h3>
							<xsl:for-each select="fach">
								<div class="fach">
									<h4><xsl:value-of select="title"/>, <xsl:value-of select="type"/></h4>
									<div class="lvas">
										<xsl:choose>
											<xsl:when test="count(lva)=0">
												<p class="nolvas">Keine LVAs zu diesem Fach</p>
											</xsl:when>
											<xsl:otherwise>
												<table>
													<xsl:for-each select="lva">
														<xsl:sort select="semester" order="descending"/>
														<!--only display LVA when it has the highest semester; it is assumed that there is only one such LVA -->
														<!-- at TU there is always the same key, not on the Uni -->
														<xsl:if test="count(../lva[./title=current()/title and ./university=current()/university and ./type=current()/type and (./university='Uni' or ./key=current()/key) and translate(./semester,'SW','05') &gt; translate(current()/semester,'SW','05')])=0">
															<tr>
																<xsl:if test="semester=$highlightSemester">
																	<xsl:attribute name="class">
																		currentlva
																	</xsl:attribute>
																</xsl:if>
																<td class="lvauniversity"><xsl:value-of select="university"/></td>
																<!--<td><xsl:value-of select="semester"/></td>-->
																<td class="lvasemester">
																	<xsl:variable name="newestSemester"><xsl:value-of select="semester"/></xsl:variable>
																	<xsl:for-each select="../lva[./title=current()/title and ./university=current()/university and ./type=current()/type and (./university='Uni' or ./key=current()/key)]">
																		<xsl:sort select="semester" order="descending"/>
																		<xsl:if test="not(position() = 1)">, </xsl:if>
																		<span>
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
																				<xsl:attribute name="target">new</xsl:attribute>
																				<xsl:value-of select="title"/>
																			</a>
																		</xsl:otherwise>
																	</xsl:choose>
																</td>
																<td class="lvacredits">
																	(<xsl:value-of select="sws"/> SWS / <xsl:value-of select="ects"/> ECTS)
																</td>
																<td class="lvainfo">
																	<xsl:if test="string(info)">
																		Infos: <xsl:value-of select="info"/>
																	</xsl:if>
																</td>
															</tr>
														</xsl:if>
													</xsl:for-each>
												</table>
											</xsl:otherwise>
										</xsl:choose>
									</div>
								</div>
							</xsl:for-each>
						</xsl:for-each>
					</xsl:for-each>
				</div>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>
