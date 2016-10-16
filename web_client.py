# coding=utf-8
import csv
import json
import os, sys
import traceback
from flask import request
from wtforms import *

import xlsxwriter
from flask import Flask, render_template
from wtforms.validators import Required

app = Flask(__name__)
proj_dir = sys.path[0].replace('/', '\\')
file_list = os.listdir('.')
t = {}

zhongtong_price_split = json.load(open('%s/res/zhongtong_price_split.json' % proj_dir, 'r+'))
shentong_price_split = json.load(open('%s/res/shentong_price_split.json' % proj_dir, 'r+'))
youzheng_price_split = json.load(open('%s/res/youzheng_price_split.json' % proj_dir, 'r+'))


class FilePathForm(Form):
	zhongtong_path = StringField('zhongtong_path')
	shentong_path = StringField('shentong_path')
	youzheng_path = StringField('youzheng_path')
	company_path = StringField('company_path')


class PriceChangeForm(Form):
	company = RadioField('company', choices=[('0', u'中通'), ('1', u'申通'), ('2', u'邮政')], default='0')
	weight_line1 = StringField('weight_line1')
	weight_line2 = StringField('weight_line2')
	weight_line3 = StringField('weight_line3')
	weight_line4 = StringField('weight_line4')
	weight_line5 = StringField('weight_line5')
	price_line1 = StringField('price_line1')
	price_line2 = StringField('price_line2')
	price_line3 = StringField('price_line3')
	price_line4 = StringField('price_line4')
	price_line5 = StringField('price_line5')
	unit = StringField('unit')
	extra_price = StringField('extra_price')
	province = TextAreaField('province')


@app.route('/index/')
def index():
	form = FilePathForm()
	price_change_form = PriceChangeForm()
	zhongtong_price_info = get_merge_data('zhongtong')
	youzheng_price_info = get_merge_data('youzheng')
	shentong_price_info = get_merge_data('shentong')
	t1 = json.load(open('%s/res/shentong_price_merge.json' % proj_dir, 'r+'))

	return render_template('index.html',
	                       form=form,
	                       price_change_form=price_change_form,
	                       init_data={'zhongtong': zhongtong_price_info,
	                                  'youzheng' : youzheng_price_info,
	                                  'shentong' : shentong_price_info})


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
	return render_template('hello.html', name=name)


@app.route('/change_price_info/', methods=['POST', 'GET'])
def change_price_info():
	companies = [{u'中通': 'zhongtong'}, {u'申通': 'shentong'}, {u'邮政': 'youzheng'}]
	company_pinyin = companies[int(request.form['company'])].values()[0]
	data = get_data_from_json_split(company_pinyin)
	province = request.form['province'].split(u'+')
	weight_line = []
	arr = []
	for i in range(1, 6):
		if request.form.get('weight_line%s' % i):
			weight_line_str = request.form.get('weight_line%s' % i).replace(u' ', u'')
			min_num = float(weight_line_str.split(u'x')[0][:-1])
			max_num = float(weight_line_str.split(u'x')[1][1:])
			left = weight_line_str.split(u'x')[0][-1]
			right = weight_line_str.split(u'x')[1][0]
			min_num = min_num if left == u'≤' else min_num + 0.001
			max_num = max_num if right == u'≤' else max_num - 0.001
			price = float(request.form.get('price_line%s' % i))
			weight_line.append([[min_num, max_num], price])
			arr.append(min_num)
			arr.append(max_num)
			arr.append(price)
		else:
			break
	unit = u'kg' if request.form['unit'] == '0' else u'100g'
	extra_price = [float(request.form['extra_price']), unit]
	arr.append(extra_price[0])
	arr.append(unit)
	key = str(arr).decode('utf8')
	for p in province:
		for k, v in data.items():
			if p in v.keys():
				del v[p]
				if len(v) == 0:
					del data[k]
	for p in province:
		if not data.has_key(key):
			data[key] = {}
		data[key][p] = {'weight_line': weight_line, 'extra_price': extra_price}
	json.dump(data, open('%s/res/%s_price_split.json' % (proj_dir, company_pinyin), 'w+'))
	msg = u'%s[%s]的计价规则已更新' % (companies[int(request.form['company'])].keys()[0], u' '.join(province))
	print msg
	return render_template('check_succ.html', msg=msg)


