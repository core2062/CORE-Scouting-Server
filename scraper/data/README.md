#Data
this folder holds data that has already been scraped, so the server doesn't need to support scraping for old data formats.
to import the data, make the files in this folder (except README.md) into a tar.bz2 archive and then use model.db.restore to put it in the database.
this task should probably be automated when the database is being reset
PS: this data is left uncompressed to make it easier to track changes / corrections done to the data


#Errors
### Not Found (404)

 - http://www2.usfirst.org/2006comp/events/ca/matchsum.html
 - http://www2.usfirst.org/2006comp/events/galileo/matchsum.html
 - http://www2.usfirst.org/2006comp/events/ma/matchsum.html


### No Match Numbers
these didn't have any match numbers for qualifications (so they were added but might be wrong) and eliminations (so `0` was set for all of them). the match numbers for eliminations can't be derived easily, so they were left as `0` until someone finds the correct ones.

 - www2.usfirst.org/2008comp/events/nh/matchresults.html
 - www2.usfirst.org/2008comp/events/il/matchresults.html

