import os
import threading
from flask import Flask, render_template,jsonify,request
import uuid
import json
from datetime import datetime
from flask_cors import CORS
import time
import pyperclip
from req import batch_submit
oriroad=os.getcwd()
app = Flask(__name__)
road = r"D:\ws\MuMuPlayer\nx_main" #mumu的含有adb.exe的文件夹路径，之后程序会跳转到那里
app.config['JSON_AS_ASCII'] = False  # 确保中文正常显示

auto_eggyhub=False
eggyhub_header={'Authorization':'Bearer 。'}
#开启该变量并填充你的token（浏览器检查 jwt），可以自动提交（礼物结尾加空格加礼物id）

CORS(app)  # 允许所有跨域请求
# 数据存储文件路径
DATA_FILE = oriroad+'/gifts.json'
RESULT=oriroad+'/result.json'
GIFT_LISTS_FILE = oriroad+'/gift_lists.json'

trans=[(410,248),(583,248),(755,248),(920,248)]
deltax=-178
deltay=47

def gettrans(index):
    print(index)
    index-=1
    colu=index//4
    row=index%4
    tra=trans[row]
    y=tra[1]+colu*155
    return (tra[0],y)

def getshare(index,num):
    time.sleep(0.2)
    sharelist=[]
    tran=gettrans(index)
    for i in range(num):
        tap(tran[0],tran[1])
        time.sleep(0.1)
        tap(tran[0]+deltax,tran[1]+deltay)
        time.sleep(0.6)
        clip=adbclipb()
        sharelist.append(clip)
        time.sleep(0.2)

    return sharelist
def startshare(info):
    
    order_map= {}  # key: gift_id, value: order
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)  # 原变量j改为config_data，命名更清晰
        
        # 构建映射：避免后续嵌套循环查找
        for item in config_data:
            # 确保配置项包含必要的"id"和"order"字段（防数据异常）
            if "id" in item and "order" in item:
                order_map[item["id"]] = item["order"]
            else:
                print(f"警告：配置项 {item} 缺少'id'或'order'字段，已跳过")
    
    except FileNotFoundError:
        print(f"错误：配置文件 {DATA_FILE} 不存在")
        return []  # 文件不存在时返回空列表，避免后续报错
    except json.JSONDecodeError:
        print(f"错误：配置文件 {DATA_FILE} 格式错误（非合法JSON）")
        return []
    except Exception as e:
        print(f"读取配置文件时发生未知错误：{str(e)}")
        return []

    # 2. 生成分享码列表（逻辑简化，避免嵌套循环）
    shareall= []
    for share in info:
        # 提取礼物信息（防KeyError：用.get()获取，缺失时跳过）
        gift_id = share.get("gift_id")
        gift_name = share.get("name", "未知礼物")  # 缺省值避免空值
        gift_quantity = share.get("quantity", 0)  # 数量默认为0，避免无效调用

        # 校验必要参数（无效数据直接跳过，减少无效计算）
        if not gift_id or gift_quantity <= 0:
            print(f"警告：礼物 {gift_name} 的gift_id缺失或数量无效，已跳过")
            continue

        # 从映射字典获取order（O(1)查找，替代原嵌套循环）
        order = order_map.get(gift_id)
        if not order:  # 无匹配order时跳过（原逻辑的b==0）
            print(f"警告：礼物 {gift_name}（ID:{gift_id}）未在配置文件中找到对应order，已跳过")
            continue

        # 调用getshare生成分享码（原逻辑不变，确保getshare返回合法列表）
        thislist = getshare(order, gift_quantity)
        if thislist:  # 仅当分享码列表非空时添加（避免空数据）
            shareall.append({"name": gift_name, "codes": thislist})

    return shareall


