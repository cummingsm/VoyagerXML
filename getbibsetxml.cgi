#!/usr/bin/perl -w
# FILE: getbibsetxml.cgi
# DATE: 02/26/2012
# AUTH: CUMMINGS
# DESC: Responds to url in the having the following structure 
# http://gwdroid.wrlc.org/cgi-bin/getbibsetxml.cgi?bibid=7982447
#
use CGI;
$CGI::POST_MAX=1024*100; # MAX 100k POSTS
$CGI::DISABLE_UPLOADS=1; # no uploads

# trim spaces and return NULL if field is empty
sub trim
{
        my $string = shift;
        $string =~ s/^\s+//;
        $string =~ s/\s+$//;
        if ( length($string) > 0 ){
        return $string;
        } else {
        return "NULL";
        }
}


#
# This line sets the method that this script was accessed (GET or POST)
my $method = $ENV{'REQUEST_METHOD'};

# The following if else structure will use the appropriate 
# processing for grabbing the form data
if ($method eq "GET") { 
    $rawdata = $ENV{'QUERY_STRING'}; 
} else { 
   # if not "GET" then it will default "POST"
   read(STDIN, $rawdata, $ENV{'CONTENT_LENGTH'}); 
} 

# Split the data pairs into sections
my @value_pairs = split (/&/,$rawdata); 
my %formdata = (); 

# Cycle through each pair to grab the values of the fields
foreach $pair (@value_pairs) { 
    ($field, $value) = split (/=/,$pair); 
    $value =~ tr/+/ /; 
    $value =~ s/%([\dA-Fa-f][\dA-Fa-f])/pack ("C", hex ($1))/eg;
    $formdata{$field} = $value; 
    # store the field data in the results hash 
} 

print "Content-type: text/xml\n\n"; 

#
`sh bibdataquery.sh $formdata{bibid}`;

