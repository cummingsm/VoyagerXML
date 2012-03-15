#!/usr/bin/perl -w
# FILE: getitemstatusxml.cgi
# DATE: 03/07/2012
# AUTH: CUMMINGS
# DESC: Responds to url in the having the following structure 
# http://gwdroid.wrlc.org/cgi-bin/getitemstatusxml.cgi?itemid=5434377
# Returns the full name of the most recent status of the item
# in XML format
use CGI;
$CGI::POST_MAX=1024*100; # MAX 100k POSTS
$CGI::DISABLE_UPLOADS=1; # no uploads

sub trim
{
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
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

# next line sets the MIME type for the output 
#print "Content-type: application/json\n\n"; 
#print "Content-type: text/html\n\n";
print "Content-type: text/xml\n\n";

# Query outputs pipe delimited file. eg /tmp/itemlaststatusdate3000000.txt
`sh itemlaststatusdatequery.sh $formdata{itemid}`;
my $SDname="/tmp/itemlaststatusdate".$formdata{itemid}.".txt";

# Extract the status date field
my $sd=trim(`cat $SDname | cut -f2 -d'|'`);
#
# debug values
# print $sd." length is ".length($sd);
#
if ( length($sd) eq 9 )
{
   # The query returned a date in the format DD-MON-YY (9 characters).
   # Do another Query. Find the full status description for the item status 
   # that has the matching item id PLUS the status date returned above.
   #
   `sh itemstatusquery.sh $formdata{itemid} '$sd'`;
   $Fname="/tmp/itemstatus".$formdata{itemid}.".txt";
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
   @tokens = split(/\|/, $document);
   #
   print "<ITEMSTATUS>\n";
   print "<ITEMID>"; 		
		print trim($tokens[1]); 
   print "</ITEMID>\n";
   #
   print "<ITEMSTATUSDATE>"; 	
		print trim($tokens[3]); 
   print "</ITEMSTATUSDATE>\n";
   #
   print "<ITEMSTATUSDESC>"; 	
		print trim($tokens[5]); 
   print "</ITEMSTATUSDESC>\n";
   print "</ITEMSTATUS>";
   #cleanup /tmp
   `rm $Fname`;
   `rm $SDname`;
} else {
  # ERROR return
   print "<ITEMSTATUS>\n";
   print "<ITEMID>"; 		
		print $formdata{itemid}; 
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










 
