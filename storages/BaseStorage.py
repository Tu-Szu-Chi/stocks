#encoding: utf-8
import MySQLdb

class BaseStorage(object):
	"""docstring for BaseStorage""" #下方[host],[user],[passwd],[db],[charset] 皆需自行設定
	db = MySQLdb.connect(host="192.168.1.5", user="finance", passwd="finance_fb3efc4", db="finance", charset="utf8")
	def __init__(self):
		super(BaseStorage, self).__init__()