def init_data_file():
    """初始化数据文件，如果不存在则创建并添加默认数据"""
    # 初始化礼物数据文件
    if not os.path.exists(DATA_FILE):
        default_gifts = {
            "gifts": [
                {"id": 1, "name": "第一位分享码", "image": "http://eggyhub.top/static/eggloading.jpg", "order": 1}
                
            ]
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_gifts, f, ensure_ascii=False, indent=2)
    
    # 初始化礼物清单数据文件
    if not os.path.exists(GIFT_LISTS_FILE):
        with open(GIFT_LISTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    # 初始化礼物清单数据文件
    if not os.path.exists(RESULT):
        with open(RESULT, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def read_gifts():
    """从JSON文件读取礼物数据"""
    init_data_file()
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        app.logger.error(f"读取礼物数据失败: {str(e)}")
        return []

def save_gifts(gifts):
    """将礼物数据保存到JSON文件"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(gifts, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        app.logger.error(f"保存礼物数据失败: {str(e)}")
        return False

def save_share(gifts):
    """将数据保存到JSON文件"""
    try:
        with open(RESULT, 'w', encoding='utf-8') as f:
            json.dump(gifts, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        app.logger.error(f"保存礼物数据失败: {str(e)}")
        return False
    
def read_gift_lists():
    """读取礼物清单数据"""
    with open(GIFT_LISTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_gift_list(list_data):
    """保存新的礼物清单"""
    all_lists = read_gift_lists()
    all_lists.append(list_data)
    
    with open(GIFT_LISTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_lists, f, ensure_ascii=False, indent=2)
    return len(all_lists) - 1  # 返回新清单的索引

@app.route('/api/gifts', methods=['GET'])
def get_gifts():
    """获取所有礼物数据"""
    gifts = read_gifts()
    return jsonify({
        "success": True,
        "data": {
            "gifts": gifts
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/gifts/save', methods=['POST'])
def save_gifts_data():
    """保存礼物数据"""
    data = request.get_json()
    
    if not data or 'gifts' not in data:
        return jsonify({
            "success": False,
            "message": "无效的数据格式，缺少礼物列表"
        }), 400
    
    # 为新礼物生成ID（如果没有）
    gifts = data['gifts']
    existing_ids = [g['id'] for g in read_gifts() if 'id' in g]
    
    for gift in gifts:
        if not gift.get('id') or gift['id'] not in existing_ids:
            gift['id'] = str(uuid.uuid4())
    
    # 保存数据
    if save_gifts(gifts):
        return jsonify({
            "success": True,
            "message": "礼物数据保存成功",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "success": False,
            "message": "保存礼物数据失败，请重试"
        }), 500

@app.route('/api/gifts/add', methods=['POST'])
def add_gift():
    """添加单个礼物（可选接口）"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({
            "success": False,
            "message": "无效的数据格式，缺少礼物名称"
        }), 400
    
    gifts = read_gifts()
    new_gift = {
        "id": str(uuid.uuid4()),
        "name": data['name'],
        "image": data.get('image', f"https://picsum.photos/seed/gift{len(gifts)+1}/200/200"),
        "order": len(gifts) + 1
    }
    
    gifts.append(new_gift)
    
    if save_gifts(gifts):
        return jsonify({
            "success": True,
            "message": "礼物添加成功",
            "data": {
                "gift": new_gift
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "添加礼物失败，请重试"
        }), 500

@app.route('/api/gifts/delete/<gift_id>', methods=['DELETE'])
def delete_gift(gift_id):
    """删除单个礼物（可选接口）"""
    gifts = read_gifts()
    initial_count = len(gifts)
    
    # 过滤掉要删除的礼物
    gifts = [g for g in gifts if g.get('id')!= gift_id]
    
    if len(gifts) == initial_count:
        return jsonify({
            "success": False,
            "message": f"未找到ID为 {gift_id} 的礼物"
        }), 404
    
    # 重新排序
    for i, gift in enumerate(gifts):
        gift['order'] = i + 1
    
    if save_gifts(gifts):
        return jsonify({
            "success": True,
            "message": "礼物删除成功"
        })
    else:
        return jsonify({
            "success": False,
            "message": "删除礼物失败，请重试"
        }), 500
    

# 新增礼物清单接口
@app.route('/api/gifts/list/submit', methods=['POST'])
def submit_gift_list():
    # try:
        data = request.json
        
        # 验证请求数据
        if not data or 'list' not in data:
            return jsonify({
                'success': False,
                'message': '无效的数据格式，缺少清单内容'
            }), 400
        
        # 验证清单项格式
        for item in data['list']:
            
            if not isinstance(item['quantity'], int) or item['quantity'] < 1:
                return jsonify({
                    'success': False,
                    'message': f'礼物"{item["name"]}"的数量必须是正整数'
                }), 400
        
        # 准备保存的清单数据
        list_data = {
            'id': str(uuid.uuid4()),  # 生成唯一ID
            'submitted_at': data.get('submitted_at', datetime.now().isoformat()),
            'items': data['list'],
            'total_items': sum(item['quantity'] for item in data['list']),
            'created_time': datetime.now().isoformat()
        }

        alls=startshare(data['list'])
        print(alls)
        save_share(alls)
        print("结果已保存到当前目录result.json内。")
        if auto_eggyhub:
            allids=[]
            for i in alls:
                n=i.get('name').split()
                if len(n)==2:
                    for c in i.get('codes'):
                        allids.append({'id':int(n[1]),'code':c})
            
            resu=batch_submit('https://eggyhub.top/api/gifts/update',data_list=allids,headers=eggyhub_header)
            print(resu)
        # 保存清单
        list_index = save_gift_list(list_data)
        
        return jsonify({
            'success': True,
            'message': '礼物清单提交成功',
            'data': {
                'list_id': list_data['id'],
                'index': list_index
            }
        })
    # except Exception as e:
    #     return jsonify({
    #         'success': False,
    #         'message': f'提交礼物清单失败: {str(e)}'
    #     }), 500

# 获取历史清单接口（可选）
@app.route('/api/gifts/list/history', methods=['GET'])
def get_gift_list_history():
    try:
        all_lists = read_gift_lists()
        return jsonify({
            'success': True,
            'data': {
                'total': len(all_lists),
                'lists': all_lists
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取清单历史失败: {str(e)}'
        }), 500
    


@app.route("/")
def home():
    return render_template("index.html")


def run_flask():
    """在单独线程中运行Flask应用"""
    # 关闭debug模式的自动重载，避免多线程问题
    app.run(debug=False, use_reloader=False)

def adb(ex):
    os.system("adb.exe -s 127.0.0.1:16384 shell "+ex)

def adbclipb():
    return pyperclip.paste()

def tap(x,y):
    adb(f'input tap {x} {y}')

def init(road_path):
    os.chdir(road_path)
    
    # 启动模拟器
    os.system(r".\myandroid.lnk")
    input("请确认模拟器已启动，按回车继续...")
    
    # 连接adb
    os.system("adb.exe connect 127.0.0.1:16384")
    


if __name__ == "__main__":
    init_data_file()
    # 执行初始化操作
    init(road)
    
    
    # 在后台线程启动Flask
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("Flask应用已在后台启动")
    time.sleep(1.5)
    input("进入分享码界面后继续......")
    # 保持主线程运行，否则程序会退出
    while True:
        try:
            # 可以在这里添加其他需要交互的命令
            cmd = input("请输入命令（或前往localhost:5000操作：")
            if cmd.lower() == "exit":
                break
            os.system(cmd)
        except KeyboardInterrupt:
            break
    os.system("adb.exe disconnect")
