# coding=utf-8
from DataParser.DataParserBase import DataParserBase

__author__ = 'guangde'


class ZhongtongDataParser(DataParserBase):
	def __init__(self, file_path):
		DataParserBase.__init__(self, file_path)
		self.info = {'order_key': u'运单编号',
		             'province_key': u'签收省份',
		             'weight_key': u'重量',
		             'price_key': u'价格',
		             'continue_key': u'邮件综合查询',
		             'left_break_key': u'',
		             'right_break_key': u''}
		self.company_pinyin = 'zhongtong'
		self.company_name = '中通'

	def calculate_extra_weight(self, unit, extra_weight):
		return self.kg(extra_weight) if unit == 'kg' else extra_weight
