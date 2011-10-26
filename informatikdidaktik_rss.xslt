<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!--
Fabian Ehrentraud, 2011-10-26
e0725639@mail.student.tuwien.ac.at
https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
Licensed under the Open Software License (OSL 3.0)
-->

<!--
TODO
	could use stylesheet parameters to limit number of entries
	content nicer styled
	table is not recognized by all rss readers
	make direct link to xml and set selector to only display newest LVAs
-->

	<xsl:output method="xml" media-type="application/rss+xml" indent="yes" encoding="utf-8"/>
	
	
	<!-- iso date must not contain 'Z' and be in format YYYY-MM-DD"T"HH:MM:SS[.(number)*] -->
	<xsl:template name="dateConversion_ISO8601_to_RFC822">
		<xsl:param name="isodate"/>
		
		<xsl:variable name="year">
			<xsl:value-of select="substring-before($isodate,'-')"/>
		</xsl:variable>
		<xsl:variable name="month">
			<xsl:value-of select="substring-before(substring-after($isodate,'-'),'-')"/>
		</xsl:variable>
		<xsl:variable name="stringmonth">
			<xsl:choose>
				<xsl:when test="number($month) = 1">
					<xsl:text>Jan</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 2">
					<xsl:text>Feb</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 3">
					<xsl:text>Mar</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 4">
					<xsl:text>Apr</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 5">
					<xsl:text>May</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 6">
					<xsl:text>Jun</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 7">
					<xsl:text>Jul</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 8">
					<xsl:text>Aug</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 9">
					<xsl:text>Sep</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 10">
					<xsl:text>Oct</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 11">
					<xsl:text>Nov</xsl:text>
				</xsl:when>
				<xsl:when test="number($month) = 12">
					<xsl:text>Dec</xsl:text>
				</xsl:when>
				
				<xsl:otherwise>
					<!-- should not happen... -->
					<xsl:value-of select="$month"/>
					<xsl:message terminate="no">
						<xsl:text>Month out of range: {$month}, input date was: {$isodate}</xsl:text>
					</xsl:message>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		
		<xsl:variable name="day">
			<xsl:value-of select="substring-before(substring-after(substring-after($isodate,'-'),'-'),'T')"/>
		</xsl:variable>
		<xsl:variable name="fulltime">
			<xsl:value-of select="substring-after($isodate,'T')"/>
		</xsl:variable>
		<xsl:variable name="rfctime">
			<xsl:value-of select="substring($fulltime,0,9)"/>
		</xsl:variable>
		
		<xsl:value-of select=" concat($day , ' ' , $stringmonth , ' ' , $year , ' ' , $rfctime , ' GMT')"/>
	</xsl:template>
	
	
	<xsl:template match="/">
	
		<xsl:variable name="latestQuerydate">
			<xsl:for-each select="/stpl_collection/source/query_date">
				<xsl:sort select="." order="descending"/>
				<xsl:if test="position() = 1"><!--XSLT1 hack for getting string-maximum-->
					<xsl:value-of select="."/>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		
		<xsl:variable name="latestLVA">
			<xsl:for-each select="/stpl_collection/stpl//fach/lva/query_date">
				<!--more complex version: <xsl:if test="count(../source[translate(./query_date, 'TZ:-', '') &gt; translate(current()/query_date, 'TZ:-', '')])=0">-->
				<xsl:sort select="." order="descending"/>
				<xsl:if test="position() = 1"><!--XSLT1 hack for getting string-maximum-->
					<xsl:value-of select="."/>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>

		<rss version="2.0" xml:lang="de">
			<channel>
				<title>Studienplan Informatik LVA News</title>
				<link>https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping</link>
				<description>Shows scraped courses.</description>
				<language>de</language>
				<pubDate>
					<xsl:call-template name="dateConversion_ISO8601_to_RFC822">
						<xsl:with-param name="isodate" select="$latestLVA"/>
					</xsl:call-template>
				</pubDate>
				<lastBuildDate>
					<xsl:call-template name="dateConversion_ISO8601_to_RFC822">
						<xsl:with-param name="isodate" select="$latestQuerydate"/>
					</xsl:call-template>
				</lastBuildDate>
				<!--docs>http://blogs.law.harvard.edu/tech/rss</docs-->
				<!--generator>Weblog Editor 2.0</generator-->
				<!--managingEditor>editor@example.com</managingEditor-->
				<!--webMaster>webmaster@example.com</webMaster-->
				
				
				<xsl:for-each select="/stpl_collection/stpl//fach/lva/query_date">
					<xsl:sort select="." order="descending"/>
					<!-- this method has complexity of n*n, Muenchian method would need more wiriting but have complexity of n log n -->
					<xsl:if test="count(./preceding::query_date[name(..)='lva' and substring-before(current(), 'T') = substring-before(., 'T')])=0">
							
							<item>
								<title>
									<xsl:value-of select="count(/stpl_collection/stpl//fach/lva[starts-with(./query_date, substring-before(current(), 'T'))])"/>
									neue LVAs
								</title>
								<!--TODO make direct link to xml and set selector to only display newest LVAs-->
								<link>https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping</link>

								<description>
									<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
									
										Neue LVAs:
										
										<table>
											<tbody>

												<xsl:for-each select="/stpl_collection/stpl//fach/lva[starts-with(./query_date, substring-before(current(), 'T'))]">
													<xsl:sort select="semester" order="descending"/>
													<xsl:sort select="university" order="descending"/>
													<xsl:sort select="key" order="descending"/>
													
													<tr>
														<td>
															<xsl:value-of select="university"/>
														</td>
														<td>
															<xsl:value-of select="semester"/>
														</td>
														<td>
															<xsl:value-of select="key"/>
														</td>
														<td>
															<xsl:value-of select="type"/>
														</td>
														<td>
															<xsl:value-of select="sws"/>SWS
														</td>
														<td>
															<xsl:value-of select="ects"/>ECTS
														</td>
														<td>
														<td>
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
															<xsl:value-of select="info"/>
														</td>
													</tr>
												</xsl:for-each>
										
											</tbody>
										</table>
									
									<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
									
								</description>
								
								<pubDate>
									<xsl:call-template name="dateConversion_ISO8601_to_RFC822">
										<xsl:with-param name="isodate" select="."/>
									</xsl:call-template>
								</pubDate>
								<guid isPermaLink="false">
									<xsl:value-of select="substring-before(., 'T')"/>
								</guid>
							</item>
							
					</xsl:if>
				</xsl:for-each>
			</channel>
		</rss>
	</xsl:template>
</xsl:stylesheet>
