# coding=utf-8
import csv
import platform

import sys
import xlrd

from DataParser.DataParserBase import DataParserBase

__author__ = 'guangde'

cur_platform = platform.system()
proj_dir = sys.path[0]
res_dir = '%s/res/' % proj_dir
result_dir = '%s/result/' % proj_dir
tmp_dir = '%s/tmp/' % proj_dir
if cur_platform == 'Windows':
	proj_dir = proj_dir.replace('/', '\\')
	res_dir = res_dir.replace('/', '\\')
	result_dir = result_dir.replace('/', '\\')
	tmp_dir = tmp_dir.replace('/', '\\')


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

