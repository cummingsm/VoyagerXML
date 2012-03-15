#!/usr/bin/perl -w
# FILE: getitemdataxml.cgi
# DATE: 02/26/2012
# AUTH: CUMMINGS
# DESC: Responds to url in the having the following structure 
# http://gwdroid.wrlc.org/cgi-bin/getitemdataxml.cgi?bibid=7982447
#
use CGI;
$CGI::POST_MAX=1024*100; # MAX 100k POSTS
$CGI::DISABLE_UPLOADS=1; # no uploads
#
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

# query produces pipe delimited output. eg /tmp/itemdata7982447.txt

`sh itemdataquery.sh $formdata{bibid}`;

my $Fname="/tmp/itemdata".$formdata{bibid}.".txt";
if (-s $Fname) {
  print "<ITEMSLIST>\n";
  #
  # Each item is separate line in the output. 
  $max=`wc -l $Fname | cut -c1-4`;
  for ( $n=1; $n<=$max; $n++ ) 
  {
  # Extract each line an print it in XML tags
  	`awk NR==$n $Fname > /tmp/line$n.txt`;
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
	@tokens = split(/\|/, $document);
	#
	# Since there are only a few fields, did not try creating a %hash
	# and iterating through it.
 	#
	print "<ITEM>\n\n";
	#
   	print "<BIBID>"; 		
		print trim($tokens[1]); 
   	print "</BIBID>\n";
   	#
   	print "<MFHDID>"; 	
		print trim($tokens[3]); 
   	print "</MFHDID>\n";
   	print "<ITEMID>"; 	
		print trim($tokens[5]); 
   	print "</ITEMID>\n";
   	print "<ITEMENUM>"; 	
		print trim($tokens[7]); 
   	print "</ITEMENUM>\n";
   	print "<ITEMTYPEDISPLAY>"; 	
		print trim($tokens[9]); 
   	print "</ITEMTYPEDISPLAY>\n";
   	print "<LIBRARYNAME>"; 	
		print trim($tokens[11]); 
   	print "</LIBRARYNAME>\n";
   	print "<NUCCODE>"; 	
		print trim($tokens[13]); 
   	print "</NUCCODE>\n";
   	print "<PERMLOCATION>"; 	
		print trim($tokens[15]); 
   	print "</PERMLOCATION>\n";
   	print "<PERMLOCDESC>"; 	
		print trim($tokens[17]); 
   	print "</PERMLOCDESC>\n";
   	print "<TEMPLOCATION>"; 	
		print trim($tokens[19]); 
   	print "</TEMPLOCATION>\n";
   	print "<ENDREC>"; 	
		print trim($tokens[25]); 
   	print "</ENDREC>\n";
	#
	print "</ITEM>\n";
   }
  print "</ITEMSLIST>";
  `rm $Fname`;
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
	# end of empty recordset
 	print "</ITEMSLIST>";
}

