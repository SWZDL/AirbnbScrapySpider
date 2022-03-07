#!usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:Joshua
@description:
  只是继承一下scrapy.Request，然后pass，好区分哪些Request需要启用selenium进行解析页面，相当于改个名
"""
import scrapy


class SeleniumRequest(scrapy.Request):
    """
    selenium专用Request类
    """
    pass
