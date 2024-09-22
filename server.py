from flask import Flask, request, jsonify, render_template
import requests
import asyncio
import aiohttp
from urllib import parse
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/search', methods=['GET'])
def suggest():
    # parse url
    product = request.args.get("product")

    def get_product_links(product):
        # encoded = parse.quote(product.encode("utf8"))

        url = "https://www.flipkart.com/search?q={}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off".format(
            product)

        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        all_products = soup.find_all(class_=["_1fQZEK", "_2rpwqI", "_2UzuFa"])

        product_links = []

        for each_product in all_products:
            product_link = each_product.get("href")
            product_link = "https://www.flipkart.com{}".format(product_link)
            product_links.append(product_link)

        return product_links

    product_links = get_product_links(product)

    def get_reviews_link_from_product_page(html):
        soup = BeautifulSoup(html, 'html.parser')

        reviews_link = soup.find_all(class_="JOpGWq")
        reviews_link = reviews_link.find_all("a")
        reviews_link = reviews_link.get("href")

        return reviews_link

    async def get_one_product_reviews(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    links_of_review_pages = []

    async def get_all_product_reviews(product_links):
        tasks = [asyncio.ensure_future(get_one_product_reviews(
            product_link)) for product_link in product_links]
        product_pages = await asyncio.gather(*tasks)

        for page in product_pages:
            soup = BeautifulSoup(page, 'html.parser')

            reviews_link = soup.find(class_="JOpGWq")
            if (not reviews_link):
                continue
            if (not reviews_link.find_all("a")):
                continue
            reviews_link = reviews_link.find_all("a")[-1]
            reviews_link = reviews_link.get("href")
            links_of_review_pages.append(
                "https://www.flipkart.com{}".format(reviews_link))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_all_product_reviews(product_links))

    # for page in links_of_review_pages:
    #     print(page, sep="\n")

    link_and_ratings = []

    async def get_reviews_from_review_pages(links_of_review_pages):
        tasks = [asyncio.ensure_future(get_one_product_reviews(
            link)) for link in links_of_review_pages]
        review_pages = await asyncio.gather(*tasks)

        for page in review_pages:
            soup = BeautifulSoup(page, 'html.parser')

            product_link = soup.find(class_="_2rpwqI")
            product_image = soup.find(class_=["_396cs4", "_2r_T1I"])
            product_image = product_image.get("src") if product_image else ""
            product_title = soup.find(
                class_=["s1Q9rs _2qfgz2", "s1Q9rs _2zdixn"])
            product_title = product_title.text if product_title else ""
            ratings = soup.find_all(class_="_1uJVNT")
            ratings = [rating.text for rating in ratings]

            # print(ratings, sep="\n")

            if (len(ratings) and product_link):
                link_and_ratings.append({
                    "link": "https://www.flipkart.com{}".format(product_link.get("href")),
                    "ratings": [int(rating.replace(",", "")) for rating in ratings],
                    "product_image": product_image,
                    "product_title": product_title
                })

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        get_reviews_from_review_pages(links_of_review_pages))

    # calc percentages
    for item in link_and_ratings:
        ratings = item["ratings"]
        total = sum(ratings)
        positive = ((ratings[0] + ratings[1]) / total) * 100
        neutral = ((ratings[2]) / total) * 100
        negative = ((ratings[3] + ratings[4]) / total) * 100
        item["positive"] = positive
        item["neutral"] = neutral
        item["negative"] = negative

    sorted_products = sorted(
        link_and_ratings, key=lambda i: i['positive'], reverse=True)

    return jsonify(sorted_products)


if __name__ == '__main__':
    app.run(debug=True)
