from nonebot import logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.matcher import Matcher

from ..config import config_manager
from ..utils import get_memory_data, write_memory_data


async def enable(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    """处理启用聊天功能的命令"""
    # 检查全局配置是否启用聊天功能
    if not config_manager.config.enable:
        matcher.skip()

    # 获取用户在群组中的角色信息
    member = await bot.get_group_member_info(
        group_id=event.group_id, user_id=event.user_id
    )
    # 如果用户是普通成员且不在管理员列表中，发送无权限提示
    if member["role"] == "member" and event.user_id not in config_manager.config.admins:
        await matcher.send("你没有这样的力量呢～（管理员/管理员+）")
        return

    # 记录日志
    logger.debug(f"{event.group_id} enabled")
    # 获取当前群组的记忆数据
    data = get_memory_data(event)
    # 检查记忆数据是否与当前群组匹配
    if data["id"] == event.group_id:
        # 如果聊天功能未启用，则启用并发送提示
        if not data["enable"]:
            data["enable"] = True
        await matcher.send("聊天启用")
    # 更新记忆数据
    write_memory_data(event, data)
