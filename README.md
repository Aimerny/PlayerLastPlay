# PlayerLastPlay
统计玩家最后一次上线时间，方便查看玩家活跃度，清理僵尸（bushi

## 使用姿势

```
!!plp [help] #插件帮助
!!plp help #显示帮助消息
!!plp list  #全部玩家列表
!!plp get <player> #获取玩家的最后游玩时间
!!plp clean <player> #清除玩家的信息
```
>清除玩家信息权限需要玩家权限在`Admin`以上

## 配置说明
> 以下注释中的数字均为默认配置，可根据服务器状况自行配置。不同的颜色目前只做提示，并无其他功能

```json5
    {
    // 第一区间，7天内上线过或者当前在线，时间展示为绿色
    "active": 7, 
    // 第二区间，介于7-14天之间上线过，时间展示为黄色
    "normal": 14,
    // 第三区间，介于14-21天内上线过，时间展示为红色
    "inactive": 21,
    // 第四区间，21天及以上没上线过，时间展示为灰色


    //plp list时的排序方向，如设为true，优先展示最近上线的玩家，否则优先展示最近没上过线的玩家
    "reverse": true
    }

```

部分Utils及代码风格来自于[离线白名单](https://github.com/EMUnion/AdvancedWhitelistR)以及[QQChat](https://github.com/Aimerny/MCDReforgedPlugins/tree/master/qq_chat)插件
