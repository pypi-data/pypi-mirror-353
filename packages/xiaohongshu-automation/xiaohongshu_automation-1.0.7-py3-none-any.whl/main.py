# local_api.py
from fastapi import FastAPI, Query, Body, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel
import subprocess
from xiaohongshu_tools import XiaohongshuTools
import logging
import time
import threading
from unti import get_news,get_comments_and_reply
from license_manager import LicenseManager
import sys
from pathlib import Path

# 定义请求模型
class PublishRequest(BaseModel):
    pic_urls: List[str]
    title: str
    content: str
    labels: Optional[List[str]] = None  # 添加可选的labels字段

class ActivationRequest(BaseModel):
    activation_code: str

class CommentRequest(BaseModel):
    comment: str
    metions_lists: Optional[List[str]] = None  # 添加可选的@提及列表字段

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 初始化许可证管理器
license_manager = LicenseManager()

# 创建静态文件目录
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# 添加静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 在应用启动时检查许可证
@app.on_event("startup")
async def startup_event():
    """应用启动时的许可证检查"""
    print("\n" + "="*60)
    print("🚀 小红书自动化工具启动中...")
    print("="*60)
    
    # 检查许可证有效性
    if not license_manager.is_valid():
        expiry_info = license_manager.get_expiry_info()
        print(f"❌ 许可证验证失败: {expiry_info['message']}")
        print("💡 请使用激活码激活软件")
        print("📧 如需获取激活码，请联系软件提供商")
        print("="*60)
        
        # 显示激活码接口信息
        print("🔑 激活方式:")
        print("   方法1: 访问 http://localhost:8000/activate 网页激活")
        print("   方法2: 访问 http://localhost:8000/docs 使用API激活")
        print("   方法3: 使用命令行工具激活")
        print("="*60)
    else:
        expiry_info = license_manager.get_expiry_info()
        print(f"✅ 许可证验证成功")
        print(f"📅 有效期至: {expiry_info['expiry_date']}")
        print(f"⏰ 剩余时间: {expiry_info['remaining_days']} 天")
        print(f"🏷️ 许可证类型: {expiry_info['license_type']}")
        
        # 检查是否即将过期
        warning = license_manager.check_and_warn_expiry()
        if warning:
            print(f"⚠️ {warning}")
        
        print("="*60)

# 许可证中间件
@app.middleware("http")
async def license_middleware(request, call_next):
    """许可证验证中间件"""
    # 跳过许可证相关的接口
    license_exempt_paths = ["/", "/docs", "/openapi.json", "/license/status", "/license/activate", "/activate", "/static"]
    
    if any(request.url.path.startswith(path) for path in license_exempt_paths):
        response = await call_next(request)
        return response
    
    # 检查许可证
    if not license_manager.is_valid():
        raise HTTPException(status_code=403, detail={
            "error": "许可证无效或已过期",
            "message": "请激活软件后重试",
            "license_info": license_manager.get_expiry_info()
        })
    
    response = await call_next(request)
    return response

tools = XiaohongshuTools()

def run_get_comments_and_reply():
    retry_count = 0
    max_retries = 5
    reply_count = 0
    while True:
        # 在后台任务中也检查许可证
        if not license_manager.is_valid():
            logger.warning("许可证已过期，停止后台任务")
            break
            
        try:
            url= "https://www.xiaohongshu.com/explore/67b94551000000002902b506?xsec_token=AB6AsqCQ2ck6I6ANbnEuEPHjAxMwvYCAm00BiLxfjU9o8=&xsec_source=pc_user"
            comments_data = get_comments_and_reply(url)
            logger.info("Successfully executed get_comments_and_reply()")
            reply_count += 1
            logger.info(f"Successfully executed get_comments_and_reply() {reply_count} times")
            retry_count = 0
        except Exception as e:
            if "[Errno 11001] getaddrinfo failed" or "network connectivity" in str(e):
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"getaddrinfo failed, retrying {retry_count}/{max_retries}...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"Max retries ({max_retries}) reached. Continuing main loop...")
            logger.error(f"Error executing get_comments_and_reply(): {str(e)}")
            # Don't break the loop on error, continue to next iteration
        logger.info("等待3分钟，准备下次执行")
        time.sleep(3 * 60)  # Sleep for 3 minutes before next iteration

