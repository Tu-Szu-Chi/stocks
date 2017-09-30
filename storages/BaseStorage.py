#encoding: utf-8
import MySQLdb

class BaseStorage(object):
	"""docstring for BaseStorage""" #下方[host],[user],[passwd],[db],[charset] 皆需自行設定
	db = MySQLdb.connect(host="172.17.0.2", user="root", passwd="test", db="stock", charset="utf8")
	def __init__(self):
		super(BaseStorage, self).__init__()
