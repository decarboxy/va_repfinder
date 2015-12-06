# va_repfinder
The website for finding out what VA stat district you're in isn't accessible to the visually impaired.

This is a quick and dirty hack to fix this problem, its a Flask app that loads up a headless firefox instance, loads http://whosmy.virginiageneralassembly.gov, performs the search, scrapes the relevant information and returns it in a simple format thats easy for screen readers.