# Start the background thread
#comments_thread = threading.Thread(target=run_get_comments_and_reply, daemon=True)
#comments_thread.start()
#logger.info("Comments thread started successfully")

# ==================== 许可证管理接口 ====================

@app.get("/")
def read_root():
    """根路径，显示应用信息和许可证状态"""
    expiry_info = license_manager.get_expiry_info()
    return {
        "app": "小红书自动化工具",
        "version": "2.0.0",
        "license_status": expiry_info,
        "api_docs": "/docs",
        "activation_page": "/activate"
    }

@app.get("/activate", response_class=HTMLResponse)
async def activation_page():
    """许可证激活网页"""
    expiry_info = license_manager.get_expiry_info()
    machine_id = license_manager._get_machine_id()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>小红书自动化工具 - 许可证激活</title>
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            
            .container {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: #333;
                font-size: 28px;
                margin-bottom: 10px;
            }}
            
            .header p {{
                color: #666;
                font-size: 16px;
            }}
            
            .status-card {{
                background: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 30px;
                border-left: 4px solid {'#28a745' if expiry_info['valid'] else '#dc3545'};
            }}
            
            .status-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }}
            
            .status-row:last-child {{
                margin-bottom: 0;
            }}
            
            .status-label {{
                font-weight: 500;
                color: #555;
            }}
            
            .status-value {{
                color: #333;
            }}
            
            .form-group {{
                margin-bottom: 25px;
            }}
            
            label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #333;
            }}
            
            input[type="text"] {{
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }}
            
            input[type="text"]:focus {{
                outline: none;
                border-color: #667eea;
            }}
            
            .btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 14px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s ease;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
            }}
            
            .btn:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }}
            
            .alert {{
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: none;
            }}
            
            .alert-success {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            
            .alert-error {{
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            
            .machine-info {{
                background: #e9ecef;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-family: monospace;
                font-size: 14px;
                word-break: break-all;
            }}
            
            .help-text {{
                font-size: 14px;
                color: #666;
                margin-top: 10px;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e1e5e9;
                color: #666;
                font-size: 14px;
            }}
            
            .api-link {{
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .api-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔑 许可证激活</h1>
                <p>小红书自动化工具</p>
            </div>
            
            <div class="status-card">
                <div class="status-row">
                    <span class="status-label">📋 许可证状态:</span>
                    <span class="status-value">{'✅ 有效' if expiry_info['valid'] else '❌ ' + expiry_info['message']}</span>
                </div>
                {'<div class="status-row"><span class="status-label">📅 有效期至:</span><span class="status-value">' + expiry_info['expiry_date'] + '</span></div>' if expiry_info['valid'] else ''}
                {'<div class="status-row"><span class="status-label">⏰ 剩余时间:</span><span class="status-value">' + str(expiry_info['remaining_days']) + ' 天</span></div>' if expiry_info['valid'] else ''}
                <div class="status-row">
                    <span class="status-label">🏷️ 许可证类型:</span>
                    <span class="status-value">{expiry_info.get('license_type', 'unknown')}</span>
                </div>
            </div>
            
            <div class="machine-info">
                <strong>🖥️ 机器ID:</strong> {machine_id}
                <div class="help-text">请向软件提供商提供此机器ID以获取专用激活码</div>
            </div>
            
            <div class="alert alert-success" id="successAlert"></div>
            <div class="alert alert-error" id="errorAlert"></div>
            
            <form id="activationForm">
                <div class="form-group">
                    <label for="activationCode">激活码</label>
                    <input type="text" id="activationCode" name="activationCode" 
                           placeholder="请输入激活码 (格式: MONTH-XXXXXXXX-XXXXXXXXXX-XXXXXXXXXXXXXXXXXXXX)" 
                           required>
                    <div class="help-text">
                        支持的激活码类型: WEEK (7天), MONTH (30天), QUARTER (90天), YEAR (365天)
                    </div>
                </div>
                
                <button type="submit" class="btn" id="activateBtn">
                    🚀 激活许可证
                </button>
            </form>
            
            <div class="footer">
                <p>💡 需要帮助？访问 <a href="/docs" class="api-link">API 文档</a> 了解更多信息</p>
                <p>📧 如需获取激活码，请联系软件提供商</p>
            </div>
        </div>
        
        <script>
            document.getElementById('activationForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const activationCode = document.getElementById('activationCode').value.trim();
                const submitBtn = document.getElementById('activateBtn');
                const successAlert = document.getElementById('successAlert');
                const errorAlert = document.getElementById('errorAlert');
                
                // 隐藏之前的提示
                successAlert.style.display = 'none';
                errorAlert.style.display = 'none';
                
                if (!activationCode) {{
                    showError('请输入激活码');
                    return;
                }}
                
                // 禁用按钮
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ 激活中...';
                
                try {{
                    const response = await fetch('/license/activate', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            activation_code: activationCode
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        showSuccess(`🎉 激活成功！许可证延长 ${{result.extended_days}} 天，新的有效期至: ${{result.new_expiry}}`);
                        document.getElementById('activationCode').value = '';
                        
                        // 3秒后刷新页面
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 3000);
                    }} else {{
                        showError(result.message || '激活失败');
                    }}
                }} catch (error) {{
                    showError('网络错误: ' + error.message);
                }} finally {{
                    // 恢复按钮
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 激活许可证';
                }}
            }});
            
            function showSuccess(message) {{
                const alert = document.getElementById('successAlert');
                alert.textContent = message;
                alert.style.display = 'block';
            }}
            
            function showError(message) {{
                const alert = document.getElementById('errorAlert');
                alert.textContent = '❌ ' + message;
                alert.style.display = 'block';
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/license/status")
def get_license_status():
    """获取许可证状态"""
    try:
        expiry_info = license_manager.get_expiry_info()
        warning = license_manager.check_and_warn_expiry()
        
        return {
            "license_info": expiry_info,
            "warning": warning,
            "machine_id": license_manager._get_machine_id()
        }
    except Exception as e:
        return {"error": f"获取许可证状态失败: {str(e)}"}

@app.post("/license/activate")
def activate_license(request: ActivationRequest):
    """激活许可证"""
    try:
        result = license_manager.activate_with_code(request.activation_code)
        
        if result["success"]:
            logger.info(f"许可证激活成功: {result['message']}")
            return {
                "success": True,
                "message": result["message"],
                "new_expiry": result["new_expiry"],
                "extended_days": result["extended_days"]
            }
        else:
            logger.warning(f"许可证激活失败: {result['message']}")
            return {
                "success": False,
                "message": result["message"]
            }
    except Exception as e:
        error_msg = f"激活过程中发生错误: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg
        }

# ==================== 原有业务接口 ====================

@app.post("/publish")
def publish(request: PublishRequest):
    """
    发布内容到小红书
    支持 JSON 请求体，避免 URL 过长问题
    """
    try:
        logger.info(f"接收到发布请求: {request.title}")
        urls = tools.publish_xiaohongshu(
            request.pic_urls, 
            request.title, 
            request.content, 
            request.labels  # 传递labels参数
        )
        if urls:    
            logger.info(f"发布成功: {request.title}")
            return {"status": "success", "urls": urls}
        else:
            logger.error(f"发布失败，未返回URL: {request.title}")
            return {"status": "error", "message": "发布失败，未获得发布链接"}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"发布异常: {request.title} - {error_msg}")
        return {"status": "error", "message": error_msg}
    
    
@app.post("/post_comments")
def post_comments(
    comments_response: dict[str,List[dict]] = Body(...),
    url: str = Query(...)
):
    try:
        tools.reply_comments(comments_response, url)
        return {"message": "success"}
    except Exception as e:
        message = f"Error posting comments: {str(e)}"
        logger.error(message)
        return {"message": message}
    
@app.get("/get_comments")
def get_comments(url: str):
    try:
        comments = tools.get_comments(url)
        if comments == "当前无评论":
            return {"status": "success", "message": "当前无评论"}
        return {"status": "success", "comments": comments}
    except Exception as e:
        message = f"Error getting comments: {str(e)}"
        logger.error(message)
        return {"status": "error", "message": message}

@app.get("/search_notes")
def search_notes(keywords: str = Query(...), limit: int = Query(5, ge=1, le=20)):
    """
    搜索小红书笔记
    
    Args:
        keywords: 搜索关键词
        limit: 返回结果数量限制，最多20条
    """
    try:
        logger.info(f"接收到搜索请求: {keywords}, 限制: {limit}")
        result = tools.search_notes(keywords, limit)
        logger.info(f"搜索完成: {keywords} - 找到 {len(result.get('data', []))} 条结果")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"搜索异常: {keywords} - {error_msg}")
        return {
            "success": False,
            "message": f"搜索失败: {error_msg}",
            "data": []
        }

