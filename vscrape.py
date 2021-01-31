import os
from os.path import basename
import re
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from PIL import Image
import io
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException
import time
from colorama import Fore, Back, Style, init

# Add some style to this bland text
init(convert=True)


# Function that scrolls to the bottom of the web page


def scroll_to_end(wd):
    # Brings up the chrome window because it is buggy if its minimized and wont grab all images
    driver.switch_to.window(driver.current_window_handle)

    i = 0
    while (i < 5):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        i += 1

    # Brings up the chrome window because it is buggy if its minimized and wont grab all images
    driver.switch_to.window(driver.current_window_handle)

    # Scroll around all areas of the web page to grab and load all images
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight / 3);")
    time.sleep(2)

    driver.switch_to.window(driver.current_window_handle)
    driver.execute_script(
        "window.scrollTo(document.body.scrollHeight, document.body.scrollHeight / 2);")
    time.sleep(2)

    driver.switch_to.window(driver.current_window_handle)
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight / 6);")
    time.sleep(2)


# Subtle flex with a slight warning?
print(str.center(
    Fore.YELLOW + " VScrape " + Style.RESET_ALL, 90, '#'))
print(Fore.YELLOW + "This was developed for company use and might be buggy if used outside of company websites")

print(Style.RESET_ALL)

# This sets up options and headless chrome browser, so users don't need to see a chrome window popup (OPTIONAL)
opts = webdriver.ChromeOptions()
opts.headless = False  # Set to True to Enable Headless Chrome Browser

# This controls the display of logs you see. It hides lower levels. INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3
opts.add_experimental_option('excludeSwitches', ['enable-logging'])

# Auto installs chrome driver and saves it to /driver, this is also where you can add and activate the headless browser
driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)


# The URL we will be targeting
print(Fore.YELLOW + 'Enter the URL you want to target')
print(Fore.YELLOW + 'Please include the http(s) but do not end it with a / please. It will cause errors because this script stoopid')

print(Fore.GREEN + 'Example of good link: https://google.com' + '       ' +
      Fore.RED + 'BAD LINK: https://google.com/  <--- do not end with a forward slash ')

# end=' ' will stop it from making a new line but will add a single space
print(Fore.YELLOW + 'Enter the URL:' + Style.RESET_ALL, end=' ')
driver.minimize_window()
url = input()
driver.get(url)

# Scroll to the bottom of the page to grab as many images as possible
scroll_to_end(driver)
driver.minimize_window()

# Locate the images to be scraped from the current page
img_elements = driver.find_elements(By.TAG_NAME, 'img')
source_elements = driver.find_elements(By.TAG_NAME, 'source')

image_urls = []

# Loop through the image elements
for e in img_elements:

    src = e.get_attribute('src')
    datasrc = e.get_attribute('data-src')

    # Grab style tags and use regex to look for and extract image paths inbetween double quotes
    style_tag = e.get_attribute('style')
    style_tag_img = re.findall('\"(.*?)\"', style_tag)

    print(src)

    # Filter out data paths and src links that lead to google ads
    if not src is None and "data:image/gif" not in str(src) and "googleads" not in str(src):
        # This filters anything with http in it and checks if its an image, if it is, we grab it
        if "http" in str(src) and "png" in str(src):
            print(src)
            image_urls.append(src)
        elif "http" in str(src) and "jpg" in str(src):
            print(src)
            image_urls.append(src)
        elif "png" in str(src) or "jpg" in str(src):
            print(url+src)
            image_urls.append(url+src)

    # Filter out tags with empty data-src
    if not datasrc is None:
        print(url+datasrc)
        image_urls.append(url+datasrc)

    # Filter the style tags by checking for the terms jpg or png
    if "jpg" in style_tag or "png" in style_tag:
        print(url+style_tag_img[0])
        image_urls.append(url+style_tag_img[0])

# Look through the source elements because they also contain images
for e in source_elements:
    srcset = e.get_attribute('srcset')

    # There are many useless src-sets with data paths and more, this will filter them out. We only want image paths
    if not srcset is None and "data:image/gif" not in str(srcset) and "googleads" not in str(srcset):
        # This filters anything with http in it and checks if its an image, if it is, we grab it
        if "http" in str(srcset) and "png" in str(srcset):
            print(srcset)
            image_urls.append(srcset)
        elif "http" in str(srcset) and "jpg" in str(srcset):
            print(srcset)
            image_urls.append(srcset)
        elif "png" in str(srcset) or "jpg" in str(srcset):
            print(url+srcset)
            image_urls.append(url+srcset)

# The \033[32m codes inside the strings are color codes


def downloadImages(folder_path, file_name, url):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"{Fore.RED}ERROR - COULD NOT DOWNLOAD {Style.RESET_ALL} {url} - {e}")
    try:
        image_file = io.BytesIO(image_content)

        # If its a PNG, keep the PNG format
        if ".png" in file_name:
            image = Image.open(image_file).convert('RGBA')
            file_path = os.path.join('', file_name)
            with open(file_path, 'wb') as f:
                image.save(f, "PNG")
            print(f"{Fore.GREEN}SAVED {Style.RESET_ALL} - {url} - AT: {file_path}")
        # Else download as JPEG
        else:
            image = Image.open(image_file).convert('RGB')
            file_path = os.path.join('', file_name)
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG")
            print(f"{Fore.GREEN}SAVED {Style.RESET_ALL} - {url} - AT: {file_path}")

    except Exception as e:
        print(f"{Fore.RED}ERROR - COULD NOT SAVE {Style.RESET_ALL} {url} - {e}")


def saveInDestFolder():
    totalLinks = image_urls

    if totalLinks is None:
        print('No images found')

    else:
        for link in totalLinks:
            file_name = basename(link)
            downloadImages('', file_name, link)

    # Once finished, print out the goodbye message
    print('\033[35m' + str.center(" FINISHED! HAVE A NICE DAY! ",
                                  60, '#') + '\033[0m')
    # Shutdown Selenium and the entire script
    driver.quit()


# START THE SCRIPT LEZ GOOOOOO!!!! CHOO CHOOOOOOO!!!!!! ALL ABOARRRRDDDDDDDD!!!!!!!!!!!!!!
saveInDestFolder()
