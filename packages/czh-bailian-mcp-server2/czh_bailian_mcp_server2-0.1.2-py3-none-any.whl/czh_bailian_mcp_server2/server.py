# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import logging
import dashscope
logger = logging.getLogger('mcp')
settings = {
    'log_level': 'DEBUG'
}
# 初始化mcp服务
mcp = FastMCP('czh-bailian-mcp-server2', log_level='ERROR', settings=settings)
# 定义工具
@mcp.tool(name='回复专家', description='回复专家，根据用户发的消息，在后面加上我收到了')
async def reply_moderator( msg:str) -> str:

    return str(msg+",我收到了")
def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
   run()