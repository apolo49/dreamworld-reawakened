#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from urllib.parse import urlparse, parse_qs
import time

class S(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("GET %s\n", str(self.path))
        path = urlparse(self.path).path
        if(path == "/api/"):
            queryString = urlparse(self.path).query
            query = parse_qs(queryString, strict_parsing=True)
            apiName = query["p"][0]
            print(apiName)
            if(apiName == "pgl.news.information_list"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"list":[], "total_count":0}')
            elif(apiName == "pgl.member.profile.my_state"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"{}")
            elif(apiName == "pdw.home.my_island"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"island_id":201, "arranged_interior_list":[]}')
            elif(apiName == "pdw.croft.my_croft_list"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"croft_list":[:"kinomi_state":0, "my_croft_id": 0, "pokeitem_id": 0, "kinomi": 0, "kinomi_id": 52, "dirt_hp": 0, "x": 1, "y": 1}, :"kinomi_state":0, "my_croft_id": 0, "pokeitem_id": 0, "kinomi": 0, "kinomi_id": 52, "dirt_hp": 0, "x": 2, "y": 1}], "diglett_flag":0}')
            elif(apiName == "pdw.croft.tutorial_start"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{}')
            elif(apiName == "pdw.croft.tutorial_end"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{}')
            elif(apiName == "pdw.home.my_bridge"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{}')
            elif(apiName == "pdw.dreamland.top"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"dreamland_area_id":3, "object_list":[]}')
            elif(apiName == "pdw.dreamland.tree_top"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"pokemon_list":[], "encount_list":[{}]}')
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"")
            return
            
        # ruffle test, didn't work
        if(path == "/"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<object data-flashhack="undefined" style="visibility: visible;" data="/data/main.swf" id="flashcontent" type="application/x-shockwave-flash" height="528" width="1003"><param value="true" name="allowFullScreen"><param value="always" name="allowScriptAccess"><param value="false" name="menu"><param value="opaque" name="transparent"><param value="noscale" name="scale"><param value="shortcut=undefined&amp;mailto=undefined&amp;rankingto=undefined&amp;infoto=undefined&amp;api_host_name=/api/&amp;page=SITE_PDW&amp;json=%7B%22member%22%3A%7B%22member_id%22%3A%2211384399%22%2C%22pgl_name%22%3A%22MinakoArtemis5%22%2C%22country_id%22%3A%22176%22%2C%22special_flag%22%3A%220%22%2C%22bridge_flag%22%3A%220%22%2C%22special_disp_flag%22%3A%220%22%2C%22member_created_at%22%3A%222012-11-05%22%2C%22disclosure_flag%22%3A%220%22%2C%22list_disclosure_flag%22%3A%220%22%2C%22member_savedata_id%22%3A%223392301%22%2C%22gsid%22%3A%22415131399%22%2C%22sleep_time%22%3A%220%22%2C%22sleep_pokemon_count%22%3A%229%22%2C%22send_pokemon_count%22%3A%229%22%2C%22island_id%22%3A%22201%22%2C%22shelf_id%22%3A%22301%22%2C%22disable_flag%22%3A%220%22%2C%22wateringpot_id%22%3A%221%22%2C%22avator_id%22%3A%22185%22%2C%22first_flag%22%3A%221%22%2C%22trial_flag%22%3A%220%22%2C%22sleeping_flag%22%3A%221%22%2C%22rom_id%22%3A%2223%22%2C%22pokemon_no%22%3A%22493%22%2C%22form_no%22%3A%220%22%2C%22player_badge_num%22%3A%228%22%2C%22last_started_at%22%3A%221353477934%22%2C%22last_logined_at%22%3A%221353477934%22%2C%22deleted_at%22%3Anull%2C%22pdw_copied_at%22%3A%222012-11-21%2015%3A04%3A01%22%2C%22pgl_copied_at%22%3A%222012-11-21%2015%3A05%3A34%22%2C%22item_deleted_flag%22%3A%220%22%2C%22world_id%22%3A%221%22%2C%22avator_name%22%3A%22Passho%20Berry%22%2C%22gsid_count%22%3A%221%22%2C%22point%22%3A%220%22%2C%22experiment_point%22%3A%2219970%22%2C%22is_initializing%22%3A0%2C%22langcode%22%3A%222%22%2C%22player_name%22%3A%22%u30A2%u30EB%u30C6%u30DF%u30B9%u306E%22%2C%22play_status%22%3A%222%22%2C%22isin_sleep_pokemon%22%3A%221%22%2C%22last_up_time%22%3A%2211/21/12%2001%3A02%22%2C%22last_up_time_strict%22%3A%222012-11-21%2015%3A02%3A46%22%2C%22rom_name%22%3A%22Pok%E9mon%20Black%20Version%202%22%2C%22alter_rom_name%22%3A%22Kuro*%22%2C%22pokemon_name%22%3A%22Arceus%22%2C%22type1%22%3A%22Normal%22%2C%22type2%22%3Anull%2C%22gscd%22%3A%22H236MNWFFD%22%2C%22is_downloaded%22%3A0%2C%22nextstart_remaintime%22%3A71974%2C%22last_started_at_timezone%22%3A%221353427534%22%2C%22unread_mail_count%22%3A%220%22%7D%2C%22token%22%3A%2244tkn50ac6f48077c79.25427156%22%2C%22medals%22%3A%5B%5D%7D&amp;v=2.0&amp;lang=http://en.pokemon-gl.com/pdw/" name="flashvars"><param name="wmode" value="opaque"></object>')
            
        with open('./'+path, "rb") as f:
            self.send_response(200)
            data = f.read()
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.wfile.write(b"Error: Not found")

    def do_POST(self):
        logging.info("POST %s\n", str(self.path))
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        query = parse_qs(post_data.decode(), strict_parsing=True)
        print(query)
        apiName = query["p"][0]
        print(apiName)
        if(apiName == 'pdw.home.pdw_timecheck'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")
        elif(apiName == 'pgl.member.profile.pdw_login'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")
        elif(apiName == 'pdw.home.pdw_start'):
            print('{"started_at":'+str(int(time.time()))+'}')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(('{"started_at":'+str(int(time.time()))+'}').encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"")
        return
        
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.wfile.write(b"Error: Not found")

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting server...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping server...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
