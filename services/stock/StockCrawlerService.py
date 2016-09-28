#encoding: utf-8

import urllib2
import re
import time
from log.Logger import logger
from services.stock.StockService import StockService
from storages.stock.StockStorage import StockStorage
from models.stock.StockBaseModel import StockBaseModel
from models.stock.StockModel import StockModel
from models.stock.StockCategoryModel import StockCategoryModel
from models.stock.StockTradeModel import StockTradeModel

class StockCrawlerService(object):
	"""网络抓取股票相关数据服务"""
	def __init__(self):
		super(StockCrawlerService, self).__init__()

	@staticmethod
	def fetchAllStockBaseModelsFromInternet():
		"""从东方财富网抓取所有股票代码、名字及所属市场"""
		try:
			response = urllib2.urlopen(urllib2.Request('http://quote.eastmoney.com/stocklist.html')).read()
			pattern = re.compile(r'(<li><a target="_blank" href="http://quote\.eastmoney\.com/.+\.html">.+\(\d{6}\)</a></li>)', re.MULTILINE)
			rows = pattern.findall(response)

			pattern = re.compile(r'<li><a target="_blank" href="http://quote\.eastmoney\.com/([a-zA-Z]{2,})\d+\.html">(.+)\((\d{6})\)</a></li>')
			for row in rows:
				matches = pattern.match(row)
				if matches:
					# 去年基金、证券等非股票代码
					stockCode = matches.group(3).decode('gbk')
					if stockCode.startswith('600') or stockCode.startswith('601') or stockCode.startswith('603') \
									or stockCode.startswith('002') or stockCode.startswith('300') or stockCode.startswith('000'):
						stockBaseModel = StockBaseModel(None, matches.group(3), matches.group(2).decode('gbk').encode('utf-8'), matches.group(1))
						try:
							StockStorage.saveStockBaseModel(stockBaseModel)
							logger.info('%s(%s) - new stockCode fetched' % (stockBaseModel.stockName, stockBaseModel.stockCode))
							StockCrawlerService.fetchStockCategoryRelationsFromInternet(stockBaseModel)
						except Exception, e:
							pass
						finally:
							pass
		except urllib2.HTTPError, e:
			logger.error('%s' % (e))
		except Exception, e:
			logger.error('%s' % (e))
		finally:
			pass

	@staticmethod
	def fetchDailyStockModelFromInternet(stockBaseModel, date = None):
		"""从东方财富网抓取一只股票当天的行情数据"""
		if not date:
			date = time.strftime('%Y-%m-%d', time.localtime())

		try:
			url = 'http://nufm2.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?' \
				'type=CT&sty=FDT&token=beb0a0047196124721f56b0f0ff5a27c&cmd=%s' % (stockBaseModel.getEastMoneyStockCode())
			response = urllib2.urlopen(urllib2.Request(url)).read()
			pattern = re.compile(r'\(\["(.*)"\]\)')
			matches = pattern.match(response)
			if matches:
				stockModel = StockModel.stockModelFromList(matches.group(1).split(','))
				stockModel.stockId = stockBaseModel.id
				stockModel.updateDate = date

				try:
					url2 = 'http://hqchart.eastmoney.com/hq20/js/%s.js?202224' % (stockBaseModel.stockCode)
					response2 = urllib2.urlopen(urllib2.Request(url2)).read()
					pattern2 = re.compile(r'var zjlx_detail=\{data\:\"(.*)\",update.*')
					matches2 = pattern2.search(response2)
					if matches2:
						list = matches2.group(1).split(',')
						stockModel.superFlowIn = float(list[12])
						stockModel.superFlowOut = float(list[13])
						stockModel.bigFlowIn = float(list[14])
						stockModel.bigFlowOut = float(list[15])
						stockModel.middleFlowIn = float(list[16])
						stockModel.middleFlowOut = float(list[17])
						stockModel.littleFlowIn = float(list[18])
						stockModel.littleFlowOut = float(list[19])

						StockStorage.saveStockModel(stockModel)
						logger.info('stock %s daily model fetched successfully' % stockBaseModel.stockCode)
				except urllib2.HTTPError, e:
					logger.error('%s - %s' % (stockBaseModel.stockCode, e))
				except Exception, e:
					logger.error('%s - %s' % (stockBaseModel.stockCode, e))
				finally:
					pass

		except urllib2.HTTPError, e:
			logger.error('%s - %s' % (stockBaseModel.stockCode, e))
		except Exception, e:
			logger.error('%s - %s' % (stockBaseModel.stockCode, e))
		finally:
			pass

	@staticmethod
	def fetchAllStockCategoryModelsFromInternet():
		"""从东方财富网抓取所有股票板块信息"""
		try:
			categories = ['trade', 'notion', 'area']
			for i in range(0,3):
				response = urllib2.urlopen(urllib2.Request('http://quote.eastmoney.com/hq2data/bk/data/%s.js' % categories[i])).read()
				pattern = re.compile(r'var BKCache = \{(Trade|Notion|Area)\:\[\[(.*)\]\]\};')
				matches = pattern.match(response)
				if matches:
					result = matches.group(2)
					rows = result[1:len(result)-1].split('","')
					for j in range(0, (len(rows)+1)/2):
						row = rows[j]
						l = row.split(',')
						stockCategoryModel = StockCategoryModel(None, l[0].decode('gbk').encode('utf-8'), i+1)
						StockStorage.saveStockCategoryModel(stockCategoryModel)
		except Exception, e:
			logger.error('%s - %s' % (stockBaseModel.stockCode, e))
		finally:
			pass

	@staticmethod
	def fetchStockCategoryRelationsFromInternet(stockBaseModel):
		"""从东方财富网抓取一只股票所属的板块"""
		l = []
		try:
			url = 'http://hqchart.eastmoney.com/hq20/js/%s.js' % stockBaseModel.stockCode
			response = urllib2.urlopen(urllib2.Request(url)).read()

			pattern = re.compile(r'var zjlx_bk=\[(.*)\];var zjlx_rank')
			matches = pattern.search(response)
			if matches:
				rows = matches.group(1)[1:len(matches.group(1))-1].split('],[')
				for row in rows:
					if row:
						categoryName = row.split(',')[0]
						categoryName = categoryName[1:len(categoryName)-1]
						l.append(categoryName)
		except Exception, e:
			logger.error('%s - %s' % (stockBaseModel.stockCode, e))
		finally:
			return l

	@staticmethod
	def fetchAllStockCategoryRelationsFromInternet():
		"""从东方财富网抓取所有股票所属的板块"""
		dict = {}
		categories = StockService.getAllStockCategoryModels()
		for category in categories:
			dict[category.categoryName.encode('utf-8')] = category

		stocks = StockService.getAllStockBaseModels()
		for stock in stocks:
			l = StockCrawlerService.fetchStockCategoryRelationsFromInternet(stock)
			for s in l:
				category = dict.get(s)
				if category:
					StockStorage.saveStockCategoryRelation(stock, category)
					pass
				else:
					logger.info('%s no category fetched' % (stock.stockCode))

	@staticmethod
	def fetchStockTradeInfoFromInternet(stockBaseModel, date = None):
		"""从东方财富网抓取一只股票当天所有的成交信息"""
		if not date:
			date = time.strftime('%Y-%m-%d', time.localtime())

		date = date + ' '

		try:
			url = 'http://hqdigi2.eastmoney.com/EM_Quote2010NumericApplication/CompatiblePage.aspx?Type=OB&stk=%s&Reference=xml&limit=0&page=%s'
			page = 1
			totalPages = 0
			while True:
				response = urllib2.urlopen(urllib2.Request(url % (stockBaseModel.getEastMoneyStockCode(), page))).read()

				pattern = re.compile(r'var jsTimeSharingData=\{pages\:(\d+),data\:\[(.*)\]\};')
				matches = pattern.match(response)

				if matches and matches.group(2):
					totalPages = int(matches.group(1))
					rows = matches.group(2)[1:len(matches.group(2))-1].split('","')
					for row in rows:
						if row:
							metas = row.split(',')
							stockTradeModel = StockTradeModel(None, stockBaseModel.id, date + metas[0], float(metas[1]), int(metas[2]), int(metas[3]))
							StockStorage.saveStockTradeModel(stockTradeModel)

				if page < totalPages:
					page = page + 1
				else:
					break
		except urllib2.HTTPError, e:
			logger.error('%s - %s' % (stockBaseModel.stockCode, e))
		except Exception, e:
			logger.error('%s - %s' % (stockBaseModel.stockCode, e))
		finally:
			pass
