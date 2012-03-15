#!/usr/bin/perl -w
# FILE: getbibdataxml.cgi
# DATE: 02/26/2012
# AUTH: CUMMINGS
# DESC: Responds to url in the having the following structure 
# http://gwdroid.wrlc.org/cgi-bin/getbibdataxml.cgi?bibid=7982447
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

# query generates pipe delimited file as output. eg /tmp/bibdata300000.txt
`sh bibdataquery.sh $formdata{bibid}`;
my $Fname="/tmp/bibdata".$formdata{bibid}.".txt";
if (-s $Fname) {
	open FILE, $Fname or dienice("Unable to open output file");
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

 print "</BIBDATA>";
 `rm $Fname`;
} else {
   # ERROR return
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

