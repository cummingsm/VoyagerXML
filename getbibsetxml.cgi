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
   print "<BIBDATA>\n";
   print "<BIBID>";
                print trim($tokens[1]);
   print "</BIBID>\n";
   #
   print "<LIBRARYID>";
                print trim($tokens[3]);
   print "</LIBRARYID>\n";
   #
   print "<LIBRARYDISPLAYNAME>";
                print trim($tokens[5]);
   print "</LIBRARYDISPLAYNAME>\n";
   #
   print "<NUCCODE>";
                print trim($tokens[7]);
   print "</NUCCODE>\n";
   #
   print "<TITLE>";
        # Ampersand character causes the xml parser to choke!
        my $cleanstring = trim($tokens[9]);
        $cleanstring =~s/\&/and/;
        print $cleanstring;
   print "</TITLE>\n";
   #
   print "<AUTHOR>";
       # Ampersand character causes the xml parser to choke!
         my $cleanstring = trim($tokens[11]);
         $cleanstring =~s/\&/and/;
         print $cleanstring;
   print "</AUTHOR>\n";
   #
   print "<ISBN>";
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
 # 
 # ----------------------------------------------------------------
 # get a list of items
 # ----------------------------------------------------------------
 #
 # query produces pipe delimited output. eg /tmp/itemdata7982447.txt
 `sh itemdataquery.sh $formdata{bibid}`;

  my $ITEMSname="/tmp/itemdata".$formdata{bibid}.".txt";
  if (-s $ITEMSname) {
  print "<ITEMSLIST>\n";
  #
  # Each item is separate line in the output. 
  $max=`wc -l $ITEMSname | cut -c1-4`;
  for ( $n=1; $n<=$max; $n++ ) 
  {
  # Extract each line an print it in XML tags
  	`awk NR==$n $ITEMSname > /tmp/line$n.txt`;
  	$Tname="/tmp/line".$n.".txt";
	open FILE, $Tname or die ("Unable to open output file");
	while (<FILE>)
	{
	$document ='';
        $document .= $_;
	}
	close (FILE);
	`rm $Tname`;
	#
	# Make an array containing each sql output field in the pipe-delimited file.
	#
	@itemtokens = split(/\|/, $document);
	#
	# Since there are only a few fields, did not try creating a %hash
	# and iterating through it.
 	#
	print "<ITEM>\n\n";
	#
   	print "<BIBID>"; 		
		print trim($itemtokens[1]); 
   	print "</BIBID>\n";
   	#
   	print "<MFHDID>"; 	
		print trim($itemtokens[3]); 
   	print "</MFHDID>\n";
   	print "<ITEMID>"; 	
		print trim($itemtokens[5]); 
   	print "</ITEMID>\n";
   	print "<ITEMENUM>"; 	
		print trim($itemtokens[7]); 
   	print "</ITEMENUM>\n";
   	print "<ITEMTYPEDISPLAY>"; 	
		print trim($itemtokens[9]); 
   	print "</ITEMTYPEDISPLAY>\n";
   	print "<LIBRARYNAME>"; 	
		print trim($itemtokens[11]); 
   	print "</LIBRARYNAME>\n";
   	print "<NUCCODE>"; 	
		print trim($itemtokens[13]); 
   	print "</NUCCODE>\n";
   	print "<PERMLOCATION>"; 	
		print trim($itemtokens[15]); 
   	print "</PERMLOCATION>\n";
   	print "<PERMLOCDESC>"; 	
		print trim($itemtokens[17]); 
   	print "</PERMLOCDESC>\n";
   	print "<TEMPLOCATION>"; 	
		print trim($itemtokens[19]); 
   	print "</TEMPLOCATION>\n";
   	print "<ENDREC>"; 	
		print trim($itemtokens[25]); 
   	print "</ENDREC>\n";
	#
	#  continue with each item, retrieve temporary location, then status
        #
	my $item=trim($itemtokens[5]);
	#
	# -----------------------------------------------------------------
        # get temporary location description for the item
	# -----------------------------------------------------------------
	# query output is a pipe delimited file. eg /tmp/locdata300000.txt
	`sh templocquery.sh $item`;
	my $LOCname="/tmp/locdata".$item.".txt";
	if (-s $LOCname) {
		open FILE, $LOCname or dienice("Unable to open output file");
		$document='';
		while (<FILE>)
		{
        	$document .= $_;
		}
	close (FILE);
	@locationtokens = split(/\|/, $document);
	# Note: No trim required.
 	print "<TEMPLOC>\n";
   	print "<ITEMID>";
                print $locationtokens[1];
   	print "</ITEMID>\n";
   	#
   	print "<TEMPLOCDESC>";
                print $locationtokens[3];
   	print "</TEMPLOCDESC>\n";
 	print "</TEMPLOC>";
	`rm $LOCname`;
	} else {
 		print "<TEMPLOC>\n";
   		print "<ITEMID>";
                print $item;
   		print "</ITEMID>\n";
   		print "<TEMPLOCDESC>";
                print "NA";
   		print "</TEMPLOCDESC>\n";
 		print "</TEMPLOC>";
		} 
	# -----------------------------------------------------------------
	# get current status of the item
	# -----------------------------------------------------------------
	# 
	# Query outputs pipe delimited file. eg /tmp/itemlaststatusdate3000000.txt
	`sh itemlaststatusdatequery.sh $item`;
	my $SDname="/tmp/itemlaststatusdate".$item.".txt";
	# Extract the status date field
	my $sdate=trim(`cat $SDname | cut -f2 -d'|'`);
	#
	# debug values
	# print $sd." length is ".length($sd);
	#
	if ( length($sdate) eq 9 )
	{
   	# The query returned a date in the format DD-MON-YY (9 characters).
   	# Do another Query. Find the full status description for the item status 
   	# that has the matching item id PLUS the status date returned above.
   	#
   	`sh itemstatusquery.sh $item '$sdate'`;
   	$Fname="/tmp/itemstatus".$item.".txt";
   	#
   	# Now return XML instead of pipe-delimited text
   	#
   	open FILE, $Fname or dienice("Unable to open output file");

   	$document='';
   	while (<FILE>)
   	{
        $document .= $_;
   	}
   	close (FILE);
   	@statustokens = split(/\|/, $document);
   	#
   	print "<ITEMSTATUS>\n";
   	print "<ITEMID>"; 		
		print trim($statustokens[1]); 
   	print "</ITEMID>\n";
   	#
   	print "<ITEMSTATUSDATE>"; 	
		print trim($statustokens[3]); 
   	print "</ITEMSTATUSDATE>\n";
   	#
   	print "<ITEMSTATUSDESC>"; 	
		print trim($statustokens[5]); 
   	print "</ITEMSTATUSDESC>\n";
   	print "</ITEMSTATUS>";
   	#cleanup /tmp
   	`rm $Fname`;
   	`rm $SDname`;
	} else {
  	# ERROR return
   	print "<ITEMSTATUS>\n";
   	print "<ITEMID>"; 		
		print $item; 
   	print "</ITEMID>\n";
   	#
   	print "<ITEMSTATUSDATE>"; 	
		print "01-JAN-00"; 
   	print "</ITEMSTATUSDATE>\n";
   	#
   	print "<ITEMSTATUSDESC>"; 	
		print "Invalid Item ID"; 
   	print "</ITEMSTATUSDESC>\n";
   	print "</ITEMSTATUS>";
	}
	# end of get current status
	print "</ITEM>\n";
   }
  print "</ITEMSLIST>";
  `rm $ITEMSname`;
} else {
        # ERROR. The query output file was empty so print null values
	# in the same structure as a valid record.
 	print "<ITEMSLIST>\n";
 	#
	print "<ITEM>\n";
   	print "<BIBID>"; 		
		print $formdata{bibid};
   	print "</BIBID>\n";
   	#
   	print "<MFHDID>"; 	
		print "0";
   	print "</MFHDID>\n";
   	print "<ITEMID>"; 	
		print "0";
   	print "</ITEMID>\n";
   	print "<ITEMENUM>"; 	
		print "0";
   	print "</ITEMENUM>\n";
   	print "<ITEMTYPEDISPLAY>"; 	
		print "No record found for requested bib id";
   	print "</ITEMTYPEDISPLAY>\n";
   	print "<LIBRARYNAME>"; 	
		print "NA";
   	print "</LIBRARYNAME>\n";
   	print "<NUCCODE>"; 	
		print "NA";
   	print "</NUCCODE>\n";
   	print "<PERMLOCATION>"; 	
		print "0";
   	print "</PERMLOCATION>\n";
   	print "<PERMLOCDESC>"; 	
		print "NA";
   	print "</PERMLOCDESC>\n";
   	print "<TEMPLOCATION>"; 	
		print "0";
   	print "</TEMPLOCATION>\n";
   	print "<ENDREC>"; 	
		print "NULL";
   	print "</ENDREC>\n";
	print "</ITEM>";
	#
	# end of empty recordset for items
 	print "</ITEMSLIST>";
 }
 #
 print "</BIBDATA>";
 `rm $BIBname`;
} else {
   # ERROR return no bib record
   #
   print "<BIBDATA>\n";
   print "<BIBID>";
                print $formdata{bibid};
   print "</BIBID>\n";
   #
   print "<LIBRARYID>";
                print "0";
   print "</LIBRARYID>\n";
   #
   print "<LIBRARYDISPLAYNAME>";
                print "NA";
   print "</LIBRARYDISPLAYNAME>\n";
   #
   print "<NUCCODE>";
                print "NA";
   print "</NUCCODE>\n";
   #
   print "<TITLE>";
                print "No title found for requested bib id";
   print "</TITLE>\n";
   #
   print "<AUTHOR>";
                print "NA";
   print "</AUTHOR>\n";
   #
   print "<ISBN>";
                print "0";
   print "</ISBN>\n";
   print "<ISSN>";
                print "0"; 
   print "</ISSN>\n";
   print "<LANGUAGE>";
                print "NA";
   print "</LANGUAGE>\n";

   print "<BIBFORMAT>";
                print "NA";
   print "</BIBFORMAT>\n";
   print "<NETWORKNUMBER>";
                print "NA";
   print "</NETWORKNUMBER>\n";

 print "</BIBDATA>";
} 

