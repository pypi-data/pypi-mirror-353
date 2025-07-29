import time
import re
from binascii import b2a_hex, a2b_hex
import requests
import execjs
import ddddocr
from enum import Enum
from typing import Annotated
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    Tool,
    TextContent,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field


class DpipblockTools(str, Enum):
    PORT_ADD = "port_add"
    PORT_DELETE = "port_delete"


def convert_time_to_seconds(time_str: str) -> str:
    """
    将时间字符串转换为秒数
    支持的格式：
    - "永久" 或 "permanent" -> "-1"
    - "1分钟", "1min", "1m" -> "60"
    - "1小时", "1hour", "1h" -> "3600"
    - "1天", "1day", "1d" -> "86400"
    - "1周", "1week", "1w" -> "604800"
    - "1月", "1month" -> "2592000" (30天)
    - "1年", "1year", "1y" -> "31536000"
    - 纯数字 -> 直接返回（假设为秒）
    """
    time_str = time_str.strip().lower()
    
    # 永久封禁
    if time_str in ["永久", "permanent", "forever", "-1"]:
        return "-1"
    
    # 纯数字，直接返回
    if time_str.isdigit():
        return time_str
    
    # 提取数字和单位
    match = re.match(r'(\d+)\s*([a-zA-Z\u4e00-\u9fff]+)', time_str)
    if not match:
        # 如果无法解析，默认返回180秒
        return "180"
    
    number = int(match.group(1))
    unit = match.group(2)
    
    # 时间单位转换表
    time_units = {
        # 分钟
        '分钟': 60, 'min': 60, 'm': 60, 'minute': 60, 'minutes': 60,
        # 小时
        '小时': 3600, 'hour': 3600, 'hours': 3600, 'h': 3600,
        # 天
        '天': 86400, 'day': 86400, 'days': 86400, 'd': 86400,
        # 周
        '周': 604800, 'week': 604800, 'weeks': 604800, 'w': 604800,
        # 月
        '月': 2592000, 'month': 2592000, 'months': 2592000,
        # 年
        '年': 31536000, 'year': 31536000, 'years': 31536000, 'y': 31536000,
        # 秒
        '秒': 1, 'second': 1, 'seconds': 1, 's': 1, 'sec': 1,
    }
    
    multiplier = time_units.get(unit, 1)
    return str(number * multiplier)


