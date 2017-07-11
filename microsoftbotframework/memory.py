import os
import json
import redis


class Memory(object):
    def __init__(self):
        pass

    def get(self, key):
        raise(Exception('Memory objects must have a get method'))

    def set(self, key, value):
        raise (Exception('Memory objects must have a set method'))

    def delete(self, key):
        raise (Exception('Memory objects must have a delete method'))


class JsonMemory(Memory):
    def __init__(self, filename='memory.json', root_directory=None):
        Memory.__init__(self)

        if root_directory is not None:
            self.data_location = '{}/{}'.format(root_directory, filename)
        else:
            self.data_location = '{}/{}'.format(os.getcwd(), filename)

        # if the file doesn't exist create a empty file with a json object
        if not os.path.isfile(self.data_location):
            with open(self.data_location, 'w+') as data_file:
                data_file.write('{}')

    def get(self, key):
        with open(self.data_location) as data_file:
            data = json.load(data_file)
            if key in data:
                value = data[key]
            else:
                value = None

        return value

    def set(self, key, value):
        with open(self.data_location, 'r+') as data_file:
            data = json.load(data_file)

            data[key] = value

            data_file.seek(0)
            data_file.write(json.dumps(data))
            data_file.truncate()

        return True

    def delete(self, key):
        with open(self.data_location, 'r+') as data_file:
            data = json.load(data_file)

            data.pop(key, None)

            data_file.seek(0)
            data_file.write(json.dumps(data))
            data_file.truncate()

        return True


class RedisMemory(Memory):
    # currently loading is only from config file
    def __init__(self, config):
        Memory.__init__(self)

        self.redis_uri = config.get_config(None, 'URI', root='redis')
        self.redis = None
        self.redis_config = config.get_section_config('redis')

    def get(self, key):
        self._connect()
        value = self.redis.get(key)
        if value is not None:
            value = value.decode('UTF-8')
        return value

    def set(self, key, value):
        self._connect()
        self.redis.set(key, value)

    def delete(self, key):
        self._connect()
        self.redis.delete(key)

    def _connect(self):
        if self.redis is None:
            self.redis = redis.StrictRedis.from_url(self.redis_uri)
            for name, value in self.redis_config.items():
                try:
                    self.redis.config_set(name, value)
                except:
                    pass
                    # log...

