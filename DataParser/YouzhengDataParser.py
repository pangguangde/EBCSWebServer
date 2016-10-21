# coding=utf-8
import csv

import xlrd

from DataParser.DataParserBase import DataParserBase

__author__ = 'guangde'

from setting import *


class YouzhengDataParser(DataParserBase):
	def __init__(self, file_path):
		DataParserBase.__init__(self, file_path)
		self.info = {'order_key': u'邮件号',
		             'province_key': u'寄达省份',
		             'weight_key': u'重量',
		             'price_key': u'邮资',
		             'continue_key': u'邮件综合查询',
		             'left_break_key': u'合计',
		             'right_break_key': u''}
		self.company_pinyin = 'youzheng'
		self.company_name = '邮政'

	def parse_csv(self):
		count = 0
		if self.file_path.find('/') >= 0:
			filename = self.file_path.split('/')[-1]
		else:
			filename = self.file_path.split('\\')[-1]
		self.logger.info(u'加载' + filename + u'数据')
		csvfile = file(self.file_path, 'r+')
		reader = csv.reader(csvfile)
		all_dict = {}
		orders = []
		order_col = None
		province_col = None
		weight_col = None
		price_col = None
		for column in reader:
			if not weight_col:
				if column[0] == self.info['continue_key']:
					continue
				order_col = column.index(self.info['order_key'])
				province_col = column.index(self.info['province_key'])
				weight_col = column.index(self.info['weight_key'])
				price_col = column.index(self.info['price_key'])
				continue
			else:
				order = column[order_col]
				province = column[province_col]
				weight = float(column[weight_col]) / 1000
				price = column[price_col]
				cpname = self.company_name
			if column[0] == self.info['left_break_key'] or column[-1] != self.info['right_break_key']:
				break
			if all_dict.has_key(order):
				orders.append(order)
				count += 1
			else:
				all_dict.setdefault(order, {'province': province, 'price': price, 'weight': weight, 'cpname': cpname})
		s = u'%s%s 重复运单号(%s).csv' % (RESULT_DIR, filename, count)
		print u'%s 数据已经加载完毕,重复数：%s' % (filename, count)
		csvfile = file(s, 'w+')
		writer = csv.writer(csvfile)
		writer.writerow(['运单号'])
		writer.writerows([[o] for o in orders])
		csvfile.close()
		self._data = all_dict

	def parse_xls(self):
		count = 0
		if self.file_path.find('/') >= 0:
			filename = self.file_path.split('/')[-1]
		else:
			filename = self.file_path.split('\\')[-1]
		self.logger.info(u'加载' + filename + u'数据')
		workbook = xlrd.open_workbook(self.file_path)
		sheet = workbook.sheet_by_index(0)
		all_dict = {}
		orders = []
		order_col = sheet.row_values(1).index(self.info['order_key'])
		province_col = sheet.row_values(1).index(self.info['province_key'])
		weight_col = sheet.row_values(1).index(self.info['weight_key'])
		price_col = sheet.row_values(1).index(self.info['price_key'])
		for i in range(2, 1000000):
			row_data = sheet.row_values(i)
			order = row_data[order_col]
			province = row_data[province_col]
			weight = float(row_data[weight_col]) / 1000
			price = row_data[price_col]
			cpname = self.company_name
			if row_data[0] == self.info['left_break_key'] or row_data[-1] != self.info['right_break_key']:
				break
			if all_dict.has_key(order):
				orders.append(order)
				count += 1
			else:
				all_dict.setdefault(order, {'province': province, 'price': price, 'weight': weight, 'cpname': cpname})
		s = u'%s%s 重复运单号(%s).csv' % (RESULT_DIR, filename, count)
		print u'%s 数据已经加载完毕,重复数：%s' % (filename, count)
		csvfile = file(s, 'w+')
		writer = csv.writer(csvfile)
		writer.writerow(['运单号'])
		writer.writerows([[o] for o in orders])
		csvfile.close()
		self._data = all_dict