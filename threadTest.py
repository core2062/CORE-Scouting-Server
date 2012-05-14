from threading import Timer


def hello():
    print "hello, world"
    t = Timer(100, hello)
    t.start()

hello()
