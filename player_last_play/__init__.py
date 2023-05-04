from typing import List
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

class Config(Serializable):
    # 一周内没上线属于很活跃
    active:int = 7
    # 两周内没上线属于较为一般
    normal:int = 14
    # 三周内没上线属于基本不活跃
    inactive:int = 21
    # 超过三周属于潜水

    reverse:bool = True

config: Config

class PlayerInfo:
    player:str
    last_date:datetime
    activity:str

    def __init__(self, player, last_date):
        self.player = player
        self.last_date = last_date
        self.activity = self.get_activity()

    def get_activity(self) -> str:
        now = datetime.datetime.now()
        days = (now - self.last_date).days
        
        if days < config.active:
            return 'active'
        elif days >= config.active and days < config.normal:
            return 'normal'
        elif days >= config.normal and days < config.inactive:
            return 'inactive'
        else:
            # (这么久不上线，危)
            return 'danger'


def on_load(server: PluginServerInterface, old):
    # 获取存量数据
    global config, data, __mcdr_server
    __mcdr_server = server
    config = server.load_config_simple(target_class=Config)
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
    if player.startswith('bot_') or player.startswith('Bot_'):
        return
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    data[player] = now

    server.logger.debug(f'player {player} last play time updated!!')
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
        if not player.startswith('bot_') and not player.startswith('Bot_'):
            resp = resp + f'\n&r|- &a{player}&r:&a在线'

    # 作排序，按日期从近到远排序
    offline_players = []
    for player in data:
        # 只统计不在线的玩家
        if player not in online_players:
            offline_players.append(PlayerInfo(player, datetime.datetime.strptime(data[player], '%Y-%m-%d')))
    
    sorted_off_players = sort_date(offline_players)
    for player in sorted_off_players:
        # 按游玩先后顺序排序
        resp = resp + f'\n|- &a{player.player}&r:&{get_color_by_activity(player.activity)}{player.last_date.strftime("%Y-%m-%d")}'
    server.reply(replace_code(resp))


def get_player(server, context):
    player = context['player']
    online_players = get_online_players()
    resp:str
    if player in online_players:
        resp = f'玩家&a{player}&r当前&a在线'
    elif player in data:
        playerInfo = PlayerInfo(player, datetime.datetime.strptime(data[player], '%Y-%m-%d'))
        resp = f'玩家&a{player}&r最近的游玩时间为&{get_color_by_activity(playerInfo.activity)}{data[player]}'
    else:
        resp = f'当前没有玩家&a{player}&r的游玩时间'
    server.reply(replace_code(resp))


def clean_player(server, context):
    if __mcdr_server.get_permission_level(server) < 3:
        resp = f'&c你没有权限清除玩家的最近游玩时间'
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

def sort_date(player_list:List[PlayerInfo]) -> List[PlayerInfo]:
    sorted_player_list = sorted(player_list, key= lambda player: player.last_date.timestamp(), reverse=config.reverse)
    return sorted_player_list

def get_color_by_activity(activity:str) -> str:
    print(activity)
    if activity == 'active' :
        # 绿色
        return 'a'
    elif activity == 'normal':
        # 黄色
        return 'e'
    elif activity == 'inactive':
        # 红色
        return 'c'
    else:
        # 灰色
        return '7'