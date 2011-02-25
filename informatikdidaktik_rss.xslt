<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!--
Fabian Ehrentraud, 2011-02-25
e0725639@mail.student.tuwien.ac.at
https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping
Licensed under the Open Software License (OSL 3.0)
-->

<!--
TODO
	could use stylesheet parameters to limit number of entries
	content nicer styled
	make direct link to xml and set selector to only display newest LVAs
FIXME
	pubDate has wrong format, should follow RFC 822
		http://symphony-cms.com/download/xslt-utilities/view/50791/
-->

	<xsl:output method="xml" media-type="application/rss+xml" indent="yes" encoding="utf-8"/>
	
	<xsl:template match="/">
	
		<xsl:variable name="latestQuerydate">
			<xsl:for-each select="/stpl_collection/source">
				<!--more complex version: <xsl:if test="count(../source[translate(./query_date, 'TZ:-', '') &gt; translate(current()/query_date, 'TZ:-', '')])=0">-->
				<xsl:sort select="query_date" order="descending"/>
				<xsl:if test="position() = 1"><!--XSLT1 hack for getting string-maximum-->
					<xsl:value-of select="query_date"/>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		
		<xsl:variable name="latestLVA">
			<xsl:for-each select="/stpl_collection/stpl/modulgruppe/modul/fach/lva">
				<!--more complex version: <xsl:if test="count(../source[translate(./query_date, 'TZ:-', '') &gt; translate(current()/query_date, 'TZ:-', '')])=0">-->
				<xsl:sort select="query_date" order="descending"/>
				<xsl:if test="position() = 1"><!--XSLT1 hack for getting string-maximum-->
					<xsl:value-of select="query_date"/>
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
					<xsl:value-of select="$latestLVA"/>
					<!--TODO Tue, 10 Jun 2003 04:00:00 GMT-->
				</pubDate>
				<lastBuildDate>
					<xsl:value-of select="$latestQuerydate"/>
					<!--TODO Tue, 10 Jun 2003 09:41:01 GMT-->
				</lastBuildDate>
				<!--docs>http://blogs.law.harvard.edu/tech/rss</docs-->
				<!--generator>Weblog Editor 2.0</generator-->
				<!--managingEditor>editor@example.com</managingEditor-->
				<!--webMaster>webmaster@example.com</webMaster-->
				
				
				<xsl:for-each select="/stpl_collection/stpl/modulgruppe/modul/fach/lva/query_date">
					<xsl:sort select="." order="descending"/>
					<!-- this method has complexity of n*n, Muenchian method would need more wiriting but have complexity of n log n -->
					<xsl:if test="count(./preceding::query_date[name(..)='lva' and substring-before(current(), 'T') = substring-before(., 'T')])=0">
							
							<item>
								<title>
									<xsl:value-of select="count(/stpl_collection/stpl/modulgruppe/modul/fach/lva[starts-with(./query_date, substring-before(current(), 'T'))])"/>
									neue LVAs
								</title>
								<!--TODO make direct link to xml and set selector to only display newest LVAs-->
								<link>https://github.com/fabb/Informatikdidaktik-Studienplan-Scraping</link>

								<description>
									<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
									
										Neue LVAs:
										
										<table>
											<tbody>

												<xsl:for-each select="/stpl_collection/stpl/modulgruppe/modul/fach/lva[starts-with(./query_date, substring-before(current(), 'T'))]">
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
									<xsl:value-of select="substring-before(., 'T')"/>
									<!--TODO Tue, 03 Jun 2003 09:39:21 GMT-->
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
