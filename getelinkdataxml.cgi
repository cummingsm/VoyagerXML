#!/usr/bin/perl -w
# FILE: getelinkdataxml.cgi
# DATE: 03/21/2012
# AUTH: CUMMINGS
# DESC: Responds to url in the having the following structure 
# http://gwdroid.wrlc.org/cgi-bin/getelinkdataxml.cgi?mfhdid=9030312
# Returns selected fields of a bib record in XML format
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

# query generates pipe delimited file as output. eg /tmp/elinkdata9030312.txt
`sh elinkdataquery.sh $formdata{mfhdid}`;
my $Fname="/tmp/elinkdata".$formdata{mfhdid}.".txt";
if (-s $Fname) {
	open FILE, $Fname or dienice("Unable to open output file");
	$document='';
	while (<FILE>)
	{
        $document .= $_;
	}
	close (FILE);
   @tokens = split(/\|/, $document);
   print "<ELINKDATA E.BIBID='".trim($tokens[1])."' E.MFHDID='".trim($tokens[3])."'>\n";
   #print "<ELINKDATA>\n";
   #print "<E.BIBID>\n";
	#print trim($tokens[1]);
   #print "</E.BIBID>\n";
   #
   #print "<E.MFHDID>";
                #print trim($tokens[3]);
   #print "</E.MFHDID>\n";
   #
   # do not parse url string, return character data as is
   #
   print "<E.LINK><![CDATA[".trim($tokens[5])."]]>";
   print "</E.LINK>\n";
   #
   print "<E.LINKTEXT>";
	 print trim($tokens[7]);
   print "</E.LINKTEXT>\n";
   #
 print "</ELINKDATA>";
 `rm $Fname`;
} else {
   # ERROR return
   #
   print "<ELINKDATA></ELINKDATA>\n";
} 

