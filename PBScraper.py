import requests as r
from pathlib import Path
import sys
import time
import FIO

# The URL requests uses to make the API call
# The {} is replaced with the language key
scrape_url = "https://scrape.pastebin.com/api_scraping.php?lang={}"

# The location to download the files
download_dir = Path("downloads")

# A list of languages to download by language key 
# Language keys are found at https://pastebin.com/api#5
languages = ["php", "c", "cpp", "java", "python", "javascript", "go"]

NUM_TO_GATHER = 1000

# Gathered is a dictionary of <string, set> matching
# where the key is the language key and the value is a set of
# downloaded paste keys
gathered = dict()

TIME_BETWEEN_SCRAPES = 50
time_since_last_scrape = TIME_BETWEEN_SCRAPES

def sleep(sleep_time):
   """Causes the program to sleep for sleep_time seconds
      Works along with scrape_sleep to assure TIME_BETWEEN_SCRAPES
      seconds between language scraping attempts
   """
   global time_since_last_scrape
   time.sleep(sleep_time)
   time_since_last_scrape += sleep_time

def scrape_sleep():
   """Provides a buffer between each language scraping attempt
      The sleep time is defined by TIME_BETWEEN_SCRAPES
   """
   global time_since_last_scrape
   left = TIME_BETWEEN_SCRAPES - time_since_last_scrape
   if left > 0:
      sys.stdout.write("Peforming scrape sleep for {} seconds".format(left))
      sys.stdout.flush()
   while TIME_BETWEEN_SCRAPES - time_since_last_scrape > 0:
      sleep(1)
      sys.stdout.write('.')
      sys.stdout.flush()
   # Make sure a new line is created
   print('')
   time_since_last_scrape = 0
      
def is_all_gathered():
   """ Determines if all languages have had their download goals
       accomplished
   """
   for lang in gathered:
      if len(gathered[lang]) < NUM_TO_GATHER:
         return False
   return True

if __name__ == "__main__":
   # Build the dictionary of items already downloaded
   # ensures the program can resume if interrupted
   for lang in languages:
      lang_dir = download_dir / lang
      if lang_dir.is_dir():
         # Build a set of every item in the download location
         # item.parts[-1] provides the file name without directory info
         gathered[lang] = {item.parts[-1] for item in lang_dir.iterdir()}
      else:
         gathered[lang] = set()
   
   # Loop, downloading more files as they are available
   while not is_all_gathered():
      for lang in languages:
         if len(gathered[lang]) > NUM_TO_GATHER:
            print("Skipping", lang)
            continue
         print("Scraping", lang)
         scrape_sleep()
         scrape_list = r.post(scrape_url.format(lang)).json()
         lang_dir = download_dir / lang
         for item in scrape_list:
            if len(gathered[lang]) >= NUM_TO_GATHER:
               break
            key = item["key"]
            syntax = item["syntax"]
            if (syntax != lang):
               print("Syntax {} not equal to lang {}".format(syntax, lang))
               continue
            if key not in gathered[lang]:
               item_text = r.post(item["scrape_url"]).text
               FIO.write_file(str(lang_dir), key, item_text)
               gathered[lang].add(key)
               print("Gathered {}, total {}, lang {}".format(key, len(gathered[lang]), lang))
               sleep(1)
