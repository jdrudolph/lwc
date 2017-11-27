# last weeks commits

## Usage
Create a file with all `.repos` you want to include

	/path/to/some/local/repo
	/path/to/any/other/local/repo

Now you can create the commits file in `markdown` format and optionally generate a `html` version with `pandoc` for easy pasting into e.g. google docs.

	lwc.py --repos .repos > commits.md
	pandoc --from markdown --to html commits.md > commits.html

## Installation

	git clone https://github.com/jdrudolph/lwc.git
