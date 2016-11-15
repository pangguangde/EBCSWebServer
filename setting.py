# coding=utf-8

import platform

import sys

cur_platform = platform.system()

PROJECT_DIR = sys.path[0]
RES_DIR = '%s/res/' % PROJECT_DIR
RESULT_DIR = '%s/result/' % PROJECT_DIR
TMP_DIR = '%s/tmp/' % PROJECT_DIR
UPLOAD_DIR = '%s/upload/' % RES_DIR
if cur_platform == 'Windows':
	PROJECT_DIR = PROJECT_DIR.replace('/', '\\')
	RES_DIR = RES_DIR.replace('/', '\\')
	RESULT_DIR = RESULT_DIR.replace('/', '\\')
	TMP_DIR = TMP_DIR.replace('/', '\\')
	UPLOAD_DIR = UPLOAD_DIR.replace('/', '\\')