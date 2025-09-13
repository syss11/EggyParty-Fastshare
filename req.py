import requests
from typing import *


def batch_submit(
    url: str,
    data_list: List[Dict],
    method: str = "POST",
    timeout: float = 10.0,
    headers: Optional[Dict] = None
) -> List[Tuple[bool, Optional[requests.Response], Optional[str]]]:
    """
    复用HTTP连接向目标地址批量提交信息
    
    :param url: 目标请求地址
    :param data_list: 待提交的信息列表，每个元素为一个请求数据字典
    :param method: 请求方法（默认POST）
    :param timeout: 超时时间（秒）
    :param headers: 额外请求头
    :return: 结果列表，每个元素为(是否成功, 响应对象, 错误信息)
    """
    results = []
    # 创建Session对象（自动复用连接）
    with requests.Session() as session:
        # 设置全局请求头（可选）
        if headers:
            session.headers.update(headers)
        
        for idx, data in enumerate(data_list):
            try:
                # 根据请求方法发送请求
                if method.upper() == "POST":
                    response = session.post(
                        url,
                        json=data,  # 使用json参数自动设置Content-Type为application/json
                        timeout=timeout
                    )
                elif method.upper() == "GET":
                    response = session.get(
                        url,
                        params=data,  # GET请求使用params传递参数
                        timeout=timeout
                    )
                else:
                    error_msg = f"不支持的请求方法: {method}"
                    results.append((False, None, error_msg))
                    continue
                
                # 检查HTTP状态码（2xx视为成功）
                response.raise_for_status()
                results.append((True, response, None))
                
                
            except requests.exceptions.RequestException as e:
                # 捕获所有请求相关异常（超时、连接错误等）
                error_msg = f"第{idx+1}条数据提交失败: {str(e)}"
                results.append((False, None, error_msg))
    
    return results