def dpfhq_login(username: str, password: str) -> dict:
    # with open("7_dpfhq.js", "r", encoding="UTF-8") as file:
    #     js_code = file.read()
    js_code = """
var hexcase = 0;
function hex_md5(c) {
    return rstr2hex(rstr_md5(str2rstr_utf8(c)))
}
function rstr_md5(c) {
    return binl2rstr(binl_md5(rstr2binl(c), c.length * 8))
}
function rstr2hex(c) {
    isNaN(hexcase) && (hexcase = 0);
    for (var g = hexcase ? "0123456789ABCDEF" : "0123456789abcdef", a = "", b, d = 0; d < c.length; d++)
        b = c.charCodeAt(d),
        a += g.charAt(b >>> 4 & 15) + g.charAt(b & 15);
    return a
}

function str2rstr_utf8(c) {
    for (var g = "", a = -1, b, d; ++a < c.length; )
        b = c.charCodeAt(a),
        d = a + 1 < c.length ? c.charCodeAt(a + 1) : 0,
        55296 <= b && b <= 56319 && 56320 <= d && d <= 57343 && (b = 65536 + ((b & 1023) << 10) + (d & 1023),
        a++),
        b <= 127 ? g += String.fromCharCode(b) : b <= 2047 ? g += String.fromCharCode(192 | b >>> 6 & 31, 128 | b & 63) : b <= 65535 ? g += String.fromCharCode(224 | b >>> 12 & 15, 128 | b >>> 6 & 63, 128 | b & 63) : b <= 2097151 && (g += String.fromCharCode(240 | b >>> 18 & 7, 128 | b >>> 12 & 63, 128 | b >>> 6 & 63, 128 | b & 63));
    return g
}

function rstr2binl(c) {
    for (var g = Array(c.length >> 2), a = 0; a < g.length; a++)
        g[a] = 0;
    for (a = 0; a < c.length * 8; a += 8)
        g[a >> 5] |= (c.charCodeAt(a / 8) & 255) << a % 32;
    return g
}
function binl2rstr(c) {
    for (var g = "", a = 0; a < c.length * 32; a += 8)
        g += String.fromCharCode(c[a >> 5] >>> a % 32 & 255);
    return g
}
function binl_md5(c, g) {
    c[g >> 5] |= 128 << g % 32;
    c[(g + 64 >>> 9 << 4) + 14] = g;
    for (var a = 1732584193, b = -271733879, d = -1732584194, e = 271733878, f = 0; f < c.length; f += 16)
        var h = a
          , i = b
          , k = d
          , j = e
          , a = md5_ff(a, b, d, e, c[f + 0], 7, -680876936)
          , e = md5_ff(e, a, b, d, c[f + 1], 12, -389564586)
          , d = md5_ff(d, e, a, b, c[f + 2], 17, 606105819)
          , b = md5_ff(b, d, e, a, c[f + 3], 22, -1044525330)
          , a = md5_ff(a, b, d, e, c[f + 4], 7, -176418897)
          , e = md5_ff(e, a, b, d, c[f + 5], 12, 1200080426)
          , d = md5_ff(d, e, a, b, c[f + 6], 17, -1473231341)
          , b = md5_ff(b, d, e, a, c[f + 7], 22, -45705983)
          , a = md5_ff(a, b, d, e, c[f + 8], 7, 1770035416)
          , e = md5_ff(e, a, b, d, c[f + 9], 12, -1958414417)
          , d = md5_ff(d, e, a, b, c[f + 10], 17, -42063)
          , b = md5_ff(b, d, e, a, c[f + 11], 22, -1990404162)
          , a = md5_ff(a, b, d, e, c[f + 12], 7, 1804603682)
          , e = md5_ff(e, a, b, d, c[f + 13], 12, -40341101)
          , d = md5_ff(d, e, a, b, c[f + 14], 17, -1502002290)
          , b = md5_ff(b, d, e, a, c[f + 15], 22, 1236535329)
          , a = md5_gg(a, b, d, e, c[f + 1], 5, -165796510)
          , e = md5_gg(e, a, b, d, c[f + 6], 9, -1069501632)
          , d = md5_gg(d, e, a, b, c[f + 11], 14, 643717713)
          , b = md5_gg(b, d, e, a, c[f + 0], 20, -373897302)
          , a = md5_gg(a, b, d, e, c[f + 5], 5, -701558691)
          , e = md5_gg(e, a, b, d, c[f + 10], 9, 38016083)
          , d = md5_gg(d, e, a, b, c[f + 15], 14, -660478335)
          , b = md5_gg(b, d, e, a, c[f + 4], 20, -405537848)
          , a = md5_gg(a, b, d, e, c[f + 9], 5, 568446438)
          , e = md5_gg(e, a, b, d, c[f + 14], 9, -1019803690)
          , d = md5_gg(d, e, a, b, c[f + 3], 14, -187363961)
          , b = md5_gg(b, d, e, a, c[f + 8], 20, 1163531501)
          , a = md5_gg(a, b, d, e, c[f + 13], 5, -1444681467)
          , e = md5_gg(e, a, b, d, c[f + 2], 9, -51403784)
          , d = md5_gg(d, e, a, b, c[f + 7], 14, 1735328473)
          , b = md5_gg(b, d, e, a, c[f + 12], 20, -1926607734)
          , a = md5_hh(a, b, d, e, c[f + 5], 4, -378558)
          , e = md5_hh(e, a, b, d, c[f + 8], 11, -2022574463)
          , d = md5_hh(d, e, a, b, c[f + 11], 16, 1839030562)
          , b = md5_hh(b, d, e, a, c[f + 14], 23, -35309556)
          , a = md5_hh(a, b, d, e, c[f + 1], 4, -1530992060)
          , e = md5_hh(e, a, b, d, c[f + 4], 11, 1272893353)
          , d = md5_hh(d, e, a, b, c[f + 7], 16, -155497632)
          , b = md5_hh(b, d, e, a, c[f + 10], 23, -1094730640)
          , a = md5_hh(a, b, d, e, c[f + 13], 4, 681279174)
          , e = md5_hh(e, a, b, d, c[f + 0], 11, -358537222)
          , d = md5_hh(d, e, a, b, c[f + 3], 16, -722521979)
          , b = md5_hh(b, d, e, a, c[f + 6], 23, 76029189)
          , a = md5_hh(a, b, d, e, c[f + 9], 4, -640364487)
          , e = md5_hh(e, a, b, d, c[f + 12], 11, -421815835)
          , d = md5_hh(d, e, a, b, c[f + 15], 16, 530742520)
          , b = md5_hh(b, d, e, a, c[f + 2], 23, -995338651)
          , a = md5_ii(a, b, d, e, c[f + 0], 6, -198630844)
          , e = md5_ii(e, a, b, d, c[f + 7], 10, 1126891415)
          , d = md5_ii(d, e, a, b, c[f + 14], 15, -1416354905)
          , b = md5_ii(b, d, e, a, c[f + 5], 21, -57434055)
          , a = md5_ii(a, b, d, e, c[f + 12], 6, 1700485571)
          , e = md5_ii(e, a, b, d, c[f + 3], 10, -1894986606)
          , d = md5_ii(d, e, a, b, c[f + 10], 15, -1051523)
          , b = md5_ii(b, d, e, a, c[f + 1], 21, -2054922799)
          , a = md5_ii(a, b, d, e, c[f + 8], 6, 1873313359)
          , e = md5_ii(e, a, b, d, c[f + 15], 10, -30611744)
          , d = md5_ii(d, e, a, b, c[f + 6], 15, -1560198380)
          , b = md5_ii(b, d, e, a, c[f + 13], 21, 1309151649)
          , a = md5_ii(a, b, d, e, c[f + 4], 6, -145523070)
          , e = md5_ii(e, a, b, d, c[f + 11], 10, -1120210379)
          , d = md5_ii(d, e, a, b, c[f + 2], 15, 718787259)
          , b = md5_ii(b, d, e, a, c[f + 9], 21, -343485551)
          , a = safe_add(a, h)
          , b = safe_add(b, i)
          , d = safe_add(d, k)
          , e = safe_add(e, j);
    return [a, b, d, e]
}
function md5_cmn(c, g, a, b, d, e) {
    return safe_add(bit_rol(safe_add(safe_add(g, c), safe_add(b, e)), d), a)
}
function md5_ff(c, g, a, b, d, e, f) {
    return md5_cmn(g & a | ~g & b, c, g, d, e, f)
}
function md5_gg(c, g, a, b, d, e, f) {
    return md5_cmn(g & b | a & ~b, c, g, d, e, f)
}
function md5_hh(c, g, a, b, d, e, f) {
    return md5_cmn(g ^ a ^ b, c, g, d, e, f)
}
function md5_ii(c, g, a, b, d, e, f) {
    return md5_cmn(a ^ (g | ~b), c, g, d, e, f)
}
function safe_add(c, g) {
    var a = (c & 65535) + (g & 65535);
    return (c >> 16) + (g >> 16) + (a >> 16) << 16 | a & 65535
}
function bit_rol(c, g) {
    return c << g | c >>> 32 - g
}

function ws_str_encrypt(a) {
    for (var d = a.length, e = d / 2 + 1, f = [], c, g = "", h = 0, k = d - 1; h < e; h++,
    k--)
        d = a.charAt(h),
        c = a.charAt(k),
        f[h] = c,
        f[k] = d;
    for (h = 0; h < f.join("").length; h++)
        g += "%" + (f.join("").charCodeAt(h) ^ 55).toString();
    return g
}

function conplat_str_encrypt(a) {
    function d(a, d) {
        if (a.src.length != 0) {
            a.tmp_dest[0] = a.src[0] ^ d ^ a.src.length - 1 & 127;
            for (var c = 1; c < a.src.length; ++c)
                a.tmp_dest[c] = a.src[c] ^ a.tmp_dest[c - 1] ^ c & 127 ^ a.src.length - 1 & 127;
            var c = [], f, g;
            for (f = g = 0; f < a.src.length; )
                48 <= a.tmp_dest[f] && a.tmp_dest[f] <= 57 || 97 <= a.tmp_dest[f] && a.tmp_dest[f] <= 122 || 65 <= a.tmp_dest[f] && a.tmp_dest[f] <= 90 || (c[g++] = 36),
                c[g++] = e[a.tmp_dest[f++]].charCodeAt();
            a.tmp_dest = c
        }
    }
    var e = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "$", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "l", "m", "n", "o", "p", "q", "r", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "s", "t", "u", "v", "w", "x", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "y", "z", "_", ".", "/"]
      , f = {
        dest: []
    }
      , c = [];
    if ("" == a)
        return a;
    var a = a.split(""), g;
    for (g in a)
        c[g] = a[g].charCodeAt();
    f.src = c;
    f.tmp_dest = [];
    (function(a) {
        var c;
        c = parseInt(Math.random() * 100) % 90 + 10;
        d(a, c);
        a.src[0] = parseInt(c / 10) + 48;
        a.src[1] = c % 10 + 48;
        for (c = 0; c < a.tmp_dest.length; ++c)
            a.src[c + 2] = a.tmp_dest[c];
        d(a, 65);
        var e = "%@%@";
        for (c = 0; c < a.tmp_dest.length; ++c)
            e += String.fromCharCode(a.tmp_dest[c]);
        a.dest = e;
        return 0
    }
    )(f);
    return f.dest
}

function getEncryptCode(pData,ycode) {
    var vtysh;
    var encodestr;

    //页面下发时会增加verify字段，所以算加密字段时也要加上
    vtysh = "jccs" + ycode;
    encodestr = pData.join("&");
    encodestr = (encodestr+vtysh).toString();
    encryptData = hex_md5(encodestr);
    return encryptData
}

function valid_refresh()
{
    var d=new Date();
    var s=""+(d.getYear())+(d.getMonth()+1)+(d.getDay())+(d.getHours())+(d.getMinutes())+(d.getSeconds())+(d.getMilliseconds());
    return hex_md5(s).toLowerCase()
}
"""
    # 执行 JavaScript 代码
    ctx = execjs.compile(js_code)
    check = ctx.call("valid_refresh")
    uname = ctx.call("conplat_str_encrypt", username)
    pwd = ctx.call("conplat_str_encrypt", password)
    i = 1
    while True:
        if i > 10:
            return None
        url = 'https://10.138.36.249:8889/func/web_main/validate?check=' + check
        main_url_html = requests.get(url=url, verify=False)
        ocr = ddddocr.DdddOcr(show_ad=False)
        image = main_url_html.content
        code = ocr.classification(image)

        pData = ["_csrf_token=4356274536756456326", "uname=" + uname, "ppwd=" + pwd, "language=1", "ppwd1=", "otp_value=",
                 "code=" + code, "check=" + check]
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'slotType=0; SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV; BACKUP_SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV',
            'Host': '10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/html/login.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        url = 'https://10.138.36.249:8889/func/web_main/login_tamper/user/user_login_check_code'
        main_url_html = requests.get(url=url, headers=headers, verify=False)
        response = main_url_html.text
        match = re.search(r'<checkcode>(.*?)</checkcode>', response)
        ycode = match.group(1)
        encryptCode = ctx.call("getEncryptCode", pData, ycode)

        params = {
            '_csrf_token': '4356274536756456326',
            'uname': uname,
            'ppwd': pwd,
            'language': '1',
            'ppwd1': '',
            'otp_value': '',
            'code': code,
            'check': check,
            'encryptCode': encryptCode
        }
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '258',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'slotType=0; SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV; BACKUP_SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV',
            'Host': '10.138.36.249:8889',
            'Origin': 'https://10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/html/login.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        url = 'https://10.138.36.249:8889/func/web_main/login'
        main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
        response = main_url_html.text
        if response.__contains__("校验码验证失败！"):
            i = i + 1
            print("校验码验证失败！")
            time.sleep(1)
            continue
        cookies = main_url_html.cookies
        cookie_list = cookies.get_dict()
        SID = cookie_list.get('SID')

        headers2 = {
            'Accept': 'text/css,*/*;q=0.1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'slotType=0; SID='+SID+'; BACKUP_SID='+SID,
            'Host': '10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/func/web_main/display/frame/main',
            'Sec-Fetch-Dest': 'xslt',
            'Sec-Fetch-Mode': 'same-origin',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        return headers2

def dpfhq_logout(headers):
    url = 'https://10.138.36.249:8889/func/web_main/logout?lang=cn'
    main_url_html = requests.get(url=url, headers=headers, verify=False)

def dpfhq_port_management_getValueId(ip: str, headers: dict) -> str | None:
    params = {
        'searchsips': ip,
        'searchsipe': ip,
        'searchages': 0,
        'searchagee': 31535999,
        'searchact': 0,
        'searchgroups': 128,
        'searchsta': 2,
        'searchgroupname': None
    }
    url = 'https://10.138.36.249:8889/func/web_main/display/maf/maf_addrfilter/maf_cidr_v4_wblist'
    main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
    response = main_url_html.text
    match = re.search(r'<TR VALUE="(.*?)">', response)
    if match:
        ycode = match.group(1)
        return ycode
    else:
        return None


class DpipblockServer:
    def dpfhq_port_management_add(self, ip: str, time_str: str) -> str:
        headers = dpfhq_login('admin', 'Khxxb2421!@')
        if headers is not None:
            # 将时间字符串转换为秒数
            time_seconds = convert_time_to_seconds(time_str)
            
            params = {
                'to_add': '端口封禁?Default?1?'+ip+'?'+ip+'?32?'+time_seconds+'?2?1',
                'del_all': None
            }
            url = 'https://10.138.36.249:8889/func/web_main/submit/maf/maf_addrfilter/maf_cidr_v4_wblist'
            main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
            response = main_url_html.text
            dpfhq_logout(headers)
            if response.__contains__("HiddenSubWin"):
                return f"({ip})端口封禁成功！封禁时长：{time_str}（{time_seconds}秒）"
            else:
                return f"({ip})端口封禁失败！"
        else:
            return f"({ip})登录失败，无法执行封禁操作！"
    
    
    def dpfhq_port_management_delete(self, ip: str) -> str:
        headers = dpfhq_login('admin', 'Khxxb2421!@')
        if headers is not None:
            valueId = dpfhq_port_management_getValueId(ip, headers)
            if valueId is not None:
                params = {
                    'to_delete': valueId + '?Default?1?'+ip+'?'+ip+'?32?180?2?1',
                    'del_all': None
                }
                url = 'https://10.138.36.249:8889/func/web_main/submit/maf/maf_addrfilter/maf_cidr_v4_wblist'
                main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
                response = main_url_html.text
                dpfhq_logout(headers)
                if response.__contains__("HiddenSubWin"):
                    return "(" + ip + ")端口解禁成功！"
                else:
                    return "(" + ip + ")端口解禁失败！"
            else:
                dpfhq_logout(headers)
                return f"({ip})未找到对应的封禁记录！"
        else:
            return f"({ip})登录失败，无法执行解禁操作！"


async def serve() -> None:
    """运行IP管理MCP服务"""
    server = Server("mcp-dpipblock")
    tdpipblock_server = DpipblockServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available dpipblock tools."""
        return [
            Tool(
                name=DpipblockTools.PORT_ADD.value,
                description="在防火墙层面封禁IP地址",
                inputSchema= {
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be blocked at the port level, e.g., '192.168.1.1'",
                        },
                        "time": {
                            "type": "string",
                            "description": "Time of sequestration. Supports formats: '永久'(permanent), '1分钟'/'1min'/'1m', '1小时'/'1hour'/'1h', '1天'/'1day'/'1d', '1周'/'1week'/'1w', '1月'/'1month', '1年'/'1year'/'1y', or pure number (seconds)",
                        }
                    },
                    "required": ["ip","time"]
                },
            ),
            Tool(
                name=DpipblockTools.PORT_DELETE.value,
                description="在防火墙层面解封IP地址",
                inputSchema = {
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be unblocked at the port level, e.g., '192.168.1.1'",
                        }
                    },
                    "required": ["ip"]
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            match name:
                case DpipblockTools.PORT_ADD.value:
                    if not all(
                        k in arguments
                        for k in ["ip", "time"]
                    ):
                        raise ValueError("Missing required arguments")
                    
                    result = tdpipblock_server.dpfhq_port_management_add(
                        arguments["ip"],
                        arguments["time"],
                        )

                case DpipblockTools.PORT_DELETE.value:
                    ip = arguments.get("ip")
                    if not ip:
                        raise ValueError("Missing required argument: ip")
                    
                    result = tdpipblock_server.dpfhq_port_management_delete(ip)
               
                case _:
                    raise ValueError(f"Unknown tool: {name}")
            return [TextContent(type="text", text=result)]

        except Exception as e:
            raise ValueError(f"Error processing mcp-server-dpipblock query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


