#!/bin/env lua

--[[
    A lua CGI program to record score of PingPong games.

    Oct 21, 2016    Created by Joe Xue
--]]


local PEOPLE = {
    {"Zhang", "zhang@co.com"},
    {"Liao", "lia@co.com"},
    {"Jin", "jin@co.com"},
    {"Xue", "xue@co.com"},
    {"Chang", "chang@co.com"}
}

local RECORD = "score.lua"

local HEAD=[[
<!DOCTYPE html>
<html>
    <head>
        <title>Ping Pong Score Board</title>
    </head>
    <body>

        <h1>Ping Pong Score Board</h1>
]]

local TABLE_HEAD=[[
        <table style="width:100%" align="right" border=1>
]]

-- Dynamic name row, score rows, new score record  and total row here.

local TABLE_FOOT=[[
        </table>
]]

-- Add and delete buttons, not shown always
local BUTTONS=[[
        &nbsp;<br>
        <table style="width:50%" align="left" >
            <tr>
                <td>
                    <form method="get" action="index.cgi">
                        <input type="hidden" name="action" value="new"/>
                        <button type="submit" style="background-color:LightGreen"> Add a new record</button>
                    </form>
                </td>
                <td>
                    <form method="get" action="index.cgi">
                        <input type="hidden" name="action" value="delete"/>
                        <button type="submit" style="background-color:LightCoral"> Delete last record</button>
                    </form>
                </td>
            </tr>
        </table>
]]

-- Rest of html page
local FOOT=[[
        <p>
            &nbsp;<br> &nbsp;<br>
            Rules:<br>
            (1) Team A win Team B by 2:0 Team A gets 2 points, Team B gets 0 point.<br>
            (2) Team A win Team B by 2:1 Team A gets 2 points, Team B gets 1 point.<br>
            (3) Any game team B get the score under 10 will plus 1 point to Team A <br>
        </p>

    </body>
</html>
]]

-- Simple debug function
function debug(str)
    os.execute("echo \"" .. str .. "\" >> /tmp/debug.txt")
end

function name_row()
    local th = {}
    table.insert(th, "<tr>")
    table.insert(th, "<th>Data/Name</th>")
    for i = 1, #PEOPLE do
        table.insert(th, "<th>" .. PEOPLE[i][1] .. "</th>")
    end
    table.insert(th, "</tr>")
    return table.concat(th, "\n")
end

function newrecord_row()
    local newrecord = {}
    local date = os.date("%b %d, %Y", os.time())
    table.insert(newrecord,
    [[<form method="get" action="index.cgi">
    <input type="hidden" name="action" value="add"/>
    <tr>
        <td align="center">
    ]]
    .. date ..
    [[      <button type="submit" style="background-color:LightGreen">Save</button>
        </td>
    ]])

    for i = 1, #PEOPLE do
        table.insert(newrecord, "<td align=\"center\"><input type=\"text\" name=\"ps" .. i .. "\" </td>")
    end

    table.insert(newrecord, "</tr>")
    table.insert(newrecord, "</form>")
    return table.concat(newrecord, "\n")
end

function total_row()
    local total = {}
    local ts = {}

    for i = 1, #PEOPLE do
        ts[i] = {0, 0}
    end

    table.insert(total, "<tr>")
    table.insert(total, "<th>Total/Attendace=Average</th>")

    for i = 1, #ss do
        for j = 1, #PEOPLE do
            if ss[i][j + 1] >= 0 then
                ts[j][1] = ts[j][1] + ss[i][j + 1]
                ts[j][2] = ts[j][2] + 1
            end
        end
    end

    for n = 1, #ts do
        table.insert(total, "<th>" .. ts[n][1] .. "/" .. ts[n][2] .. "=" .. string.format("%.2f", ts[n][1]/ts[n][2]) .. "</th>")
    end

    table.insert(total, "</tr>")

    return table.concat(total, "\n")
end

function score_rows()
    local score={}
    for i = 1, #ss do
        table.insert(score, "<tr>")
        for j = 1, #ss[i] do
            if j == 1 then
                table.insert(score, "<td align=\"center\">" .. os.date("%b %d, %Y", ss[i][j]) .. "</td>")
            else
                if ss[i][j] < 0 then
                    table.insert(score, "<td align=\"center\" style=\"color:red\">Absent</td>")
                else
                    table.insert(score, "<td align=\"center\">" .. ss[i][j] .. "</td>")
                end
            end
        end
        table.insert(score, "</tr>")
    end

    return table.concat(score, "\n")
end

function save_record()
    local f = assert(io.open(RECORD, "w"))

    f:write("ss={")
    for i = 1, #ss do
        f:write("\n{")
        --We have the date in record so, the total item number is #PEOPLE + 1
        for j = 1, #PEOPLE + 1 do
            f:write(ss[i][j])
            if j ~= (#PEOPLE + 1) then
                f:write(", ")
            end
        end

        if (i == #ss) then
            f:write("}\n")
        else
            f:write("},")
        end
    end
    f:write("}\n")
    f:close()
end

function send_mail(str)
    local command
    local tos = {}
    for i = 1, #PEOPLE do
        table.insert(tos, PEOPLE[i][2])
    end
    command = [[ echo "Someone ]] .. str .. [[ one record, please check http://joxue:8000" | mail -s "Ping Pong Scoreboard Changed" -r pingpong@co.com ]] .. table.concat(tos, " ")
    --os.execute(command)
end

function add_record(param)
    ps = {}
    --Some text area may be empty, so we firstly add the & to the tail then 
    --replace "=&" to "=0&" to give the empty area as 0
    local record = string.gsub(param .. "&", "=&", "=-1&");
    record = string.gsub(record, "&", " ");
    --Replace the "ps/number/" as "ps[number]"
    record = string.gsub(record, "ps(%d+)", "ps[%1]");
    loadstring(record)()

    for i = 1, #PEOPLE do
        if not tonumber(ps[i]) then
            return
        end
    end

    table.insert(ps, 1, os.time())
    table.insert(ss, ps)

    save_record()

    send_mail("added")
end

function delete_record()
    if #ss == 0 then
        return
    end

    table.remove(ss)

    save_record()
    send_mail("deleted")
end

--Start to run
dofile(RECORD)

local param = os.getenv("QUERY_STRING")
if not param then
    param=""
end
debug("xxxxxxx param = ".. param)
if string.match(param, "action=add") then
    add_record(param)
elseif string.match(param, "action=delete") then
    delete_record()
end

print(HEAD)

print(TABLE_HEAD)

print(name_row())

print(score_rows())

if (param == "action=new") then
    print(newrecord_row())
end

print(total_row())

print(TABLE_FOOT)

if (param ~= "action=new") then
    print(BUTTONS)
end

print(FOOT)
