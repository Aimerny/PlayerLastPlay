from mcdreforged.api.all import *
import datetime


__mcdr_server: PluginServerInterface
data: dict


help_msg = '''-------- §a Player Last Play §r--------
§b!!plp help §f- §c显示帮助消息
§b!!plp list §f- §c全部玩家列表
§b!!plp get <player> §f- §c获取玩家的最后游玩时间
§b!!plp clean <player> §f- §c清除玩家的信息
-----------------------------------
'''


def on_load(server: PluginServerInterface, old):
    # 获取存量数据
    global data, __mcdr_server
    __mcdr_server = server
    data = server.load_config_simple(
        'data.json',
        default_config = {'player_list': {}},
        echo_in_console=True
    )['player_list']
    server.register_help_message('!!plp', '获取玩家最后一次游玩时间')

    #注册指令
    command_builder = SimpleCommandBuilder()
    command_builder.command('!!plp list', player_list)
    command_builder.command('!!plp get <player>', get_player)
    command_builder.command('!!plp clean <player>', clean_player)
    command_builder.command('!!plp help', help_info)
    command_builder.command('!!plp', help_info)
    command_builder.arg('player', Text)
    command_builder.register(server)
    

def on_player_left(server: PluginServerInterface, player: str):
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    data[player] = now

    server.logger.info(f'player {player} last play time updated!!')
    save_data(server)


# -------------------------
# command handlers
# -------------------------
def help_info(server):
    for line in help_msg.splitlines():
        server.reply(line)


def player_list(server):
    resp = '------ &a玩家列表 &r------'
    online_players = get_online_players()
    # 先统计在线的玩家
    for player in online_players:
        # 跳过假人
        if not player.startswith('bot_'):
            resp = resp + f'\n|- &a{player}&r:&a在线'

    for player in data:
        # 只统计不在线的玩家
        if player not in online_players:
            resp = resp + f'\n|- &a{player}&r:&c{data[player]}'

    server.reply(replace_code(resp))


def get_player(server, context):
    player = context['player']
    online_players = get_online_players()
    resp:str
    if player in online_players:
        resp = f'玩家&a{player}&r当前&e在线'
    elif player in data:
        resp = f'玩家&a{player}&r最近的游玩时间为&e{data[player]}'
    else:
        resp = f'当前没有玩家&a{player}&r的游玩时间'
    server.reply(replace_code(resp))


def clean_player(server, context):
    player = context['player']
    resp:str
    if player in data:
        del data[player]
        resp = f'已清除玩家&a{player}&r最近的游玩时间'
    else:
        resp = f'当前没有玩家&a{player}&r的游玩时间'
    server.reply(replace_code(resp))
    
    


# -------------------------
# utils
# -------------------------

def save_data(server: PluginServerInterface):
    server.save_config_simple({'player_list': data}, 'data.json')


def replace_code(msg: str) -> str:
    return msg.replace('&','§')


def get_online_players() -> list:
    online_player_api = __mcdr_server.get_plugin_instance('online_player_api')
    return online_player_api.get_player_list()