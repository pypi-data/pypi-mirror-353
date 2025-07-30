#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/19 18:58
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import yaml

from dg_itest.servers.file_handler.file_handler import FileHandler


class YamlHandler(FileHandler):
	def load(self):
		with open(self.file_path, 'r', encoding='utf-8') as f:
			raw = yaml.safe_load(f.read())
		return raw