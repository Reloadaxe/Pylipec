# Pylipec

Pylipec is a LinkedIn crawler (for LinkedIn 2020). You can't only crawl persons !

## Prerequisites

You need to have chromedriver and the application Google Chrome.

## Installation

```bash
git clone "https://github.com/Reloadaxe/Pylipec.git"
cd Pylipec

python3 -m pip install -r requirements.txt
```

## Configuration

You have to set your LinkedIn email and password, the path to your chrome driver and the path to the Google Chrome binary file

## Usage

```bash
python3 scrape_users.py --help # To show more informations about parameters

exemple:
python3 scrape_users.py -c "conf.json" -p "Benjamin Rousseliere"
```

You can search multiple persons. To do that, just separate names with a comma ("firstname lastname, Lastname Firstname, ...")