@app.route('/check/', methods=['POST', 'GET'])
def check():
	zhongtong_price_split = json.load(open('%s/res/zhongtong_price_split.json' % proj_dir, 'r+'))
	shentong_price_split = json.load(open('%s/res/shentong_price_split.json' % proj_dir, 'r+'))
	youzheng_price_split = json.load(open('%s/res/youzheng_price_split.json' % proj_dir, 'r+'))
	zhongtong_path = request.form.get('zhongtong_path')
	shentong_path = request.form.get('shentong_path')
	youzheng_path = request.form.get('youzheng_path')
	company_path = request.form.get('company_path')
	count = 0
	count_str = u''
	if company_path:
		if not os.path.exists(company_path):
			msg = u'内部混合文件不存在:%s' % company_path
			return render_template('error.html', msg=msg)
	else:
		msg = u'\'内部混合\'一栏不能为空！'
		return render_template('error.html', msg=msg)
	if zhongtong_path:
		if not os.path.exists(zhongtong_path):
			msg = u'外部中通文件不存在:%s' % company_path
			return render_template('error.html', msg=msg)
		compute('中通', zhongtong_path, company_path)
		count += 1
		count_str += u'中通'
	if shentong_path:
		if not os.path.exists(shentong_path):
			msg = u'外部申通文件不存在:%s' % company_path
			return render_template('error.html', msg=msg)
		compute('申通', shentong_path, company_path)
		count += 1
		count_str += u'申通'
	if youzheng_path:
		if not os.path.exists(youzheng_path):
			msg = u'外部邮政文件不存在:%s' % company_path
			return render_template('error.html', msg=msg)
		compute('邮政', youzheng_path, company_path)
		count += 1
		count_str += u'邮政'
	msg = u'核对完成! 共核对了%s%s家公司的快递账单,请到%s\\result\\目录下查看核对结果!' % (count_str, count, proj_dir)
	print msg
	return render_template('check_succ.html', msg=msg)


@app.route('/test/')
def test():
	t['info'] = 123456
	return json.dumps(t)


@app.route('/test1/')
def test1():
	t['info1'] = 456
	return json.dumps(t)


# ****************************** 数据处理部分 ********************************************

def magic(data, filename):
	arr = []
	new_data = {}
	for k, v in data.items():
		for info in v['weight_line']:
			arr.append(info[0][0])
			arr.append(info[0][1])
			arr.append(info[1])
		arr.append(v['extra_price'][0])
		arr.append(v['extra_price'][1])
		key = str(arr)
		if not new_data.has_key(key):
			new_data[key] = {}
		new_data[key][k] = v
		arr = []
	json.dump(new_data, open(filename, 'w+'))


def get_data_from_json_split(company_name):
	filename = ''
	if company_name == 'zhongtong':
		filename = '%s/res/zhongtong_price_split.json' % proj_dir
	elif company_name == 'shentong':
		filename = '%s/res/shentong_price_split.json' % proj_dir
	elif company_name == 'youzheng':
		filename = '%s/res/youzheng_price_split.json' % proj_dir
	data = json.load(open(filename, 'r+'))
	return data


def get_merge_data(company_name):
	data = get_data_from_json_split(company_name)
	new_data = []
	for k, v in data.items():
		province = v.keys()
		info = v.values()[0]
		extra_price = info['extra_price']
		weight_line = []
		for item in info['weight_line']:
			max_weight = item[0][1]
			min_weight = item[0][0]
			price = item[1]
			left = u'≤' if str(float(min_weight)).endswith('0') else u'<'
			right = u'≤' if str(float(max_weight)).endswith('0') else u'<'
			weight_line.append(u'%s%sx%s%s: %s元' % (min_weight, left, right, max_weight, price))
		new_data.append({'province': province, 'extra_price': extra_price, 'weight_line': weight_line, 'len': len(weight_line)})
	return new_data


def get_old_split_data(company_name):
	data = get_data_from_json_split(company_name)
	new_data = {}
	for infos in data.values():
		for k, v in infos.items():
			new_data[k] = v
	return new_data


