# Music Tool
A tool to help update and organize mp3 files. Created this for fun and because I had a large number of mp3 files with 
incorrect metadata that I wanted to update. I can't add these songs to my playlist while they are so chaotic. 

## Updates to come

* Add a button to automatically set the album and artist data based on the folder structure
  * Given a src folder, all subfolders should be set up as src/artist/album
  * All files in src/ will be ignored
  * All files in /src/artist/ will have the album removed
* Account for comments, artwork, and other tags that aren't covered by EasyMP3
* Use an API to pull the song information from the internet and autofill where possible
