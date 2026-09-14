# mcp_server/tools/ops_tools.py（新增）
from mcp_server.server import mcp
from app.services.cmdb_service import CMDBService
from app.services.ticket_service import TicketService
from app.services.server_status_service import ServerStatusService

cmdb_service = CMDBService()
ticket_service = TicketService()
server_status_service = ServerStatusService()




@mcp.tool()
async def query_cmdb_asset(keyword: str) -> str:
    """查询CMDB资产信息，包括负责人、所属业务、所在机房。
    keyword 可以是资产名称、资产ID或IP地址的部分关键词，支持模糊匹配。
    """
    return await cmdb_service.query_asset_as_text(keyword)

@mcp.tool()
async def create_ticket(server_ip: str, title: str, description: str, severity: str = "P3") -> str:
    """创建运维工单。用于记录需要跟进处理的故障或问题。

    参数：
    - server_ip: 故障服务器的IP地址
    - title: 工单标题，简要描述问题
    - description: 详细描述，包括现象、已排查的信息等
    - severity: 严重级别，可选 P1(最严重)/P2/P3/P4(默认P3)
    """
    return await ticket_service.create_ticket_as_text(server_ip, title, description, severity)

@mcp.tool()
async def query_server_status(ip: str) -> str:
    """查询服务器实时运行状态，包括CPU、内存、磁盘使用率和健康状态。

    参数：
    - ip: 服务器IP地址
    """
    return await server_status_service.get_status_as_text(ip)