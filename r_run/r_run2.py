from redis import StrictRedis

try:
    sr = StrictRedis(host='localhost', port=6379, db=0, password='sunck')
    # res = sr.set("name", "itheima")
    # print(res)
    res = sr.get("name").decode("utf8")
    print(res)
except Exception as e:
    print(e)
