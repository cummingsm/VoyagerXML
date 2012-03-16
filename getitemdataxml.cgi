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
   	print "<I.BIBID>"; 		
		print trim($tokens[1]); 
   	print "</I.BIBID>\n";
   	#
   	print "<I.MFHDID>"; 	
		print trim($tokens[3]); 
   	print "</I.MFHDID>\n";
   	print "<I.ITEMID>"; 	
		print trim($tokens[5]); 
   	print "</I.ITEMID>\n";
   	print "<I.ITEMENUM>"; 	
		print trim($tokens[7]); 
   	print "</I.ITEMENUM>\n";
   	print "<I.ITEMTYPEDISPLAY>"; 	
		print trim($tokens[9]); 
   	print "</I.ITEMTYPEDISPLAY>\n";
   	print "<I.LIBRARYNAME>"; 	
		print trim($tokens[11]); 
   	print "</I.LIBRARYNAME>\n";
   	print "<I.NUCCODE>"; 	
		print trim($tokens[13]); 
   	print "</I.NUCCODE>\n";
   	print "<I.PERMLOCATION>"; 	
		print trim($tokens[15]); 
   	print "</I.PERMLOCATION>\n";
   	print "<I.PERMLOCDESC>"; 	
		print trim($tokens[17]); 
   	print "</I.PERMLOCDESC>\n";
   	print "<I.TEMPLOCATION>"; 	
		print trim($tokens[19]); 
   	print "</I.TEMPLOCATION>\n";
   	print "<I.ENDREC>"; 	
		print trim($tokens[25]); 
   	print "</I.ENDREC>\n";
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
   	print "<I.BIBID>"; 		
		print $formdata{bibid};
   	print "</I.BIBID>\n";
   	#
   	print "<I.MFHDID>"; 	
		print "0";
   	print "</I.MFHDID>\n";
   	print "<I.ITEMID>"; 	
		print "0";
   	print "</I.ITEMID>\n";
   	print "<I.ITEMENUM>"; 	
		print "0";
   	print "</I.ITEMENUM>\n";
   	print "<I.ITEMTYPEDISPLAY>"; 	
		print "No record found for requested bib id";
   	print "</I.ITEMTYPEDISPLAY>\n";
   	print "<I.LIBRARYNAME>"; 	
		print "NA";
   	print "</I.LIBRARYNAME>\n";
   	print "<I.NUCCODE>"; 	
		print "NA";
   	print "</I.NUCCODE>\n";
   	print "<I.PERMLOCATION>"; 	
		print "0";
   	print "</I.PERMLOCATION>\n";
   	print "<I.PERMLOCDESC>"; 	
		print "NA";
   	print "</I.PERMLOCDESC>\n";
   	print "<I.TEMPLOCATION>"; 	
		print "0";
   	print "</I.TEMPLOCATION>\n";
   	print "<I.ENDREC>"; 	
		print "NULL";
   	print "</I.ENDREC>\n";
	print "</ITEM>";
	#
	# end of empty recordset
 	print "</ITEMSLIST>";
}

