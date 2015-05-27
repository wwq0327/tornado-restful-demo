# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json
from bson import json_util
from bson.objectid import ObjectId 

import pymongo

from tornado.options import define, options
define('port', default=8000, help='run on the given port', type=int)

class Application(tornado.web.Application):
    def __init__(self):
        self.handlers = handlers
        settings = dict(debug=True)

        # 链接数据库
        client = pymongo.MongoClient("mongodb://localhost:12345")
        self.db = client['codedb']

        tornado.web.Application.__init__(self, self.handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    

class APIHandler(BaseHandler):
    ## 设置默认header为json
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')


class CodesHandler(APIHandler):
    def get(self):
        codes = self.db.code.find()
        self.write(json.dumps(list(codes), default=json_util.default))

    def post(self):
        res = json.loads(self.request.body)
        self.db.code.insert(res)
        self.write(json.dumps(res, default=json_util.default))


class CodeHandler(APIHandler):
    ## 查询
    def get(self, oid):
        code = self.db.code.find_one({'_id': ObjectId(str(oid))})
        self.write(json.dumps(code, default=json_util.default))

    ## 修改记录
    def put(self, oid):
        code = self.db.code.find_one({"_id": ObjectId(str(oid))})
        new_code = json.loads(self.request.body)
        self.db.code.update(code, new_code)

    ## 删除一条记录
    def delete(self, oid):
        result = self.db.code.delete_one({'_id': ObjectId(str(oid))})

handlers = [
    (r'/api/v1/codes', CodesHandler),
    (r'/api/v1/codes/(.*)', CodeHandler)
]

if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()