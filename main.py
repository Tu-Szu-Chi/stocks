#encoding: utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from services.stock.StockService import StockService
from services.stock.StockCrawlerService import StockCrawlerService
from models.stock.StockBaseModel import StockBaseModel
from models.stock.StockModel import StockModel

if __name__ == '__main__':
	StockCrawlerService.fetchAllStockBaseModelsFromInternet() #首次使用前須先執行，才可Fetch所有'標的'下來

	StockCrawlerService.fetchAllStockCategoryModelsFromInternet() #首次使用前須先執行，才可Fetch所有'類別'下來

	l = StockService.getAllStockBaseModels()
	for model in l:
		StockCrawlerService.fetchDailyStockModelFromInternet(model)

	l = StockService.getAllStockBaseModels()
	for model in l:
		StockCrawlerService.fetchStockTradeInfoFromInternet(model)

	# stockBaseModel = StockBaseModel(62, '502000', '', 'sh') #可以指定標的代碼來爬資料
	# StockCrawlerService.fetchDailyStockModelFromInternet(stockBaseModel)
