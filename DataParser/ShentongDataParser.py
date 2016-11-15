# coding=utf-8

from DataParser.DataParserBase import DataParserBase

__author__ = 'guangde'


class ShentongDataParser(DataParserBase):
	def __init__(self, file_path):
		DataParserBase.__init__(self, file_path)
		self.info = {'order_key': u'运单编号',
		             'province_key': u'目的地',
		             'weight_key': u'计费重量',
		             'price_key': u'总运费',
		             'continue_key': u'邮件综合查询',
		             'left_break_key': u'',
		             'right_break_key': u''}
		self.company_pinyin = 'shentong'
		self.company_name = '申通'

