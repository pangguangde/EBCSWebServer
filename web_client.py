# coding=utf-8

import json
import os
import time

from flask import Flask, render_template
from flask import request
from wtforms import *

from Checker.Checker import Checker
from DataParser.CompanyDataParser import CompanyDataParser
from DataParser.ShentongDataParser import ShentongDataParser
from DataParser.YouzhengDataParser import YouzhengDataParser
from DataParser.ZhongtongDataParser import ZhongtongDataParser
from setting import *

app = Flask(__name__)

parse_company_dict = {}
parse_company_repeat_orders = []


class FilePathForm(Form):
	zhongtong_file = FileField('zhongtong_file')
	shentong_file = FileField('shentong_file')
	youzheng_file = FileField('youzheng_file')
	company_file = FileField('company_file')
	company_file1 = FileField('company_file1')
	company_file2 = FileField('company_file2')
	company_file3 = FileField('company_file3')


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


class UploadForm(Form):
	upload_file = FileField('test')


@app.route('/index/')
def index():
	form = FilePathForm()
	price_change_form = PriceChangeForm()
	zhongtong_price_info = get_merge_data('zhongtong')
	youzheng_price_info = get_merge_data('youzheng')
	shentong_price_info = get_merge_data('shentong')

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
	data = json.load(open('%s/res/%s_price_split.json' % (PROJECT_DIR, company_pinyin), 'r+'))
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
	json.dump(data, open('%s/res/%s_price_split.json' % (PROJECT_DIR, company_pinyin), 'w+'))
	msg = u'%s[%s]的计价规则已更新' % (companies[int(request.form['company'])].keys()[0], u' '.join(province))
	print msg
	return render_template('check_succ.html', msg=msg)


@app.route('/check/', methods=['POST', 'GET'])
def check():
	zhongtong_file = request.files['zhongtong_file']
	shentong_file = request.files['shentong_file']
	youzheng_file = request.files['youzheng_file']
	company_file = request.files['company_file']
	company_file1 = request.files['company_file1']
	company_file2 = request.files['company_file2']
	company_file3 = request.files['company_file3']
	count = 0
	count_str = u''
	company_path = u''

	ts1 = int(time.time())
	if company_file.filename:
		company_file.save('%scompany.csv' % UPLOAD_DIR)
		company_path += u'%scompany.csv' % UPLOAD_DIR.decode('utf8')
	else:
		msg = u'\'内部混合\'一栏不能为空！'
		return render_template('error.html', msg=msg)
	if not(zhongtong_file.filename or shentong_file.filename or youzheng_file.filename):
		msg = u'\'外部中通\'、\'外部申通\'、\'外部邮政\'不能全都留空哦(至少选一个)'
		return render_template('error.html', msg=msg)
	if company_file1.filename:
		company_file1.save('%scompany1.csv' % UPLOAD_DIR)
		company_path += u'+%scompany1.csv' % UPLOAD_DIR.decode('utf8')
		if company_file2.filename:
			company_file2.save('%scompany2.csv' % UPLOAD_DIR)
			company_path += u'+%scompany2.csv' % UPLOAD_DIR.decode('utf8')
			if company_file3.filename:
				company_file3.save('%scompany3.csv' % UPLOAD_DIR)
				company_path += u'+%scompany3.csv' % UPLOAD_DIR.decode('utf8')
	company_parser = CompanyDataParser(company_path)
	if zhongtong_file.filename:
		zhongtong_file.save('%szhongtong.xls' % UPLOAD_DIR)
		zhongtong_parser = ZhongtongDataParser(u'%szhongtong.xls' % UPLOAD_DIR.decode('utf8'))
		Checker(company_parser, zhongtong_parser).check()
		count += 1
		count_str += u'中通'
	if shentong_file.filename:
		shentong_file.save('%sshentong.xls' % UPLOAD_DIR)
		shentong_parser = ShentongDataParser(u'%sshentong.xls' % UPLOAD_DIR.decode('utf8'))
		Checker(company_parser, shentong_parser).check()
		count += 1
		count_str += u'申通'
	if youzheng_file.filename:
		youzheng_file.save('%syouzheng.xls' % UPLOAD_DIR)
		youzheng_parser = YouzhengDataParser(u'%syouzheng.xls' % UPLOAD_DIR.decode('utf8'))
		Checker(company_parser, youzheng_parser).check()
		count += 1
		count_str += u'邮政'
	ts2 = int(time.time())
	t1 = ts2 - ts1
	msg = u'核对完成,耗时%s秒! 共核对了%s%s家公司的快递账单,请到%s目录下查看核对结果!' % (t1, count_str, count, RESULT_DIR)
	print msg
	return render_template('check_succ.html', msg=msg)


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		f = request.files['upload_file']
		f.save('%stest.csv' % UPLOAD_DIR)
	form = UploadForm()
	return render_template('upload.html', form=form)


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


def get_merge_data(company_pinyin):
	data = json.load(open('%s%s_price_split.json' % (RES_DIR, company_pinyin), 'r+'))
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


def transform_file_decode(filename):
	try:
		fin = open(filename, 'r')
		fout = open(u'%s系统混合.csv' % TMP_DIR, 'w')
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

if __name__ == '__main__':
	app.run(debug=True)