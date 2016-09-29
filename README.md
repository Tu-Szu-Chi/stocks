# stocks
每天从网上抓取股票数据并保存到本地以供分析
## 配置教學
###需安裝「MySQLdb Library」
  >可用 "pip install MySQL-python"
  >
- - -
###storages/BaseStorage.py 需更改DB設定
  >[host],[user],[passwd],[db],[charset]
  >
- - -
###main.py
  >初次跑此程式需把
  >>line:14 StockCrawlerService.fetchAllStockBaseModelsFromInternet()
  >>line:16 StockCrawlerService.fetchAllStockCategoryModelsFromInternet()
  >執行過一遍(將註解拿掉)，有了標的&類別存在DB，之後就不用再執行此二行了
- - -