def parse_csv(file_path, is_company, company_name):
	if file_path.find('/') >= 0:
		filename = file_path.split('/')[-1].encode('utf8')
	else:
		filename = file_path.split('\\')[-1]
	logger(u'加载' + filename + u'数据')
	csvfile = file(file_path, 'r+')
	reader = csv.reader(csvfile)

	all_dict = {}
	orders = []
	count = 0

	cpname_col = None
	order_col = None
	province_col = None
	weight_col = None
	if is_company:
		for column in reader:
			if not weight_col:
				cpname_col = column.index('快递公司名称')
				order_col = column.index('快递单号')
				province_col = column.index('省')
				weight_col = column.index('订单毛重')
				continue
			else:
				price = 0
				cpname = column[cpname_col]
				order = column[order_col]
				province = column[province_col]
				weight = column[weight_col]
			if all_dict.has_key(order):
				orders.append(order)
				count += 1
			else:
				all_dict.setdefault(order, {'province': province, 'price': price, 'weight': weight, 'cpname': cpname})
	else:
		for column in reader:
			order = column[0]
			province = column[1]
			weight = column[2]
			price = column[3]
			cpname = company_name
			if all_dict.has_key(order):
				orders.append(order)
				count += 1
			else:
				all_dict.setdefault(order, {'province': province, 'price': price, 'weight': weight, 'cpname': cpname})
	s = u'%s\\result\%s 重复运单号(%s).csv' % (proj_dir, filename, count)
	csvfile = file(s, 'w+')
	writer = csv.writer(csvfile)
	writer.writerow(['运单号'])
	writer.writerows([[o] for o in orders])
	csvfile.close()
	print u'%s 数据已经加载完毕,重复数：%s' % (filename, count)
	return all_dict


def shentong_price(province, weight):
	price_dict = get_old_split_data('shentong')
	try:
		prov_key = province[0: 6]
		prov_key = prov_key.decode('utf8')
		extra_price_info = price_dict[prov_key]['extra_price']
		weight_line_info = price_dict[prov_key]['weight_line']
		for i in range(0, len(weight_line_info)):
			if weight_line_info[i][0][0] <= weight <= weight_line_info[i][0][1]:
				return float('%.4f' % weight_line_info[i][1])
		extra_weight = weight - weight_line_info[-1][0][1]
		extra_weight = kg(extra_weight) if extra_price_info[1] == 'kg' else hectogram(extra_weight)
		price = weight_line_info[-1][1] + extra_weight * extra_price_info[0]
		return float('%.4f' % price)
	except Exception, e:
		exstr = traceback.format_exc()
		print exstr


def zhongtong_price(province, weight):
	price_dict = get_old_split_data('zhongtong')
	try:
		prov_key = province[0: 6]
		prov_key = prov_key.decode('utf8')
		extra_price_info = price_dict[prov_key]['extra_price']
		weight_line_info = price_dict[prov_key]['weight_line']
		for i in range(0, len(weight_line_info)):
			if weight_line_info[i][0][0] <= weight <= weight_line_info[i][0][1]:
				return float('%.4f' % weight_line_info[i][1])
		extra_weight = weight - weight_line_info[-1][0][1]
		extra_weight = kg(extra_weight) if extra_price_info[1] == 'kg' else extra_weight

		price = weight_line_info[-1][1] + extra_weight * extra_price_info[0]
		return float('%.4f' % price)
	except Exception, e:
		exstr = traceback.format_exc()
		print exstr


def youzheng_price(province, weight):
	price_dict = get_old_split_data('youzheng')
	try:
		prov_key = province[0: 6]
		prov_key = prov_key.decode('utf8')
		extra_price_info = price_dict[prov_key]['extra_price']
		weight_line_info = price_dict[prov_key]['weight_line']
		for i in range(0, len(weight_line_info)):
			if weight_line_info[i][0][0] <= weight <= weight_line_info[i][0][1]:
				return float('%.4f' % weight_line_info[i][1])
		extra_weight = weight - weight_line_info[-1][0][1]
		extra_weight = kg(extra_weight) if extra_price_info[1] == 'kg' else hectogram(extra_weight)
		price = weight_line_info[-1][1] + extra_weight * extra_price_info[0]
		return float('%.4f' % price)
	except Exception, e:
		exstr = traceback.format_exc()
		print exstr


