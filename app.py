import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome import service as fs


item_ls = []
item_url_ls=[]

def browser_setup():
    """ブラウザを起動する関数"""
    #ブラウザの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #ブラウザの起動
    # webdriver_managerによりドライバーをインストール
    CHROMEDRIVER = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()  # chromiumを使用したいので引数でchromiumを指定しておく
    service = fs.Service(CHROMEDRIVER)
    browser = webdriver.Chrome(
        options=options,
        service=service
    )
    browser.implicitly_wait(3)
    return browser


def get_url(KEYWORD , browser):
    #売り切れ表示
    url = 'https://jp.mercari.com/search?keyword=' + KEYWORD + '&status=sold_out%7Ctrading'
    browser.get(url)
    browser.implicitly_wait(5)

    #商品の詳細ページのURLを取得する
    item_box = browser.find_elements(By.CSS_SELECTOR, '#item-grid > ul > li')
    for item_elem in item_box:
        item_urls = item_elem.find_elements(By.CSS_SELECTOR, 'a')
        for item_url in item_urls:
            item_url_ls.append(item_url.get_attribute('href'))


def is_contained(target_str, search_str):
    """
    target_str に search_str が含まれるかどうかを判定する関数
    """
    if target_str.find(search_str) >= 0:
        return True
    else:
        return False


def page_mercari_com(browser):
    #商品名 
    item_name = browser.find_element(By.CSS_SELECTOR,'#item-info > section:nth-child(1) > div.mer-spacing-b-12').text
    # 商品説明
    shadow_root = browser.find_element(By.CSS_SELECTOR,'#item-info > section:nth-child(2) > mer-show-more').shadow_root
    item_ex = shadow_root.find_element(By.CSS_SELECTOR,'div.content.clamp').text
    # 価格
    item_price = browser.find_element(By.CSS_SELECTOR, '#item-info [data-testid="price"] > span:last-child').text
    # 画像のURL
    src = browser.find_element(By.CSS_SELECTOR,'div.slick-list div[data-index="0"] img').get_attribute('src')

    return item_name , item_ex , item_price , src


def page_mercari_shop_com(browser):
    #商品名 
    item_name = browser.find_element(By.CSS_SELECTOR, 'h1.chakra-heading.css-159ujot').text
    # 商品説明
    item_ex = browser.find_element(By.CSS_SELECTOR,'div.css-0 div.css-1x15fb3 p').text
    # 価格
    item_price = browser.find_element(By.CSS_SELECTOR,'.chakra-stack.css-xerlbm .css-x1sij0 .css-1vczxwq').text
    # 画像のURL
    src = browser.find_element(By.CSS_SELECTOR, 'div.css-1f8sh1y img').get_attribute('src')

    return item_name , item_ex , item_price , src


def get_data(browser):
    #商品情報の詳細を取得する
    count = 0
    st.write("全商品数", len(item_url_ls) , "個を取得中")
    for item_url in item_url_ls:
        browser.get(item_url)
        time.sleep(3)

        #商品名〜画像URLを取得
        if is_contained(item_url, "shop"):  # 商品詳細ページが「mercari-shops.com」の場合
            item_name , item_ex , item_price , src = page_mercari_shop_com(browser)
        else:  # 商品詳細ページが「mercari.com」の場合
            item_name , item_ex , item_price , src = page_mercari_com(browser)
        
        data = {
            '商品名':item_name,
            '商品説明':item_ex,
            '価格':item_price,
            'URL':item_url,
            '画像URL':src
        }
        item_ls.append(data)

        item_url_ls_10 = len(item_url_ls) % 10
        if count % 10 == 0  and  count < len(item_url_ls) - item_url_ls_10 :  # count : 0〜9 , 10〜19 , 20〜29
            st.write(count + 1, "〜" , count + 10, "まで完了")
        if item_url_ls_10 != 0  and  count == len(item_url_ls) - item_url_ls_10 :
            st.write(count + 1, "〜" , len(item_url_ls) , "まで完了")
        count = count + 1


def main():
    KEYWORD = ""
    st.title("メルカリ売れ行き商品を一括取得")
    st.write("<p></p>", unsafe_allow_html=True)
    KEYWORD = st.text_input("検索キーワード")
    st.write("<p></p>", unsafe_allow_html=True)

    if KEYWORD != "":
        browser = browser_setup()
        get_url(KEYWORD , browser)
        get_data(browser)
        df = pd.DataFrame(item_ls)
        csv = df.to_csv(index=False)

        # CSVファイルのダウンロードボタンを表示
        st.download_button(
            label='CSVをダウンロード',
            data=csv,
            file_name='メルカリデータ.csv',
            mime='text/csv'
        )


if __name__ == '__main__':
    main()
