# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource
import docker
import platform

import json

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '哈哈哈'},
    'todo3': {'task': 'profit!'},
}

LIVING_CONTAINER = {
    'c1': {'container_id': 'b0ca7e6131c3', 'name': 'redis'}
}

RESURN_OPT_STATUS = {
    'CLEAN_SUCCESS': {'message': 'clean success', 'opt': 'clean'},
    'CLEAN_FAIL': {'message': 'clean fail', 'opt': 'clean'}
}

@app.route('/')
def hello_world():
    return 'Hello World!'


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


class TodoList(Resource):
    """
    TodoList
    shows a list of all todos, and lets you POST to add new tasks
    """
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


class CustomContainer(object):
    """
    CONTAINER ID ,IMAGE  ,COMMAND ,CREATED,STATUS,PORTS ,NAMES
    """
    def __init__(self, container_id, image, command, created, status, ports, names):
        """
        :param container_id:
        :param image:
        :param command:
        :param created:
        :param status:
        :param ports:
        :param names:
        """
        self.container_id = container_id
        self.image = image
        self.command = command
        self.created = created
        self.status = status
        self.ports = ports
        self.names = names

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True)


def _get_living_container():
    LIVING_CONTAINER.clear()
    client = _get_client()
    container_list = client.containers.list(all=True)
    for i, container in enumerate(container_list, 1):
        t_dict = dict()
        t_dict['container_id'] = container.short_id
        t_dict['image'] = str(container.image)
        t_dict['name'] = container.name
        t_dict['status'] = container.status
        index = 'c%d' % (i, )
        LIVING_CONTAINER[index] = t_dict

    client.close()


def _get_client():
    sys_str = platform.system()
    if sys_str == "Windows":
        client = docker.from_env()
    else:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    return client


def abort_if_index_doesnt_exist(index):
    if index not in LIVING_CONTAINER:
        abort(404, message="LIVING_CONTAINER {} doesn't exist".format(index))


class DockerMonitor(Resource):
    """
    monitor the docker process
    """
    def get(self):
        _get_living_container()
        return LIVING_CONTAINER


class DockerStop(Resource):
    """

    """
    def get(self, index):
        print '---->' + index
        return LIVING_CONTAINER[index]


class DockerClean(Resource):
    """
    清理已经停止运行的容器
    """
    def get(self, index):
        abort_if_index_doesnt_exist(index)
        client = _get_client()
        container = LIVING_CONTAINER.get(index)
        container_object = client.containers.get(container.get("container_id"))
        container_object.remove()
        del LIVING_CONTAINER[index]
        client.close()
        return RESURN_OPT_STATUS['CLEAN_SUCCESS']


class DockerRestart(Resource):
    """
    重启容器
    """
    def get(self, index):
        return LIVING_CONTAINER[index]


# Actually setup the Api resource routing here
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')
api.add_resource(DockerMonitor, '/docker')
api.add_resource(DockerStop, '/docker/stop/<index>')  # 停止正在运行中容器
api.add_resource(DockerClean, '/docker/clean/<index>')  # 清理已经停止运行的容器
api.add_resource(DockerRestart, '/docker/restart/<index>')  # 重启容器

if __name__ == '__main__':
    app.run()