def calculate_price(weight, province, company_name, order_code):
	if company_name == '中通':
		return zhongtong_price(province, weight)
	elif company_name == '申通':
		return shentong_price(province, weight)
	elif company_name == '邮政':
		return youzheng_price(province, weight)
	else:
		print '未识别的快递公司'
	return None


def compute(company_name, waibu_file, company_file):
	logger('计算%s数据' % company_name)
	waibu_dict = parse_csv(waibu_file, is_company=False, company_name=company_name)
	transform_file_decode(company_file)
	company_dict = parse_csv(u'%s\\tmp\\系统混合.csv' % proj_dir, is_company=True, company_name=company_name)
	data = []
	data_1 = []

	workbook = xlsxwriter.Workbook(u'%s\\result\\比对结果(%s).xlsx' % (proj_dir, company_name.decode('utf8')))
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
			if company_name == '邮政':
				waibu_weight = float(waibu_dict[item[0]]['weight']) / 1000.0
			else:
				waibu_weight = float(waibu_dict[item[0]]['weight'])
			company_weight = float(item[1]['weight'])

			waibu_price = float(waibu_dict[item[0]]['price'])
			company_price = calculate_price(company_weight, waibu_dict[item[0]]['province'], company_name, item[0])

			weight_diff = waibu_weight - company_weight
			price_diff = float('%.4f' % (waibu_price - company_price))
			sub_str = ''
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
		worksheet.write(column_num, 1, i[1][1].decode('utf8'))
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

	for item in company_dict.items():
		if item[1]['cpname'] == company_name:
			company_list.append(item[0])
	waibu_set = set(waibu_list)
	company_set = set(company_list)

	extra_wai = waibu_set - company_set
	extra_nei = company_set - waibu_set

	logger('检查不互有的运单')
	print u'外部有而公司没有的运单数: %s' % len(extra_wai)
	csvfile = file(u'%s\\result\\外部有而公司没有的运单号(%s-%s).csv' % (proj_dir, company_name.decode('utf8'), len(extra_wai)), 'wb')
	writer = csv.writer(csvfile)
	writer.writerow(['运单号'])
	writer.writerows([[o] for o in extra_wai])
	print u'公司有而外部没有的运单数: %s' % len(extra_nei)
	csvfile = file(u'%s\\result\\公司有而外部没有的运单号(%s-%s).csv' % (proj_dir, company_name.decode('utf8'), len(extra_nei)), 'wb')
	writer = csv.writer(csvfile)
	writer.writerow(['运单号'])
	writer.writerows([[o] for o in extra_nei])
	print '-' * 60
	csvfile.close()


def transform_file_decode(filename):
	try:
		fin = open(filename, 'r')
		fout = open(u'%s\\tmp\\系统混合.csv' % proj_dir, 'w')
		out_str = ''
		lines = fin.readlines()
		row_num = len(lines)
		count = 1
		for line in lines:
			if count == row_num:  # 已自动去除最后一行
				break
			out_str += line.decode('gbk').encode('utf8')
			count += 1

		fout.write(out_str)
		fin.close()
		fout.close()
	except Exception, e:
		print e


def get_width(o):
	"""Return the screen column width for unicode ordinal o."""
	widths = [
		(126, 1), (159, 0), (687, 1), (710, 0), (711, 1),
		(727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
		(4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1),
		(8426, 0), (9000, 1), (9002, 2), (11021, 1), (12350, 2),
		(12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
		(55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
		(65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
		(120831, 1), (262141, 2), (1114109, 1)
	]
	if o == 0xe or o == 0xf:
		return 0
	for num, wid in widths:
		if o <= num:
			return wid
	return 1


def logger(info):
	str_len = 0
	if type(info) != unicode:
		info = info.decode('utf8')
	for i in info:
		str_len += get_width(ord(i))
	left_len = 20
	print '%s%s%s' % (('-' * left_len), info, ('-' * (60 - left_len - str_len)))


def kg(weight):
	weight = float('%.5f' % weight)
	return int(weight) if (int(weight) == weight) else (int(weight) + 1)


def hectogram(weight):
	weight = float('%.5f' % weight)
	a = weight * 10
	return int(a) if (int(a) == a) else (int(a) + 1)


if __name__ == '__main__':
	app.run(debug=True)