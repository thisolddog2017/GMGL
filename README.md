# Morning Post Generator
The program helps generating morning post images from news items in excel.
## How to use
1. Download executables from Release page
2. Input news items into the data.xls file. You may need to fill in at least news_title, news_content and date. But you can delete any column you don't need.
3. The following instruction varies in different operating systems:

    **macOS/Linux**

	Open Terminal in unzipped folder and type:

	`python3 -m pip install -r requirements.txt`

	After installing dependencies you can use the following command to generate news posts in the future:

	`python3 -m main.py`

	**Windows(64 bit)**

	Run main.exe file directly.

4. Image will be generated in the same folder.

## Configuration
|Key in Excel|Note|
|-------------------------------|-----------------------------|
|`news_category`|Used to insert a category separator before a news item starts. Need to enable category in config file.
|`news_title`|News title            |
|`news_content`|News content|
|`url`|News url|
|`date(yyyy/mm/dd)`|Date. You need to specify date format in config file otherwise it is m.d by default with no leading zero (eg. 8.2).|
|`issue_number`|Issue number|

**All options are optional, even news content and news title. You can delete the unneeded columns in Excel.**

## Features
* Font size, font color are adjustable in config.ini.
* No need for Photoshop or image editors.
* Align center support, justification support
