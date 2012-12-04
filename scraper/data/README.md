this folder holds data that has already been scraped, so the server doesn't need to support scraping for old data formats.
to import the data, make the files in this folder (except README.md) into a tar.bz2 archive and then use model.db.restore to put it in the database.
this task should probably be automated when the database is being reset
PS: this data is left uncompressed to make it easier to track changes / corrections done to the data