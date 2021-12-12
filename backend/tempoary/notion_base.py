# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: Notion Base Abilities
# date: 2021/12/11

import json
import requests


class HANotionBase:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.notion_setting = json.load(open("./notion_setting.json", "r", encoding="utf-8"))

        self.integration_token = self.notion_setting["integrationToken"]
        self.headers = {
            "Authorization": "Bearer %s" % self.integration_token,
            "Content-Type": "application/json",
            "Notion-Version": self.notion_setting["latestApiVersion"]
        }
        self.base_url = "https://api.notion.com"

    '''Common operations'''
    def request(self, request_type, url, body=None, headers=None):

        """
        发送请求
        :return:
        """
        if headers is None:
            headers = self.headers

        self.log.add_log("HANotionBase: start send http request-%s" % request_type, 1)
        if request_type == "POST":
            r = requests.post(url, data=json.dumps(body), headers=headers)
        elif request_type == "GET":
            r = requests.get(url, headers=headers)
        elif request_type == "patch":
            r = requests.patch(url, data=body)
        else:
            return False

        code = r.status_code
        res = r.json()
        if code == 200:
            self.log.add_log("HANotionBase: http request success", 1)
        elif code == 400:
            self.log.add_log("HANotionBase: http request meet an error, res-%s" % res, 3)

        return code, res

    def create_filter_object(self, filter_type, property_name, property_type, property_condition, property_value):

        """
        创建一个过滤器
        :param filter_type: 过滤器类型 compound/normal
        :param property_name: 性质名称
        :param property_type: 性质值类型
        :param property_condition: 性质条件
        :param property_value: 性质值
        :return: dict
        """
        self.log.add_log("HANotionBase: create an %s filter" % filter_type, 1)
        if filter_type == "normal":
            result = {
                "property": property_name,
                property_type: {
                    property_condition: property_value
                }
            }
        elif filter_type == "compound":
            if (property_name == "or" or property_name == "and") and (type(property_value) == dict):
                result = {
                    property_name: property_value
                }
            else:
                self.log.add_log("HANotionBase: wrong value of param-property_name or param-property_value", 1)
                result = None
        else:
            self.log.add_log("HANotionBase: unknown filter_type-%s" % filter_type)
            result = None
        return result

    def create_sort_object(self):

        """
        创建排序器
        :return:
        """

    def create_rich_text_object(self):

        """
        创建一个富文本对象 list
        :return: list
        """

    def create_property_schema_object(self, names, operations, values, options=None):

        """
        创建property schema object
        :param operations: 操作 remove/rename/type/value
        :param names: id/name
        :param values:
        :param options: multi-select select options
        :type operations list
        :type names list
        :type values list
        type
          "title", "rich_text", "number", "select", "multi_select", "date", "people",
          "files", "checkbox", "url", "email", "phone_number", "formula", "relation", "rollup",
          "created_time", "created_by", "last_edited_time", "last_edited_by"
        :return:
        """
        self.log.add_log("HANotionBase: create an property schema object", 1)
        if options is None:
            options = {}

        result = {}
        for i in range(0, len(operations)):
            operation = operations[i]
            name = names[i]
            if operation == "remove":
                result[name] = None
            elif operation == "rename":
                result[name] = {"name": values[i]}
            elif operation == "type":
                result[name] = {values[i]: options}
            elif operation == "value":
                result[name] = values[i]

    def create_property_value_object(self, names, types, ):

    '''Database operations'''
    def analyze_database_object(self, database_object):

        """
        分析database object
        :param database_object: database数据
        :return: dict
        """

    def query_database(self, database_id, id_type="name", filter_object=None, sorts_object=None, start_cursor=None, page_size=None):

        """
        获取数据库中的Pages
        :param database_id:
        :param id_type: name/id
        :param filter_object: 过滤器
        :param sorts_object: 排序器
        :param start_cursor: page读取起始index
        :param page_size: 返回的page数 max:100
        :type page_size int
        :type start_cursor str
        :type filter_object: dict
        :type sorts_object: list
        :return: bool, dict
        """
        self.log.add_log("HANotionBase: query for database-%s" % database_id)

        if id_type == "name":
            database_id = self.notion_setting["boardIdList"][database_id]
        url = "https://api.notion.com/v1/databases/%s/query" % database_id

        body = {}
        if filter_object is not None:
            body["filter"] = filter_object
        if sorts_object is not None:
            body["sorts"] = sorts_object
        if start_cursor is not None:
            body["start_cursor"] = start_cursor
        if page_size is not None:
            body["page_size"] = page_size

        code, res = self.request("POST", url, body)

        if code == 200:
            self.log.add_log("HANotionBase: query_database-%s success" % database_id, 1)
            return res
        elif code == 404:
            self.log.add_log("HANotionBase: database-%s does not exist" % database_id, 3)
            return res
        else:
            self.log.add_log("HANotionBase: query_database failed, code-%s" % code, 3)
            return False

    def update_database(self, database_id, id_type, title, properties):

        """
        修改数据库数据
        :param database_id: 数据库id
        :param id_type: name/id
        :param title:
        :param properties:
        :return:
        """
        self.log.add_log("HANotionBase: update database-%s's info" % database_id)
        if id_type == "name":
            database_id = self.notion_setting["boardIdList"][database_id]

        url = "https://api.notion.com/v1/databases/%s" % database_id

        body = {}
        if title is not None:
            body["title"] = title
        if properties is not None:
            body["properties"] = properties

        code, res = self.request("PATCH", url, body)

        if code == 200:
            self.log.add_log("HANotionBase: update_database-%s success" % database_id, 1)
            return res
        elif code == 404:
            self.log.add_log("HANotionBase: database-%s does not exist" % database_id, 3)
            return res
        else:
            self.log.add_log("HANotionBase: update_database failed, code-%s" % code, 3)
            return False

    '''Page operations'''
    def analyze_page_object(self, page_object):

        """
        分析page object
        :param page_object: page数据
        :return: dict
        """

    def query_page(self, page_id):

        """
        获取page
        :param page_id:
        :return:
        """
        self.log.add_log("HANotionBase: query page-%s's info" % page_id)

        url = "https://api.notion.com/v1/pages/%s" % page_id

        code, res = self.request("GET", url)

        if code == 200:
            self.log.add_log("HANotionBase: query_page success", 1)
            return res
        elif code == 404:
            self.log.add_log("HANotionBase: page does not exist", 3)
            return res
        else:
            self.log.add_log("HANotionBase: query page failed, code-%s" % code, 3)
            return False

    def create_page(self, parent, properties, children=None, icon=None, cover=None):

        """
        创建一个页面
        :param parent: 父级对象
        :param properties: 页面性质 dict
        :param children: 子对象 list
        :param icon:
        :param cover:
        :type properties dict
        :type children list
        :return:
        """
        self.log.add_log("HANotionBase: create a page")
        url = "https://api.notion.com/v1/pages/"

        body = {
            "parent": parent,
            "properties": properties
        }
        if children
        code, res = self.request("POST", url, body)

        if code == 200:
            self.log.add_log("HANotionBase: query_page success", 1)
            return res
        elif code == 404:
            self.log.add_log("HANotionBase: page does not exist", 3)
            return res
        else:
            self.log.add_log("HANotionBase: query page failed, code-%s" % code, 3)
            return False

    '''Block operations'''

    '''Search'''