# 
my $BIBname="/tmp/bibdata".$formdata{bibid}.".txt";
if (-s $BIBname) {
	open FILE, $BIBname or dienice("Unable to open output file");
	$document='';
	while (<FILE>)
	{
        $document .= $_;
	}
	close (FILE);
   @tokens = split(/\|/, $document);
   # -----------------------------------------------------------
   # BIBLIOGRAPHIC INFORMATION
   # -----------------------------------------------------------
   print "<BIBDATA>\n";
       print "<BIBID>";
           print $formdata{bibid};
       print "</BIBID>\n";
       print "<LIBRARYID>";
       	   print trim($tokens[3]);
       print "</LIBRARYID>\n";
       print "<LIBRARYDISPLAYNAME>";
           print trim($tokens[5]);
       print "</LIBRARYDISPLAYNAME>\n";
       print "<NUCCODE>";
           print trim($tokens[7]);
       print "</NUCCODE>\n";
       print "<TITLE>";
       # Ampersand character causes the xml parser to choke!
       # Substitute the word 'and'. Preferable to CDATA
           my $cleantitle = trim($tokens[9]);
           $cleantitle =~s/\&/and/;
           print $cleantitle;
       print "</TITLE>\n";
       print "<AUTHOR>";
           my $cleanauthor = trim($tokens[11]);
           $cleanauthor =~s/\&/and/;
           print $cleanauthor;
       print "</AUTHOR>\n";
       print "<ISBN SEQ='FIRST'>";
           print trim($tokens[13]);
       print "</ISBN>\n";
       print "<ISSN>";
           print trim($tokens[15]);
       print "</ISSN>\n";
       print "<LANGUAGE>";
           print trim($tokens[17]);
       print "</LANGUAGE>\n";
       print "<BIBFORMAT>";
           print trim($tokens[19]);
       print "</BIBFORMAT>\n";
       print "<NETWORKNUMBER>";
           print trim($tokens[21]);
       print "</NETWORKNUMBER>\n";
       print "<EDITION>";
           print trim($tokens[23]);
       print "</EDITION>\n";
       print "<IMPRINT>";
           print trim($tokens[25]);
       print "</IMPRINT>\n";
       print "<SERIES>";
           print trim($tokens[27]);
       print "</SERIES>\n";
       # end of bibliographic information fields
       print "<HIERARCHY>\n";

       # ---------------------------------------------------
       # LIST OF HOLDINGS
       # ---------------------------------------------------
       # query produces pipe delimited output. eg /tmp/mfhddata7982447.txt
      `sh mfhddataquery.sh $formdata{bibid}`;
       my $Fname="/tmp/mfhddata".$formdata{bibid}.".txt";
       if (-s $Fname) {
        	#
        	# Each item is separate line in the output. 
        	$mfhdmax=`wc -l $Fname | cut -f1 -d' '`;
        	print "<HOLDINGS COUNT='".trim($mfhdmax)."'>\n";
        	#
        	for ( $h=1; $h<=trim($mfhdmax); $h++ ) 
        	{
                # Extract each holding line and print it in XML tags
  		`awk NR==$h $Fname > /tmp/hline-$h-$formdata{bibid}.txt`;
  		$Tname="/tmp/hline-".$h."-".$formdata{bibid}.".txt";
		## debug file name ##
	        #  print "<FILE>".$Tname."</FILE>";
		open FILE, $Tname or die ("Unable to open output file");
		while (<FILE>)
			{
				$holdingsdocument ='';
        			$holdingsdocument .= $_;
			}
		close (FILE);
		`rm $Tname`;
		#
		# Make an array containing each sql output field in the pipe-delimited file.
		#
		@mfhdtokens = split(/\|/, $holdingsdocument);
		#
		print "<MFHD M.BIBID='".$formdata{bibid}."' SEQ='".$h."'>\n\n";
   		print "<M.MFHDID>"; 	
		    print trim($mfhdtokens[3]); 
   		print "</M.MFHDID>\n";
        	print "<M.CALLNO>"; 	
			print trim($mfhdtokens[5]); 
   		print "</M.CALLNO>\n";
        	print "<M.MFHDLOCATION>"; 	
			print trim($mfhdtokens[7]); 
   		print "</M.MFHDLOCATION>\n";

		# --------------------------------------------------------
		# ONLINE LINK FOR THIS HOLDING
                # --------------------------------------------------------


		# query generates pipe delimited file as output. eg /tmp/elinkdata9030312.txt
		my $mfhd=trim($mfhdtokens[3]);
		`sh elinkdataquery.sh $mfhd`;
		my $eLinkFileName="/tmp/elinkdata".$mfhd.".txt";
		if (-s $eLinkFileName) {
			open FILE, $eLinkFileName or dienice("Unable to open output file");
			$ELdocument='';
			while (<FILE>)
			{
        				$ELdocument .= $_;
			}
			close (FILE);
   			@elinktokens = split(/\|/, $ELdocument);
   			print "<ELINKDATA E.BIBID='".trim($elinktokens[1])."' E.MFHDID='".trim($elinktokens[3])."'>\n";
   			#
   			# do not parse url string, return character data as is
   			#
   			print "<E.LINK><![CDATA[".trim($elinktokens[5])."]]>";
   			print "</E.LINK>\n";
   			#
   			print "<E.LINKTEXT>";
	 			print trim($elinktokens[7]);
   			print "</E.LINKTEXT>\n";
   			#
 			print "</ELINKDATA>";
 			`rm $eLinkFileName`;
		} else {
   			# ERROR return
   			#
   			print "<ELINKDATA></ELINKDATA>\n";
			} 

	
		# --------------------------------------------------------
		# ITEMS FOR THIS HOLDING
		# --------------------------------------------------------

 		# query produces pipe delimited output. eg /tmp/itemdata7982447.txt
  		my $mfhdid=trim($mfhdtokens[3]);
 		`sh mfhditemdataquery.sh $mfhdid`;

  		my $itemsFileName="/tmp/mfhditemdata".$mfhdid.".txt";
  		if (-s $itemsFileName) 
		      {
  				#
  				# Each item is separate line in the output. 
  				$max=`wc -l $itemsFileName | cut -f1 -d' '`;
				print "<ITEMS COUNT='".trim($max)."'>";
  				for ( $itemn=1; $itemn<=trim($max); $itemn++ ) 
  				{
  				# Extract each item line and print it in XML tags
  				# -------------------------------------------------
  				# ITEM DATA
  				# -------------------------------------------------
  				`awk NR==$itemn $itemsFileName > /tmp/itemline-$itemn-$formdata{bibid}.txt`;
  				$Tname="/tmp/itemline-".$itemn."-".$formdata{bibid}.".txt";
				open FILE, $Tname or die ("Unable to open output file");
				while (<FILE>)
					{
					$itemdocument ='';
        				$itemdocument .= $_;
					}
				close (FILE);
				`rm $Tname`;
				#
				# Make an array containing each sql output field in the pipe-delimited file.
				#
				@itemtokens = split(/\|/, $itemdocument);
				#
				print "<ITEM I.BIBID='".$formdata{bibid}."' I.MFHDID='".trim($itemtokens[3])."' SEQ='".$itemn."'>\n\n";
   				print "<I.ITEMID>"; 	
					print trim($itemtokens[5]); 
   				print "</I.ITEMID>\n";
   				print "<I.ITEMENUM>"; 	
					print trim($itemtokens[7]); 
   				print "</I.ITEMENUM>\n";
   				print "<I.ITEMTYPEDISPLAY>"; 	
					print trim($itemtokens[9]); 
   				print "</I.ITEMTYPEDISPLAY>\n";
   				print "<I.LIBRARYNAME>"; 	
					print trim($itemtokens[11]); 
   				print "</I.LIBRARYNAME>\n";
   				print "<I.NUCCODE>"; 	
					print trim($itemtokens[13]); 
   				print "</I.NUCCODE>\n";
   				print "<I.PERMLOCATION>"; 	
					print trim($itemtokens[15]); 
   				print "</I.PERMLOCATION>\n";
   				print "<I.PERMLOCDESC>"; 	
					print trim($itemtokens[17]); 
   				print "</I.PERMLOCDESC>\n";
   				print "<I.TEMPLOCATION>"; 	
					print trim($itemtokens[19]); 
   				print "</I.TEMPLOCATION>\n";
   				#print "<I.ENDREC>"; 	
					#print trim($itemtokens[25]); 
   				#print "</I.ENDREC>\n";
				#
				#  continue with each item, retrieve temporary location, then status
        			#
				my $item=trim($itemtokens[5]);
				#
				# -----------------------------------------------------------------
        			# ITEM TEMPORARY LOCATION DESCRIPTION
				# -----------------------------------------------------------------
				#
				# query output is a pipe delimited file. eg /tmp/locdata300000.txt
				`sh templocquery.sh $item`;
				my $LOCname="/tmp/locdata".$item.".txt";
				if (-s $LOCname) {
					open FILE, $LOCname or dienice("Unable to open output file");
					$locationdocument='';
					while (<FILE>)
						{
        						$locationdocument .= $_;
						}
					close (FILE);
					@locationtokens = split(/\|/, $locationdocument);
 					print "<TEMPLOC TL.ITEMID='".$item."'>\n";
   					print "<TL.TEMPLOCDESC>";
                				print $locationtokens[3];
   					print "</TL.TEMPLOCDESC>\n";
 					print "</TEMPLOC>";
					`rm $LOCname`;
				} else {
 					print "<TEMPLOC STATUS='NONE'>\n";
 					print "</TEMPLOC>";
				} 
				# -----------------------------------------------------------------
				# ITEM STATUS
				# -----------------------------------------------------------------
				# 
				# Query outputs pipe delimited file. eg /tmp/itemlaststatusdate3000000.txt
				`sh itemlaststatusdatequery.sh $item`;
				my $statusDateFileName="/tmp/itemlaststatusdate".$item.".txt";
				# Extract the status date field
				my $sdate=trim(`cat $statusDateFileName | cut -f2 -d'|'`);
				#
				# debug values
				# print $sd." length is ".length($sd);
				#
				if ( length($sdate) eq 9 )
				{
   	   				# The query returned a date in the format DD-MON-YY (9 characters).
   	   				# Do another Query. Find the full status description for the item status 
   	   				# that has both the matching item id PLUS the status date returned above.
   	   				#
   	   				`sh itemstatusquery.sh $item '$sdate'`;
   	   				$statusFileName="/tmp/itemstatus".$item.".txt";
   	   				#
   	   				# Now return XML instead of pipe-delimited text
   	   				#
   	   				open FILE, $statusFileName or dienice("Unable to open output file");
   	   				$statusdocument='';
   	   				while (<FILE>)
   	   				{
           	 				$statusdocument .= $_;
   	   				}
   	   				close (FILE);
   	   				@statustokens = split(/\|/, $statusdocument);
   	   				#
   	   				print "<ITEMSTATUS IS.ITEMID='".$item."'>\n";
   	   				print "<IS.ITEMSTATUSDATE>"; 	
		  			print trim($statustokens[3]); 
   	   				print "</IS.ITEMSTATUSDATE>\n";
   	   				print "<IS.ITEMSTATUSDESC>"; 	
						print trim($statustokens[5]); 
   	   				print "</IS.ITEMSTATUSDESC>\n";
   	   				print "</ITEMSTATUS>";
   	   				#cleanup /tmp
   	   				`rm $statusFileName`;
   	   				`rm $statusDateFileName`;
   	   				print "</ITEM>\n";
				} #end item status
				   else {
  	       				# ERROR return no item found
   	       				print "<ITEMSTATUS IS.ITEMID='".$item."' STATUS='NONE FOUND'>\n";
   	       				print "<IS.ITEMSTATUSDATE>"; 	
   	       				print "</IS.ITEMSTATUSDATE>\n";
   	       				print "<IS.ITEMSTATUSDESC>"; 	
	        				# Consider this condition like item is not charged.
						print "Not Charged / No Status";
   	       				print "</IS.ITEMSTATUSDESC>\n";
   	       				print "</ITEMSTATUS>";
	       				print "</ITEM>";
					}
  			} # end if items
                        print "</ITEMS>";
  			`rm $itemsFileName`;
  	} else {
        # ERROR return no itemlist
 	print "<ITEMS STATUS='NONE'>\n";
	print "</ITEMS>";
 	}
      print "</MFHD>";
  } 
  #print "</HOLDINGS>";
           } else {
              # ERROR return no holdings
              print "<HOLDINGS>\n";
              print "<MFHD M.BIBID='".$formdata{bibid}."'>\n\n";
              print "<M.MFHDID>";
                print "0";
              print "</M.MFHDID>\n";
              # end of empty recordset
	      print "</MFHD>";
              print "</HOLDINGS>";
          }
 print "</HOLDINGS>";
 #`rm $Fname`;
 # end of holding loop
 print "</HIERARCHY>";
 # end of the bibliographic information
 print "</BIBDATA>";
 `rm $BIBname`;
 } else {
       # ERROR return no bib record
       print "<BIBDATA>\n";
       print "<BIBID STATUS='NO MATCH'>";
                print $formdata{bibid};
       print "</BIBID>\n";
       print "</BIBDATA>";
       } 
# end of processing
