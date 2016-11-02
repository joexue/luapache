#!/bin/env lua

--[[
  luapache.lua
  * Copyright (c) 2016 Joe Xue lgxue@hotmail.com

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
--]]

local ERR = "HTTP/1.1 404 Not Found\n\rContent-Type: text/html\n\r\n\r404 Not Found\n\rNot Found The requested resource was not found"
local HEAD = "HTTP/1.1 200 OK\n\rContent-Type: Text/html\n\r\n\r"

local default_page = {"index.html", "index.cgi", "index.lua"}

local base = "./"

local function usage()
    print(arg[0] .. ": root_path default_page")
end

local function debug(str)
    os.execute("echo \"" .. str .. "\" >> /tmp/debug.txt")
end

local function run_cgi(file, params)
    local cgi = io.popen("QUERY_STRING=\"" .. params .. "\" " .. file)
    local context = cgi:read("*a")
    return context
end

local function run_html(file)
    return io.open(file):read("*a")
end

local function parse_request()
    local request = io.read()

    while true  do
        local header = io.read()
        if header == "\r" then
            break
        end
    end

    local get = string.match(request, "GET (.+) HTTP.+")
    local file = nil

    local params = string.match(get, "%?(.*)")

    if get == "/" then
        -- Pick the default page
        for i = 1, #default_page do
            if io.open(base .. default_page[i]) then
                file = base .. default_page[i]
                break
            end
        end
    else
        local filename
        if params then
            filename = string.match(get, "(.*)?")
        else
            filename = get
        end
        if io.open(base .. filename) then
            file = base .. filename
        end
    end

    if not params then
        params = ""
    end

    return file, params
end

local function run()
    local file, params = parse_request()

    if file then
        io.write(HEAD)
        -- Try CGI firstly
        local context = run_cgi(file, params)
        if context == "" then
            -- It's not a CGI program
            io.write(run_html(file))
        else
            io.write(context)
        end
    else
        io.write(ERR)
    end

    io.flush()
end

-- Start the server
if #arg > 0 then
    if arg[1] == "-h" then
        usage()
        return
    elseif arg[2] then
        default_page = {}
        table.insert(default_page, arg[2])
    end
    base = arg[1] .. "/"
end

while true do
    run()
end
