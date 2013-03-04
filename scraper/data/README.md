# Data
this folder holds data that has already been scraped, so the server doesn't need to support scraping for old data formats.
to import the data, make the files in this folder (except README.md) into a tar.bz2 archive and then use model.db.restore to put it in the database.
this task should probably be automated when the database is being reset

This data is left uncompressed to make it easier to track changes / corrections done to the data. the format that it's in is not quite valid JSON (hence the lack of file extensions). Each line is a valid JSON object, but I didn't make all the lines into a giant array because I didn't want to pass them all through simplejson at once... they're just read line-by-line and inserted into the DB.


### Finished Years

 - 2009
 - 2010

### Unfinished Years

 - 2003
 - 2004
 - 2005
 - 2006
 - 2007
 - 2008
 - 2011
 - 2012
 - 2013

# Errors
### Not Found (404)

 - http://www2.usfirst.org/2006comp/events/ca/matchsum.html
 - http://www2.usfirst.org/2006comp/events/galileo/matchsum.html
 - http://www2.usfirst.org/2006comp/events/ma/matchsum.html

### No Match Numbers
these didn't have any match numbers for qualifications (so they were added but might be wrong) and eliminations (so `0` was set for all of them). the match numbers for eliminations can't be derived easily, so they were left as `0` until someone finds the correct ones.

 - www2.usfirst.org/2008comp/events/nh/matchresults.html
 - www2.usfirst.org/2008comp/events/il/matchresults.html

### Other Flaws
data on events before 2003 is not available on the FIRST FMS DB... team history can go back this far

2000 and prior award listings may be incomplete on the FIRST FMS DB

teams which have not been active during the past 3 years are purged from the frc database ... see: http://www.team358org/files/team_lookup/
contact FIRST and see if they still have any of this data?