@app.get("/get_note_content")
def get_note_content(url: str = Query(...)):
    """
    获取小红书笔记的详细内容
    
    Args:
        url: 小红书笔记URL
    """
    try:
        logger.info(f"接收到获取笔记内容请求: {url}")
        result = tools.get_note_content(url)
        if result.get("success"):
            logger.info(f"笔记内容获取成功: {url}")
        else:
            logger.warning(f"笔记内容获取失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"获取笔记内容异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"获取笔记内容失败: {error_msg}",
            "data": {}
        }

@app.get("/analyze_note")
def analyze_note(url: str = Query(...)):
    """
    分析小红书笔记内容，提取关键信息和领域标签
    
    Args:
        url: 小红书笔记URL
    """
    try:
        logger.info(f"接收到笔记分析请求: {url}")
        result = tools.analyze_note(url)
        if result.get("success"):
            logger.info(f"笔记分析成功: {url} - 主要领域: {result.get('data', {}).get('领域分析', {}).get('主要领域', [])}")
        else:
            logger.warning(f"笔记分析失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"笔记分析异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"笔记分析失败: {error_msg}",
            "data": {}
        }

@app.post("/post_comment")
def post_comment(url: str = Query(...), request: CommentRequest = Body(...)):
    """
    发布评论到指定小红书笔记
    
    Args:
        url: 小红书笔记URL
        request: 评论请求体，包含评论内容和可选的@提及列表
            - comment: 要发布的评论内容
            - metions_lists: 可选的@提及用户名列表，例如 ["用户1", "用户2"]
    """
    try:
        logger.info(f"接收到评论发布请求: {url}")
        logger.info(f"评论内容: {request.comment}")
        if request.metions_lists:
            logger.info(f"@ 提及列表: {request.metions_lists}")
        
        result = tools.post_comment(url, request.comment, request.metions_lists)
        
        if result.get("success"):
            logger.info(f"评论发布成功: {url}")
            if request.metions_lists:
                logger.info(f"包含 {len(request.metions_lists)} 个 @ 提及")
        else:
            logger.warning(f"评论发布失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"评论发布异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"评论发布失败: {error_msg}",
            "data": {}
        }

