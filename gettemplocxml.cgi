#!/usr/bin/perl -w
# FILE: gettemplocxml.cgi
# DATE: 03/01/2012
# AUTH: CUMMINGS
# DESC: Responds to url in the having the following structure 
# http://gwdroid.wrlc.org/cgi-bin/gettemplocxml.cgi?itemid=5434377
# Returns the full name of the temporary item location for the item
# in XML format
use CGI;
$CGI::POST_MAX=1024*100; # MAX 100k POSTS
$CGI::DISABLE_UPLOADS=1; # no uploads

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
print "Content-type: text/xml\n\n";

# query output is a pipe delimited file. eg /tmp/locdata300000.txt
`sh templocquery.sh $formdata{itemid}`;
my $Fname="/tmp/locdata".$formdata{itemid}.".txt";
if (-s $Fname) {
	open FILE, $Fname or dienice("Unable to open output file");
	$document='';
	while (<FILE>)
	{
        $document .= $_;
	}
	close (FILE);
	@tokens = split(/\|/, $document);
	# Note: No trim required.
 	print "<TEMPLOC>\n";
   	print "<ITEMID>";
                print $tokens[1];
   	print "</ITEMID>\n";
   	#
   	print "<TEMPLOCDESC>";
                print $tokens[3];
   	print "</TEMPLOCDESC>\n";
 	print "</TEMPLOC>";
	`rm $Fname`;
} else {
 	print "<TEMPLOC>\n";
   	print "<ITEMID>";
                print $formdata{itemid};
   	print "</ITEMID>\n";
   	#
   	print "<TEMPLOCDESC>";
                print "No record found for item requested";
   	print "</TEMPLOCDESC>\n";
 	print "</TEMPLOC>";
} 
                                                          
