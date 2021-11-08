#!/usr/bin/env python
# coding: utf-8
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_image_urls": hemisphere_image_urls(browser, executable_path)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    # One is that we're searching for elements with a specific combination of tag (div) and attribute (list_text). 
    # As an example, ul.item_list would be found in HTML as <ul class="item_list">.
    # Secondly, we're also telling our browser to wait one second before searching for components. 
    # The optional delay is useful because sometimes dynamic pages take a little while to load, especially if they are image-heavy.
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Setup the html parser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    # Next, we want to click the "Full Image" button. This button will direct our browser to an image slideshow.
    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()
    # With the new page loaded onto our automated browser, it needs to be parsed so we can continue and scrape the full-size image URL
    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

def mars_facts():
    # read_html reads entire tables from html pages
    # The Pandas function read_html() specifically searches for and returns a list of tables found in the HTML. 
    # By specifying an index of 0, we're telling Pandas to pull only the first table it encounters, or the 
    # first item in the list. Then, it turns the table into a DataFrame.
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
      return None
    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    # Pandas also has a way to easily convert our DataFrame back into HTML-ready code using the .to_html() function
    return df.to_html()

def hemisphere_image_urls(browser, executable_path):
    # create lists to hold the image urls and titles
    hemisphere_image_urls = []
    hemisphere_image_urls_exec = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    html = browser.html
    img_soup = soup(html, 'html.parser')
    try:
        # find all div elements with class item and then iterate through the same
        hemisphere_image_urls_exec = img_soup.find_all("div", class_="item")

        for soup_item in hemisphere_image_urls_exec:
            #dictionary to hold image url and title
            hemispheres = {}
            
            # find a tags with the class as itemLink product-item within the div tag 
            image_url = soup_item.find("a", class_="itemLink product-item")
            
            # find the href from the a tag to get the image url
            img_url_rel = image_url['href']
            full_url = f'https://marshemispheres.com/{img_url_rel}'
            
            # get image title description
            title_url = soup_item.find('h3').text
            
            # instamtiate a new browser object to navigate to the full image page for each image
            browser_new = Browser('chrome', **executable_path, headless=True)
            browser_new.visit(full_url)
            html_drilldown = browser_new.html
            img_soup_drilldown = soup(html_drilldown, 'html.parser')
            
            # find the download tg which has the full image url
            download_tag = img_soup_drilldown.find("div", class_="downloads")
            a_tag = download_tag.find("a", attrs={"target" : "_blank"})
            # get the full image url. Gives just the relative path here
            full_res_img = a_tag['href']
            # construct the full image url and store in the dictionary
            hemispheres['img_url'] = f'https://marshemispheres.com/{full_res_img}'
            # store the image title in the dictionary
            hemispheres['title'] = title_url
            #print(hemispheres) # for testing
            
            # copy elements into a new dictionary so that it does not get overwritten in the next iteration
            hemispheres_copy = hemispheres.copy()
            #append the dictionary items to the list to get a list of image urls and titles
            hemisphere_image_urls.append(hemispheres_copy)
            browser_new.back()
            # quit the new automated browsers created to navigate to image pages
            browser_new.quit() 
    except BaseException:
      return None
    # return the list
    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())