def check_license_on_startup():
    """启动时检查许可证"""
    print("\n" + "="*60)
    print("🔍 正在检查软件许可证...")
    print("="*60)
    
    if not license_manager.is_valid():
        expiry_info = license_manager.get_expiry_info()
        print(f"❌ 许可证验证失败: {expiry_info['message']}")
        print("💡 软件将以受限模式运行")
        print("🔑 请访问激活页面获取激活码")
        print("="*60)
        return False
    else:
        expiry_info = license_manager.get_expiry_info()
        print(f"✅ 许可证验证成功")
        print(f"📅 有效期至: {expiry_info['expiry_date']}")
        print(f"⏰ 剩余时间: {expiry_info['remaining_days']} 天")
        
        # 检查即将过期提醒
        warning = license_manager.check_and_warn_expiry()
        if warning:
            print(f"⚠️ {warning}")
        
        print("="*60)
        return True

def main():
    """主函数入口点，用于uvx调用"""
    import uvicorn
    import threading
    import time

    # 启动时检查许可证
    check_license_on_startup()

    def run_get_news():
        while True:
            # 在后台任务中也检查许可证
            if not license_manager.is_valid():
                logger.warning("许可证已过期，停止后台新闻任务")
                break
                
            try:
                time.sleep(10)
                get_news()
                logger.info("Successfully executed get_news()")
            except Exception as e:
                logger.error(f"Error executing get_news(): {str(e)}")
            time.sleep(6 * 60 * 60)  # Sleep for 6 hours

    # Start the background thread
    #news_thread = threading.Thread(target=run_get_news, daemon=True)
    #news_thread.start()

    logger.info("🚀 启动小红书自动化工具 FastAPI 服务器...")
    logger.info("📖 API 文档: http://localhost:8000/docs")
    logger.info("🔧 健康检查: http://localhost:8000/")
    logger.info("🔑 许可证激活: http://localhost:8000/activate")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


# 运行服务（默认端口 8000）
if __name__ == "__main__":
    main()