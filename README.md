# dbcompare

Super Alpha stage, still in progress and has many errors.

Inefficient db comparison tool that work with two databases, usually a new and old backup. It takes the values from one table in the database and compares it to the same table in the other. If the value is found it deletes it from table in the newer databases. Whatever is left in the new database in the end is the new/modified data. This will be a crap tool for large databases but works decent on small and okay on medium sized ones.
