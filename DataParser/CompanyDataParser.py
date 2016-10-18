# coding=utf-8
import csv

from DataParser.DataParserBase import DataParserBase

__author__ = 'guangde'


class CompanyDataParser(DataParserBase):
	def __init__(self, file_path):
		DataParserBase.__init__(self, file_path)
		self.info = {'order_key': '运单编号',
		             'province_key': '目的地',
		             'weight_key': '计费重量',
		             'price_key': '总运费',
		             'continue_key': '邮件综合查询',
		             'left_break_key': '',
		             'right_break_key': ''}
		self.repeat_orders = []
		self.repeat_count = 0

	def _parse_company_csv(self, file_path):
		if file_path.find('/') >= 0:
			filename = file_path.split('/')[-1]
		else:
			filename = file_path.split('\\')[-1]
		self.logger.info(u'加载' + filename + u'数据')
		csvfile = file(file_path, 'r+')
		reader = csv.reader(csvfile)
		cpname_col = None
		order_col = None
		province_col = None
		weight_col = None
		for row_data in reader:
			row_data = [s.decode('gbk') for s in row_data]
			if not weight_col:
				cpname_col = row_data.index(u'快递公司名称')
				order_col = row_data.index(u'快递单号')
				province_col = row_data.index(u'省')
				weight_col = row_data.index(u'订单毛重')
				continue
			else:
				price = 0
				cpname = row_data[cpname_col]
				order = row_data[order_col]
				province = row_data[province_col]
				weight = row_data[weight_col]
			if row_data[0] == u'0':
				break
			if self._data.has_key(order):
				self.repeat_orders.append(order)
				self.repeat_count += 1
			else:
				self._data.setdefault(order, {'province': province, 'price': price, 'weight': weight, 'cpname': cpname})
		self.logger.info(u'加载完成')

	def parse_csv(self):
		for fname in self.file_path.split(u'+'):
			self._parse_company_csv(fname)
		s = u'内部混合文件 重复运单号(%s).csv' % self.repeat_count
		print u'内部混合所有文件已经加载完毕,重复数：%s' % self.repeat_count
		csvfile = file(s, 'w+')
		writer = csv.writer(csvfile)
		writer.writerow(['运单号'])
		writer.writerows([[o] for o in self.repeat_orders])
		csvfile.close()

	@property
	def csv_data(self):
		if not self._data:
			self.parse_csv()
		return self._data