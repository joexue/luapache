# luapache
A tiny webserver written by lua script

  Luapache is a tiny web server written by lua script, which supports CGI and
  GET operation. luapache has no the network function, you have to use it with
  netcat or openssl to get a http or https web server.

  Usage:
  If your netcat has -e argument, just run it as

      "nc -k -l port -w 1 -e luapache.lua"

  otherwise, you need to create a fifo to let Luapache talks with it bidirectly.

       "mkfifo /tmp/luapache"
       "cat /tmp/luapache | luapache.lua | nc -k -l port -w 1 > /tmp/luapache"

  You can use the same way to run https with openssl utils.

  Luapache has two arguments, root_path and default_page, if they are not
  provided then the default value "./" and index.html/index.cgi/index.lua will
  be used.

  POST is not supported for now, but I believe it is easy to implement.
