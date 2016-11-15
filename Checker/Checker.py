# coding=utf-8
import csv

import xlsxwriter

from Logger.Logger import Logger
from setting import *

__author__ = 'guangde'


class Checker(object):
	def __init__(self, company_obj, waibu_obj):
		self.waibu_obj = waibu_obj
		self.company_obj = company_obj
		self.logger = Logger()

	def check(self):
		company_name = self.waibu_obj.company_name
		self.logger.info('计算%s数据' % company_name)
		data = []
		data_1 = []

		company_dict = self.company_obj.csv_data
		waibu_dict = self.waibu_obj.csv_data

		workbook = xlsxwriter.Workbook(u'%s比对结果(%s).xlsx' % (RESULT_DIR, company_name.decode('utf8')))
		worksheet = workbook.add_worksheet()

		format_1 = workbook.add_format({'bold': True, 'font_color': 'red', 'align': 'right'})
		format_2 = workbook.add_format({'bold': False, 'font_color': 'green', 'align': 'right'})
		format_3 = workbook.add_format({'bold': False, 'font_color': 'gray', 'align': 'right'})
		format_4 = workbook.add_format({'align': 'right'})
		column_num = 1
		worksheet.write(0, 0, u'运单号')
		worksheet.write(0, 1, u'省份')
		worksheet.write(0, 2, u'毛重(外)')
		worksheet.write(0, 3, u'毛重')
		worksheet.write(0, 4, u'毛重差(外-内)')
		worksheet.write(0, 5, u'价格(外)')
		worksheet.write(0, 6, u'价格')
		worksheet.write(0, 7, u'价格差(外-内)')
		cp_count = 0
		for item in company_dict.items():
			if waibu_dict.has_key(item[0]):
				cp_count += 1
				waibu_weight = float(waibu_dict[item[0]]['weight'])
				company_weight = float(item[1]['weight'])
				waibu_price = float(waibu_dict[item[0]]['price'])
				company_price = self.waibu_obj.calculate_price(company_weight, waibu_dict[item[0]]['province'])
				weight_diff = waibu_weight - company_weight
				price_diff = float('%.4f' % (waibu_price - company_price))
				if price_diff > 0:
					data_1.append([price_diff, (
						item[0],
						item[1]['province'],
						'%.3f' % waibu_weight,
						'%.3f' % company_weight,
						'%.3f' % weight_diff,
						'%.2f' % waibu_price,
						'%.2f' % company_price,
						'%.2f' % price_diff
					)])
		print 'compare count=%s' % cp_count
		data_1.sort(reverse=True)
		for i in data_1:
			data.append(i[0])
			worksheet.write(column_num, 0, i[1][0].decode('utf8'))
			worksheet.write(column_num, 1, i[1][1])
			worksheet.write(column_num, 2, i[1][2].decode('utf8'), format_4)
			worksheet.write(column_num, 3, i[1][3].decode('utf8'), format_4)
			if float(i[1][4]) > 0:
				worksheet.write(column_num, 4, i[1][4].decode('utf8'), format_1)
			elif float(i[1][4]) < 0:
				worksheet.write(column_num, 4, i[1][4].decode('utf8'), format_2)
			else:
				worksheet.write(column_num, 4, i[1][4].decode('utf8'), format_3)
			worksheet.write(column_num, 5, i[1][5].decode('utf8'), format_4)
			worksheet.write(column_num, 6, i[1][6].decode('utf8'), format_4)
			worksheet.write(column_num, 7, i[1][7].decode('utf8'), format_1)
			column_num += 1
		worksheet.write(column_num, 0, u'总计')
		worksheet.write(column_num, 1, '')
		worksheet.write(column_num, 2, '')
		worksheet.write(column_num, 3, '')
		worksheet.write(column_num, 4, '')
		worksheet.write(column_num, 5, '')
		worksheet.write(column_num, 6, '')
		worksheet.write(column_num, 7, sum(data))
		workbook.close()

		waibu_list = [item for item in waibu_dict.keys()]
		company_list = []
		ucn = company_name.decode('utf8')
		for item in company_dict.items():
			if item[1]['cpname'] == ucn:
				company_list.append(item[0])
		waibu_set = set(waibu_list)
		company_set = set(company_list)

		extra_wai = waibu_set - company_set
		extra_nei = company_set - waibu_set

		self.logger.info('检查不互有的运单')
		print u'外部有而公司没有的运单数: %s' % len(extra_wai)
		csvfile = file(u'%s外部有而公司没有的运单号(%s-%s).csv' % (RESULT_DIR, company_name.decode('utf8'), len(extra_wai)), 'wb')
		writer = csv.writer(csvfile)
		writer.writerow(['运单号'])
		writer.writerows([[o] for o in extra_wai])
		print u'公司有而外部没有的运单数: %s' % len(extra_nei)
		csvfile = file(u'%s公司有而外部没有的运单号(%s-%s).csv' % (RESULT_DIR, company_name.decode('utf8'), len(extra_nei)), 'wb')
		writer = csv.writer(csvfile)
		writer.writerow(['运单号'])
		writer.writerows([[o] for o in extra_nei])
		print '-' * 60
		csvfile.close()
