# coding=utf-8
import xlrd

from Logger.Logger import Logger

__author__ = 'guangde'

import csv
import json
import traceback

from setting import *



class DataParserBase(object):
	def __init__(self, file_path):
		self.info = {}
		self._data = {}
		self.file_path = file_path
		self.company_pinyin = ''
		self.company_name = ''
		self.logger = Logger()

	def calculate_extra_weight(self, unit, extra_weight):
		return self.kg(extra_weight) if unit == 'kg' else self.hectogram(extra_weight)

	def calculate_price(self, weight, province):
		price_dict = self.get_old_split_data()
		try:
			prov_key = province[:2]
			extra_price_info = price_dict[prov_key]['extra_price']
			weight_line_info = price_dict[prov_key]['weight_line']
			for i in range(0, len(weight_line_info)):
				if weight_line_info[i][0][0] <= weight <= weight_line_info[i][0][1]:
					return float('%.4f' % weight_line_info[i][1])
			extra_weight = weight - weight_line_info[-1][0][1]
			extra_weight = self.calculate_extra_weight(extra_price_info[1], extra_weight)
			price = weight_line_info[-1][1] + extra_weight * extra_price_info[0]
			return float('%.4f' % price)
		except Exception, e:
			exstr = traceback.format_exc()
			print exstr

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
		order_col = sheet.row_values(0).index(self.info['order_key'])
		province_col = sheet.row_values(0).index(self.info['province_key'])
		weight_col = sheet.row_values(0).index(self.info['weight_key'])
		price_col = sheet.row_values(0).index(self.info['price_key'])
		for i in range(1, 1000000):
			row_data = sheet.row_values(i)
			order = row_data[order_col]
			province = row_data[province_col]
			weight = row_data[weight_col]
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
				weight = column[weight_col]
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

	@property
	def csv_data(self):
		if not self._data:
			self.parse_xls()
		return self._data

	@classmethod
	def kg(cls, weight):
		weight = float('%.5f' % weight)
		return int(weight) if (int(weight) == weight) else (int(weight) + 1)

	@classmethod
	def hectogram(cls, weight):
		weight = float('%.5f' % weight)
		a = weight * 10
		return int(a) if (int(a) == a) else (int(a) + 1)

	def get_old_split_data(self):
		data = json.load(open('%s/res/%s_price_split.json' % (PROJECT_DIR, self.company_pinyin), 'r+'))
		new_data = {}
		for infos in data.values():
			for k, v in infos.items():
				new_data[k] = v
		return new_data
