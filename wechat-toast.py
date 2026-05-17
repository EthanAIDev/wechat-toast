import os
import time
import re
import threading
import base64
import tkinter as tk
import queue
import unicodedata
import tempfile
import win32gui
import win32process
import win32api
import psutil
import ctypes
import logging
from datetime import datetime
import pythoncom  # 添加这行
import uiautomation as auto
from winotify import Notification, audio
try:
    from pywinauto import Desktop
except ImportError:
    Desktop = None

# 配置日志
DEFAULT_LOG_LEVEL_NAME = os.environ.get("WECHAT_NOTIFIER_LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, DEFAULT_LOG_LEVEL_NAME, logging.INFO)
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDED_ICON_PATH = None
WX_LOGO_BASE64 = "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"

# 微信窗口信息
WECHAT_WINDOW_NAMES = ("微信", "WeChat", "Weixin")
WECHAT_PROCESS_NAMES = ("WeChat.exe", "WeChatAppEx.exe")
WECHAT_WINDOW_TITLES = {"微信", "WeChat", "Weixin"}
V4_LIST_CLASS_NAMES = {"mmui::RecyclerListView", "mmui::XTableView"}
V4_LIST_CONTROL_TYPES = {"ListControl"}
V4_LIST_ITEM_CONTROL_TYPES = {"ListItemControl", "DataItemControl"}
SCAN_INTERVAL = 0.2  # 扫描间隔（秒）

# 通知声音设置
NOTIFICATION_SOUND = audio.Mail  # 添加这行
NOTIFICATION_MODE = "overlay"  # 可选: "overlay" 或 "system"
OVERLAY_DURATION_MS = 5000
OVERLAY_BASE_WIDTH = 336
OVERLAY_BASE_HEIGHT = 116
OVERLAY_RIGHT_MARGIN = 1
OVERLAY_BOTTOM_MARGIN = 1
WECHAT_GREEN = "#13A36A"
WECHAT_SURFACE = "#FAFAFA"
WECHAT_BORDER = "#E3E3E5"
WECHAT_SHADOW_SOFT = "#D9DDE3"
WECHAT_SHADOW_STRONG = "#C9CED6"
WECHAT_TEXT_PRIMARY = "#1F2329"
WECHAT_TEXT_SECONDARY = "#7F8792"
WECHAT_TEXT_BODY = "#49515A"
OVERLAY_LAYOUT_PRESETS = (
    {
        "name": "compact",
        "max_width": 1536,
        "max_height": 840,
        "width": 300,
        "height": 104,
        "stack_gap": 8,
        "message_max_chars": 72,
        "message_line_units": 42,
        "brand_font": 8,
        "time_font": 8,
        "title_font": 10,
        "message_font": 8,
    },
    {
        "name": "standard",
        "max_width": 1920,
        "max_height": 1080,
        "width": 336,
        "height": 116,
        "stack_gap": 10,
        "message_max_chars": 86,
        "message_line_units": 48,
        "brand_font": 9,
        "time_font": 8,
        "title_font": 11,
        "message_font": 9,
    },
    {
        "name": "large",
        "max_width": 2560,
        "max_height": 1440,
        "width": 360,
        "height": 124,
        "stack_gap": 12,
        "message_max_chars": 96,
        "message_line_units": 54,
        "brand_font": 10,
        "time_font": 9,
        "title_font": 12,
        "message_font": 10,
    },
    {
        "name": "ultra",
        "max_width": 100000,
        "max_height": 100000,
        "width": 392,
        "height": 136,
        "stack_gap": 14,
        "message_max_chars": 108,
        "message_line_units": 60,
        "brand_font": 10,
        "time_font": 9,
        "title_font": 12,
        "message_font": 10,
    },
)

# 正则表达式匹配消息内容
MESSAGE_REGEX = r"(.+?)(?:(\d+)条新消息)?(?:已置顶)?$"  # 匹配联系人名称和新消息数量
TIMESTAMP_REGEX = r"\d{1,2}/\d{1,2}/\d{1,2}|\d{1,2}:\d{2}"
SESSION_TIMESTAMP_REGEX = re.compile(
    r"^(\d{4}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}|\d{2}:\d{2}|昨天\s?\d{2}:\d{2}|星期\w|Yesterday\s?\d{2}:\d{2}|\w+day)$"
)
V4_UNREAD_PATTERNS = (
    re.compile(r"\[(\d+)条\]"),
    re.compile(r"\[(\d+)\]"),
)
V4_SESSION_LIST_TITLES = ("会话", "Chats", "對話")
V4_IGNORED_SENDERS = {"折叠的聊天", "公众号", "服务号"}
V4_PROBE_CACHE_TTL = 12
V4_SCAN_SETTLE_DELAY = 0.08
V4_MONITOR_INTERVAL = 0.25
V4_SESSION_LIST_CACHE_TTL = 20

# 添加全局变量
notified_messages = {}  # 消息历史，格式: {contact_name: (unread_count, preview)}
overlay_lock = threading.Lock()
active_overlay_windows = []
active_overlay_by_key = {}
overlay_queue = queue.Queue()
overlay_manager_ready = threading.Event()
overlay_manager_thread = None
overlay_logo_images = {}
last_v4_probe_state = None
last_v4_probe_at = 0.0
last_v4_session_list = None
last_v4_session_list_at = 0.0
v4_session_list_failure_streak = 0


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

def find_wechat_window():
    """查找微信主窗口"""
    wechat_window = None
    for window_name in WECHAT_WINDOW_NAMES:
        candidate = auto.WindowControl(searchDepth=1, Name=window_name)
        if candidate.Exists():
            wechat_window = candidate
            break

    if not wechat_window:
        logging.error("微信窗口未找到")
        return None
    
    # 设置 UIAutomation 配置，允许处理隐藏控件
    auto.SetGlobalSearchTimeout(0.5)  # 设置搜索超时
    auto.uiautomation.SEARCH_INTERVAL = 0.2  # 设置搜索间隔
    
    logging.info("找到微信窗口")
    return wechat_window

def get_file_version(file_path):
    """读取 Windows 可执行文件版本号"""
    try:
        info = win32api.GetFileVersionInfo(file_path, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return ".".join(
            str(part) for part in (
                win32api.HIWORD(ms),
                win32api.LOWORD(ms),
                win32api.HIWORD(ls),
                win32api.LOWORD(ls),
            )
        )
    except Exception as e:
        logging.debug(f"读取文件版本失败: {e}")
        return None

def get_wechat_process_info():
    """获取微信进程与版本信息"""
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        process_name = proc.info.get('name')
        if process_name not in WECHAT_PROCESS_NAMES:
            continue

        exe_path = proc.info.get('exe')
        version = get_file_version(exe_path) if exe_path else None
        return {
            "process": proc,
            "process_name": process_name,
            "exe_path": exe_path,
            "version": version,
        }
    return None

def get_wechat_process_ids():
    """获取所有微信相关进程 ID"""
    process_ids = []
    for proc in psutil.process_iter(['pid', 'name']):
        process_name = proc.info.get('name')
        if process_name in WECHAT_PROCESS_NAMES:
            process_ids.append(proc.info['pid'])
    return process_ids

def get_wechat_main_hwnd():
    """获取微信主窗口句柄"""
    cached_state = last_v4_probe_state or {}
    cached_main_window = cached_state.get("main_window") or {}
    cached_handle = cached_main_window.get("handle")
    if cached_handle:
        try:
            if win32gui.IsWindow(cached_handle):
                return cached_handle
        except Exception:
            pass

    matched_handles = []

    def callback(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            if class_name == "mmui::MainWindow":
                matched_handles.append(hwnd)
                return
            if title in WECHAT_WINDOW_NAMES and isinstance(class_name, str) and class_name.startswith("mmui::"):
                matched_handles.append(hwnd)
        except Exception:
            return

    win32gui.EnumWindows(callback, None)
    return matched_handles[0] if matched_handles else None

def focus_wechat_main_window():
    """将微信主窗口切到前台"""
    hwnd = get_wechat_main_hwnd()
    if not hwnd:
        logging.error("无法聚焦微信：未找到主窗口句柄")
        return None

    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        SW_RESTORE = 9
        SW_SHOW = 5
        HWND_TOPMOST = -1
        HWND_NOTOPMOST = -2
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040
        KEYEVENTF_KEYUP = 0x0002
        VK_MENU = 0x12

        foreground_hwnd = user32.GetForegroundWindow()
        current_thread_id = kernel32.GetCurrentThreadId()
        target_thread_id = user32.GetWindowThreadProcessId(hwnd, None)
        foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None) if foreground_hwnd else 0

        attached_foreground = False
        attached_target = False
        try:
            if foreground_thread_id and foreground_thread_id != current_thread_id:
                attached_foreground = bool(user32.AttachThreadInput(foreground_thread_id, current_thread_id, True))
            if target_thread_id and target_thread_id != current_thread_id:
                attached_target = bool(user32.AttachThreadInput(target_thread_id, current_thread_id, True))

            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.ShowWindow(hwnd, SW_SHOW)
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
            user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
            user32.BringWindowToTop(hwnd)

            # 利用一次 ALT 按键释放前台窗口限制
            win32api.keybd_event(VK_MENU, 0, 0, 0)
            win32api.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

            user32.SetForegroundWindow(hwnd)
            user32.SetActiveWindow(hwnd)
            user32.SetFocus(hwnd)
        finally:
            if attached_target:
                user32.AttachThreadInput(target_thread_id, current_thread_id, False)
            if attached_foreground:
                user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)

        logging.info("已将微信主窗口切到前台")
        return hwnd
    except Exception as e:
        logging.error(f"聚焦微信主窗口失败: {e}")
        return None

def open_wechat_session_from_notification(sender):
    """点击通知后尝试激活微信并定位到对应会话"""
    sender_name = (sender or "").strip()
    hwnd = focus_wechat_main_window()
    if not hwnd:
        return False

    if not sender_name:
        return True

    automation_id = f"session_item_{sender_name}"
    time.sleep(0.12)

    try:
        root_control = auto.ControlFromHandle(hwnd)
        session_item = root_control.ListItemControl(
            searchDepth=8,
            AutomationId=automation_id,
        )
        if session_item.Exists(0.8, 0.1):
            session_item.Click(simulateMove=False, waitTime=0)
            logging.info(f"已定位到微信会话: {sender_name}")
            return True
    except Exception as e:
        logging.debug(f"使用 uiautomation 定位会话失败: sender={sender_name}, error={e}")

    if Desktop is not None:
        try:
            window = Desktop(backend="uia").window(handle=hwnd)
            for item in window.descendants(control_type="ListItem"):
                try:
                    if item.element_info.automation_id == automation_id:
                        item.set_focus()
                        item.click_input()
                        logging.info(f"已通过 pywinauto 定位到微信会话: {sender_name}")
                        return True
                except Exception:
                    continue
        except Exception as e:
            logging.debug(f"使用 pywinauto 定位会话失败: sender={sender_name}, error={e}")

    logging.info(f"已打开微信主界面，但未能直接定位会话: {sender_name}")
    return True

def is_wechat_v4(version, process_name=None, exe_path=None):
    """判断是否为微信 4.x"""
    if process_name == "WeChatAppEx.exe":
        return True

    if exe_path and "xwechat" in exe_path.lower():
        return True

    if not version:
        return False
    try:
        return int(version.split('.')[0]) >= 4
    except (ValueError, IndexError):
        return False


def collect_window_handles(target_pids=None):
    handles = []
    pid_set = set(target_pids or [])

    def callback(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)

            if pid_set and pid not in pid_set:
                return

            title_match = title in WECHAT_WINDOW_TITLES
            class_match = isinstance(class_name, str) and class_name.startswith("mmui::")
            if title_match or class_match:
                handles.append(hwnd)
        except Exception:
            return

    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        return handles
    return handles


def control_snapshot(control, hwnd=0):
    native_handle = getattr(control, "NativeWindowHandle", 0) or 0
    return {
        "handle": hwnd or native_handle,
        "title": getattr(control, "Name", "") or "",
        "class_name": getattr(control, "ClassName", "") or "",
        "control_type": getattr(control, "ControlTypeName", "") or "",
    }


def is_main_window(control):
    class_name = getattr(control, "ClassName", "") or ""
    title = getattr(control, "Name", "") or ""
    return class_name == "mmui::MainWindow" or (
        class_name.startswith("mmui::") and title in WECHAT_WINDOW_TITLES
    )


def iter_descendants(root_control, max_depth=10, max_nodes=3000):
    queue_items = [(root_control, 0)]
    seen = set()
    visited = 0

    while queue_items and visited < max_nodes:
        control, depth = queue_items.pop(0)
        if depth >= max_depth:
            continue

        try:
            children = control.GetChildren()
        except Exception:
            continue

        for child in children:
            try:
                handle = getattr(child, "NativeWindowHandle", 0) or id(child)
                if handle in seen:
                    continue
                seen.add(handle)
                visited += 1
                yield child
                if visited >= max_nodes:
                    return
                queue_items.append((child, depth + 1))
            except Exception:
                continue


def is_list_control(control):
    class_name = getattr(control, "ClassName", "") or ""
    control_type = getattr(control, "ControlTypeName", "") or ""
    return class_name in V4_LIST_CLASS_NAMES or control_type in V4_LIST_CONTROL_TYPES


def is_list_item_control(control):
    automation_id = getattr(control, "AutomationId", "") or ""
    control_type = getattr(control, "ControlTypeName", "") or ""
    return automation_id.startswith("session_item_") or control_type in V4_LIST_ITEM_CONTROL_TYPES


def collect_list_items(list_control, limit=20):
    items = []
    try:
        children = list_control.GetChildren()
    except Exception:
        children = []

    for child in children:
        try:
            if not is_list_item_control(child):
                continue
            items.append(
                {
                    "automation_id": getattr(child, "AutomationId", "") or "",
                    "text": getattr(child, "Name", "") or "",
                    "class_name": getattr(child, "ClassName", "") or "",
                }
            )
            if len(items) >= limit:
                break
        except Exception:
            continue
    return items


def collect_controls_by_search(root_control, limit, factory_name, **search_kwargs):
    controls = []
    for found_index in range(1, limit + 1):
        try:
            factory = getattr(root_control, factory_name)
            control = factory(foundIndex=found_index, searchDepth=12, **search_kwargs)
            if not control.Exists(0.15, 0.03):
                break
            controls.append(control)
        except Exception:
            break
    return controls


def collect_session_items_from_descendants(root_control, limit=30):
    items = []
    for control in iter_descendants(root_control, max_depth=10, max_nodes=3000):
        try:
            if not is_list_item_control(control):
                continue

            automation_id = getattr(control, "AutomationId", "") or ""
            text = getattr(control, "Name", "") or ""
            class_name = getattr(control, "ClassName", "") or ""
            if not automation_id.startswith("session_item_") and not text:
                continue

            items.append(
                {
                    "automation_id": automation_id,
                    "text": text,
                    "class_name": class_name,
                }
            )
            if len(items) >= limit:
                break
        except Exception:
            continue
    return items


def collect_session_items_by_search(root_control, limit=30):
    items = []
    try:
        controls = collect_controls_by_search(
            root_control,
            limit=limit,
            factory_name="ListItemControl",
            Compare=lambda c, d: (getattr(c, "AutomationId", "") or "").startswith("session_item_"),
        )
    except Exception:
        controls = []

    for control in controls:
        try:
            items.append(
                {
                    "automation_id": getattr(control, "AutomationId", "") or "",
                    "text": getattr(control, "Name", "") or "",
                    "class_name": getattr(control, "ClassName", "") or "",
                }
            )
        except Exception:
            continue
    return items


def collect_lists_by_search(root_control, limit=10):
    lists = []
    try:
        controls = collect_controls_by_search(
            root_control,
            limit=limit,
            factory_name="Control",
            Compare=lambda c, d: is_list_control(c),
        )
    except Exception:
        controls = []

    for control in controls:
        try:
            items = collect_list_items(control)
            lists.append(
                {
                    "title": getattr(control, "Name", "") or "",
                    "class_name": getattr(control, "ClassName", "") or "",
                    "item_count": len(items),
                    "items": items,
                }
            )
        except Exception:
            continue
    return lists


def collect_wechat_state(target_pids=None):
    candidates = []
    state = {
        "windows": [],
        "main_window": None,
        "lists": [],
    }

    for hwnd in collect_window_handles(target_pids):
        try:
            window = auto.ControlFromHandle(hwnd)
            if not window:
                continue
            state["windows"].append(control_snapshot(window, hwnd=hwnd))
            candidates.append((hwnd, window))
        except Exception:
            continue

    main_window = None
    main_hwnd = 0
    for hwnd, window in candidates:
        try:
            if is_main_window(window):
                main_window = window
                main_hwnd = hwnd
                break
        except Exception:
            continue

    if main_window is None:
        for hwnd, window in candidates:
            try:
                class_name = getattr(window, "ClassName", "") or ""
                if class_name.startswith("mmui::"):
                    main_window = window
                    main_hwnd = hwnd
                    break
            except Exception:
                continue

    if main_window is None:
        return state

    state["main_window"] = control_snapshot(main_window, hwnd=main_hwnd)

    for control in iter_descendants(main_window, max_depth=10, max_nodes=3000):
        try:
            if not is_list_control(control):
                continue
            items = collect_list_items(control)
            state["lists"].append(
                {
                    "title": getattr(control, "Name", "") or "",
                    "class_name": getattr(control, "ClassName", "") or "",
                    "item_count": len(items),
                    "items": items,
                }
            )
        except Exception:
            continue

    if not state["lists"]:
        state["lists"].extend(collect_lists_by_search(main_window))

    has_session_list = any(
        any((item.get("automation_id") or "").startswith("session_item_") for item in list_state.get("items", []))
        for list_state in state["lists"]
    )
    if not has_session_list:
        synthetic_items = collect_session_items_by_search(main_window)
        if not synthetic_items:
            synthetic_items = collect_session_items_from_descendants(main_window)
        if synthetic_items:
            state["lists"].append(
                {
                    "title": "会话",
                    "class_name": "synthetic::session_list",
                    "item_count": len(synthetic_items),
                    "items": synthetic_items,
                }
            )

    return state

def find_wechat_window_v4():
    """查找微信 4.x 主窗口"""
    logging.debug("开始查找微信 4.x 主窗口")

    target_pids = get_wechat_process_ids()
    probe = probe_wechat_v4_state(target_pids)
    if probe is None:
        logging.error("微信 4.x 探针执行失败")
        return None

    logging.debug(
        "微信 4.x 探针摘要: windows=%s, main_window=%s, lists=%s, details=%s"
        % (
            len(probe.get("windows", [])),
            bool(probe.get("main_window")),
            len(probe.get("lists", [])),
            [
                "%s|%s" % (item.get("title", ""), item.get("class_name", ""))
                for item in probe.get("windows", [])[:5]
            ],
        )
    )

    main_window = probe.get("main_window")
    if main_window:
        logging.debug(f"找到微信 4.x 主窗口: {main_window.get('title', '')}")
        return probe

    logging.error("微信 4.x 主窗口未找到，请确认微信主界面处于打开且可见状态，而不是最小化到托盘。")
    return None

def probe_wechat_v4_state(target_pids=None):
    """读取微信 4.x 窗口和会话信息"""
    global last_v4_probe_state, last_v4_probe_at

    try:
        state = collect_wechat_state(target_pids)
    except Exception as e:
        logging.error(f"微信 4.x 探针执行失败: {e}")
        state = None

    if state and (state.get("windows") or state.get("main_window")):
        last_v4_probe_state = state
        last_v4_probe_at = time.time()
        return state

    if target_pids:
        logging.debug("PID 定向探针未找到窗口，回退到全局窗口探针")
        try:
            fallback_state = collect_wechat_state(None)
        except Exception as e:
            logging.error(f"微信 4.x 全局探针执行失败: {e}")
            fallback_state = None
        if fallback_state and (fallback_state.get("windows") or fallback_state.get("main_window")):
            last_v4_probe_state = fallback_state
            last_v4_probe_at = time.time()
            return fallback_state
        state = fallback_state if fallback_state is not None else state

    if last_v4_probe_state and (time.time() - last_v4_probe_at) <= V4_PROBE_CACHE_TTL:
        logging.debug("微信 4.x 探针本轮未命中窗口，回退到最近一次成功的探针结果")
        return last_v4_probe_state

    return state
def get_v4_chat_button(main_window):
    """获取微信 4.x 左侧聊天按钮"""
    if isinstance(main_window, dict):
        return None
    try:
        button = main_window.child_window(control_type="Button", found_index=0)
        if button.exists(timeout=1):
            return button
    except Exception as e:
        logging.debug(f"获取微信按钮失败: {e}")
    return None

def get_live_v4_session_list():
    """在主进程中直接读取微信 4.x 会话列表，作为探针失败时的兜底"""
    hwnd = get_wechat_main_hwnd()
    if not hwnd:
        logging.debug("主进程兜底未找到微信主窗口句柄")
        return None

    if Desktop is not None:
        try:
            window = Desktop(backend="uia").window(handle=hwnd)
            pywinauto_lists = []

            for control in window.descendants(control_type="List"):
                try:
                    control_title = control.window_text()
                    control_class_name = control.class_name()
                    items = []
                    for item in control.children(control_type="ListItem"):
                        try:
                            items.append(
                                {
                                    "automation_id": item.automation_id(),
                                    "text": item.window_text(),
                                    "class_name": item.class_name(),
                                }
                            )
                        except Exception:
                            continue

                    pywinauto_lists.append(
                        {
                            "title": control_title,
                            "class_name": control_class_name,
                            "item_count": len(items),
                            "items": items,
                        }
                    )
                except Exception:
                    continue

            for list_state in pywinauto_lists:
                if any((item.get("automation_id") or "").startswith("session_item_") for item in list_state.get("items", [])):
                    logging.debug(f"主进程 pywinauto 兜底找到会话项数量: {len(list_state.get('items', []))}")
                    return list_state

            direct_items = []
            for item in window.descendants(control_type="ListItem"):
                try:
                    automation_id = item.automation_id()
                    if not automation_id.startswith("session_item_"):
                        continue
                    direct_items.append(
                        {
                            "automation_id": automation_id,
                            "text": item.window_text(),
                            "class_name": item.class_name(),
                        }
                    )
                except Exception:
                    continue

            if direct_items:
                logging.debug(f"主进程 pywinauto 直接扫描找到会话项数量: {len(direct_items)}")
                return {
                    "title": "会话",
                    "class_name": "pywinauto::session_list",
                    "item_count": len(direct_items),
                    "items": direct_items,
                }
        except Exception as e:
            logging.debug(f"主进程 pywinauto 兜底失败: {e}")

    try:
        root_control = auto.ControlFromHandle(hwnd)
    except Exception as e:
        logging.debug(f"创建微信主窗口控件失败: {e}")
        return None

    def iter_controls(root, max_depth=10, max_nodes=3000):
        queue = [(root, 0)]
        visited = 0
        while queue and visited < max_nodes:
            control, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            try:
                children = control.GetChildren()
            except Exception:
                continue

            for child in children:
                visited += 1
                yield child
                if visited >= max_nodes:
                    return
                queue.append((child, depth + 1))

    items = []
    visited_controls = 0
    for control in iter_controls(root_control, max_depth=10, max_nodes=3000):
        try:
            visited_controls += 1
            automation_id = getattr(control, "AutomationId", "") or ""
            if not automation_id.startswith("session_item_"):
                continue

            text = getattr(control, "Name", "") or ""
            class_name = getattr(control, "ClassName", "") or ""
            items.append(
                {
                    "automation_id": automation_id,
                    "text": text,
                    "class_name": class_name,
                }
            )
            if len(items) >= 40:
                break
        except Exception:
            continue

    if not items:
        logging.debug(f"主进程兜底未找到任何 session_item_ 会话项，遍历控件数: {visited_controls}")
        return None

    logging.debug(f"主进程兜底找到会话项数量: {len(items)}")

    return {
        "title": "会话",
        "class_name": "live::session_list",
        "item_count": len(items),
        "items": items,
    }


def cache_v4_session_list(session_list):
    global last_v4_session_list, last_v4_session_list_at
    if not session_list or not session_list.get("items"):
        return
    last_v4_session_list = {
        "title": session_list.get("title", "会话"),
        "class_name": session_list.get("class_name", ""),
        "item_count": len(session_list.get("items", [])),
        "items": [dict(item) for item in session_list.get("items", [])],
    }
    last_v4_session_list_at = time.time()


def get_cached_v4_session_list():
    if last_v4_session_list and (time.time() - last_v4_session_list_at) <= V4_SESSION_LIST_CACHE_TTL:
        return {
            "title": last_v4_session_list.get("title", "会话"),
            "class_name": last_v4_session_list.get("class_name", ""),
            "item_count": len(last_v4_session_list.get("items", [])),
            "items": [dict(item) for item in last_v4_session_list.get("items", [])],
        }
    return None

def get_v4_session_list(main_window, allow_refresh=True):
    """获取微信 4.x 会话列表"""
    for list_state in main_window.get("lists", []):
        title = list_state.get("title", "")
        class_name = list_state.get("class_name", "")
        if title in V4_SESSION_LIST_TITLES or class_name == "mmui::XTableView":
            logging.debug(f"找到微信 4.x 会话列表: {title}")
            cache_v4_session_list(list_state)
            return list_state

    for list_state in main_window.get("lists", []):
        for item in list_state.get("items", []):
            automation_id = item.get("automation_id", "")
            if automation_id.startswith("session_item_"):
                logging.debug(f"找到微信 4.x 会话列表: {list_state.get('title', '')}")
                cache_v4_session_list(list_state)
                return list_state

    live_session_list = get_live_v4_session_list()
    if live_session_list is not None:
        logging.debug(f"找到微信 4.x 会话列表: {live_session_list.get('title', '')}")
        cache_v4_session_list(live_session_list)
        return live_session_list

    if allow_refresh:
        logging.debug("当前未命中微信 4.x 会话列表，执行一次强制重探测")
        refreshed_probe = probe_wechat_v4_state(get_wechat_process_ids())
        if refreshed_probe:
            refreshed_session_list = get_v4_session_list(refreshed_probe, allow_refresh=False)
            if refreshed_session_list is not None:
                return refreshed_session_list

    cached_session_list = get_cached_v4_session_list()
    if cached_session_list is not None:
        logging.debug("本轮未实时获取到微信 4.x 会话列表，回退到最近一次成功快照")
        return cached_session_list
    return None

def get_v4_total_unread_count(chats_button):
    """读取微信 4.x 侧边栏上的总未读数"""
    if chats_button is None:
        return 0

    try:
        element = chats_button.element_info.element
        for property_id in (30159, 30007):
            value = element.GetCurrentPropertyValue(property_id)
            if value:
                match = re.search(r"\d+", str(value))
                if match:
                    return int(match.group(0))
    except Exception as e:
        logging.debug(f"读取总未读数失败: {e}")

    return 0

def get_v4_visible_session_items(session_list):
    """获取当前可见的微信 4.x 会话项"""
    try:
        items = session_list.get("items", [])
        logging.debug(f"当前可见会话项数量: {len(items)}")
        return items
    except Exception as e:
        logging.error(f"读取当前可见会话项失败: {e}")
        return []

def should_skip_v4_session(sender, item_text):
    """判断微信 4.x 会话是否应跳过通知"""
    if sender in V4_IGNORED_SENDERS:
        return True
    if "消息免打扰" in item_text or "Mute notifications" in item_text:
        return True
    return False

def extract_v4_unread_count(text):
    """从微信 4.x 会话项文本中提取未读数"""
    for pattern in V4_UNREAD_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return 0

def extract_v4_sender(item):
    """获取微信 4.x 会话项发送方名称"""
    try:
        automation_id = item.get("automation_id", "")
        if automation_id and automation_id.startswith("session_item_"):
            return automation_id.replace("session_item_", "", 1)
    except Exception:
        pass

    text = item.get("text", "")
    for line in (line.strip() for line in text.splitlines()):
        if not line:
            continue
        if extract_v4_unread_count(line):
            continue
        if line == "已置顶":
            continue
        if SESSION_TIMESTAMP_REGEX.match(line):
            continue
        return line
    return ""

def extract_v4_preview(item_text, sender):
    """获取微信 4.x 会话项中的消息预览文本"""
    previews = []
    unread_count = extract_v4_unread_count(item_text)
    for raw_line in item_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == sender or line == "已置顶":
            continue
        if line in {"消息免打扰", "Mute notifications"}:
            continue
        if SESSION_TIMESTAMP_REGEX.match(line):
            continue

        # 微信 4.x 常把未读数和预览文案放在同一行，例如:
        # [3条] 张三: 测试消息
        line = re.sub(r"^\[\d+(?:条)?\]\s*", "", line).strip()
        if not line:
            continue
        if re.fullmatch(r"\d+", line):
            # 纯数字也可能是真实消息内容；只有当它更像未读角标本身时才跳过
            if unread_count and line == str(unread_count):
                continue
        previews.append(line)

    if not previews:
        return ""
    return previews[-1]

def is_displayable_v4_preview(preview):
    """判断会话摘要是否适合直接展示到通知里"""
    text = (preview or "").strip()
    if not text:
        return False

    invalid_tokens = {
        "[草稿]",
        "草稿",
        "[Draft]",
        "Draft",
    }
    if text in invalid_tokens:
        return False

    if re.fullmatch(r"[~`|]+", text):
        return False

    return True

def is_reusable_v4_preview(preview):
    """判断会话摘要是否适合写入缓存并在后续回退复用"""
    text = (preview or "").strip()
    if not is_displayable_v4_preview(text):
        return False

    # 单个测试符号、草稿态标记等不适合污染缓存，否则后续正文取不到时会一直回退成它。
    if re.fullmatch(r"[\^]+", text):
        return False

    return True

def normalize_v4_preview_text(preview, class_name=""):
    """规范化微信 4.x 的消息预览文本"""
    text = (preview or "").strip()
    item_class = (class_name or "").lower()

    if not is_displayable_v4_preview(text):
        return ""

    if "video" in item_class or text in {"视频", "[视频]"}:
        return "[视频]"

    voice_duration_match = re.fullmatch(r"(\d+\s*['\"]{1,2})", text)
    if "voice" in item_class or "audio" in item_class or voice_duration_match:
        duration_match = re.search(r"(\d+\s*['\"]{1,2})", text)
        if duration_match:
            duration = duration_match.group(1).replace('"', "''")
            return f"[语音] {duration}"
        if text:
            return f"[语音] {text}"
        return "[语音]"

    if text == "图片" or "refer" in item_class or "image" in item_class:
        return "[图片]"

    return text

def strip_sender_prefix(preview, sender):
    """去掉会话预览里重复的发送方前缀"""
    text = (preview or "").strip()
    if not text:
        return ""

    normalized_sender = sender.strip()
    prefixes = [
        f"{normalized_sender}:",
        f"{normalized_sender}：",
    ]
    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return text

def format_v4_notification_content(sender, count, preview):
    """拼装微信 4.x 的通知正文"""
    cleaned_preview = preview if is_displayable_v4_preview(preview) else ""
    body = strip_sender_prefix(cleaned_preview, sender) or cleaned_preview or "[新消息]"
    return f"[{count}条] {sender}：{body}"

def scan_wechat_messages_v4(main_window, delay=V4_SCAN_SETTLE_DELAY):
    """扫描微信 4.x 会话列表中的未读消息"""
    logging.debug("开始扫描微信 4.x 会话列表")
    chats_button = get_v4_chat_button(main_window)
    if chats_button is None:
        logging.debug("未找到微信 4.x 左侧聊天按钮，继续直接扫描会话列表")

    session_list = get_v4_session_list(main_window)
    if session_list is None:
        raise RuntimeError("未找到微信 4.x 会话列表")

    total_unread = get_v4_total_unread_count(chats_button)
    logging.debug(f"微信 4.x 侧边栏总未读数: {total_unread}")
    unread_sessions = {}
    time.sleep(delay)
    list_items = get_v4_visible_session_items(session_list)
    logging.debug(f"本轮扫描到会话项数量: {len(list_items)}")

    for item in list_items:
        text = item.get("text", "")
        count = extract_v4_unread_count(text)
        if count <= 0:
            continue

        sender = extract_v4_sender(item)
        if not sender:
            logging.debug(f"跳过无法识别发送方的会话项: {text}")
            continue
        if should_skip_v4_session(sender, text):
            logging.debug(f"按规则跳过会话: sender={sender}")
            continue

        preview = normalize_v4_preview_text(extract_v4_preview(text, sender))
        if not preview:
            logging.debug(f"会话摘要为空或已过滤: sender={sender}, raw={text!r}")
        existing = unread_sessions.get(sender)
        if existing is None or count >= existing["count"]:
            unread_sessions[sender] = {
                "count": count,
                "preview": preview,
            }
            logging.debug(f"检测到未读会话: sender={sender}, count={count}, preview={preview}")

    logging.debug(f"本轮扫描完成，未读会话数: {len(unread_sessions)}")
    return unread_sessions

def monitor_wechat_messages_v4():
    """监控微信 4.x 消息"""
    global v4_session_list_failure_streak
    logging.info("开始监控微信 4.x 消息...")
    loop_count = 0
    while True:
        try:
            loop_count += 1
            logging.debug(f"微信 4.x 监控轮次: {loop_count}")
            main_window = find_wechat_window_v4()
            if not main_window:
                logging.debug("当前未找到微信 4.x 主窗口，2 秒后重试")
                time.sleep(2)
                continue

            unread_sessions = scan_wechat_messages_v4(main_window)
            v4_session_list_failure_streak = 0
            current_senders = set(unread_sessions.keys())

            for sender, payload in unread_sessions.items():
                count = payload["count"]
                preview = payload["preview"]
                old_count, old_preview = notified_messages.get(sender, (0, ""))
                if count == old_count:
                    # 未读数没变时，不要用新的摘要覆盖历史摘要。
                    # 微信会在某些场景把摘要刷新成当前打开会话里“我自己发出”的内容，
                    # 继续覆盖缓存会导致后续未读增长时拼出错误通知正文。
                    if not old_preview and is_reusable_v4_preview(preview):
                        notified_messages[sender] = (count, preview)
                    elif is_reusable_v4_preview(old_preview):
                        unread_sessions[sender]["preview"] = old_preview
                    continue

                if not is_displayable_v4_preview(preview) and is_reusable_v4_preview(old_preview) and count > old_count:
                    preview = old_preview
                    unread_sessions[sender]["preview"] = preview

                if count < old_count:
                    next_preview = preview if is_reusable_v4_preview(preview) else old_preview
                    notified_messages[sender] = (count, next_preview if is_reusable_v4_preview(next_preview) else "")
                    continue

                message = f"{sender}\n{format_v4_notification_content(sender, count, preview)}"

                send_notification("微信新消息", message)
                logging.info(f"发现微信 4.x 新消息: {message}")
                notified_messages[sender] = (count, preview if is_reusable_v4_preview(preview) else "")

            for sender in list(notified_messages.keys()):
                if sender not in current_senders:
                    logging.debug(f"会话未读已清除: {sender}")
                    notified_messages.pop(sender, None)
        except Exception as e:
            if "未找到微信 4.x 会话列表" in str(e):
                v4_session_list_failure_streak += 1
                if v4_session_list_failure_streak == 1 or v4_session_list_failure_streak % 10 == 0:
                    logging.warning(
                        "监控微信 4.x 失败: %s（连续 %s 次）"
                        % (e, v4_session_list_failure_streak)
                    )
                else:
                    logging.debug(
                        "监控微信 4.x 失败: %s（连续 %s 次）"
                        % (e, v4_session_list_failure_streak)
                    )
            else:
                logging.error(f"监控微信 4.x 失败: {e}")

        time.sleep(V4_MONITOR_INTERVAL)

def monitor_wechat_messages():
    """监控微信消息"""
    pythoncom.CoInitialize()
    
    chat_list = find_wechat_window()
    if not chat_list:
        return

    logging.info("开始监控微信消息...")
    try:
        while True:
            try:
                # 递归扫描所有控件，包括隐藏的
                def scan_controls(control):
                    try:
                        if control.Name and "条新消息" in control.Name:
                            message = extract_message_content(control)
                            if message:
                                send_notification("微信新消息", message)
                                logging.info(f"发现新消息: {message}")
                        
                        # 获取所有子控件，包括隐藏的
                        children = control.GetChildren()
                        for child in children:
                            scan_controls(child)
                    except Exception as e:
                        logging.debug(f"扫描控件失败: {e}")
                
                scan_controls(chat_list)
                        
            except Exception as e:
                logging.error(f"监控失败: {e}")
            time.sleep(SCAN_INTERVAL)
    finally:
        pythoncom.CoUninitialize()

def is_notification_mode(mode):
    return NOTIFICATION_MODE.lower() == mode

def get_overlay_text_units(text):
    units = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ("W", "F"):
            units += 2
        else:
            units += 1
    return units


def slice_overlay_text_by_units(text, max_units):
    current_units = 0
    chars = []
    for char in text:
        char_units = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        if current_units + char_units > max_units:
            break
        chars.append(char)
        current_units += char_units
    sliced = "".join(chars)
    return sliced, text[len(sliced):]


def truncate_overlay_text_with_ellipsis(text, max_units):
    ellipsis = "..."
    if get_overlay_text_units(text) <= max_units:
        return text
    trimmed, _ = slice_overlay_text_by_units(text, max(0, max_units - len(ellipsis)))
    return trimmed.rstrip() + ellipsis


def format_overlay_message(message, max_chars=86, max_lines=2, line_units=48):
    compact = re.sub(r"\s+", " ", " ".join(part.strip() for part in message.splitlines() if part.strip())).strip()
    if not compact:
        return ""

    if len(compact) > max_chars:
        compact = compact[:max_chars]

    lines = []
    remaining = compact
    for line_index in range(max_lines):
        if not remaining:
            break
        current_line, leftover = slice_overlay_text_by_units(remaining, line_units)
        current_line = current_line.rstrip()
        remaining = leftover.lstrip()
        if line_index == max_lines - 1 and remaining:
            current_line = truncate_overlay_text_with_ellipsis(current_line + remaining, line_units)
            remaining = ""
        lines.append(current_line)

    if remaining and lines:
        lines[-1] = truncate_overlay_text_with_ellipsis(lines[-1] + remaining, line_units)

    return "\n".join(lines[:max_lines])


def get_overlay_layout():
    """根据常见分辨率档位返回浮层布局参数"""
    left, top, right, bottom = get_overlay_work_area()
    work_width = max(0, right - left)
    work_height = max(0, bottom - top)
    for preset in OVERLAY_LAYOUT_PRESETS:
        if work_width <= preset["max_width"] or work_height <= preset["max_height"]:
            layout = dict(preset)
            layout["work_left"] = left
            layout["work_top"] = top
            layout["work_right"] = right
            layout["work_bottom"] = bottom
            return layout

    layout = dict(OVERLAY_LAYOUT_PRESETS[-1])
    layout["work_left"] = left
    layout["work_top"] = top
    layout["work_right"] = right
    layout["work_bottom"] = bottom
    return layout


def scale_overlay_x(layout, value):
    return int(round(value * layout["width"] / OVERLAY_BASE_WIDTH))


def scale_overlay_y(layout, value):
    return int(round(value * layout["height"] / OVERLAY_BASE_HEIGHT))


def get_overlay_message_line_units(layout):
    """给正文预留右侧留白，避免文字贴边"""
    return max(18, layout["message_line_units"] - 6)


def get_overlay_logo_image(layout):
    """加载并缓存通知浮层使用的微信图标"""
    cache_key = layout["name"]
    cached = overlay_logo_images.get(cache_key)
    if cached is not None:
        return cached

    try:
        image = tk.PhotoImage(data=WX_LOGO_BASE64)
        target_size = max(12, scale_overlay_x(layout, 14))
        width = max(1, image.width())
        height = max(1, image.height())
        scale = max(width / target_size, height / target_size, 1)
        subsample = max(1, int(round(scale)))
        if subsample > 1:
            image = image.subsample(subsample, subsample)
        overlay_logo_images[cache_key] = image
        return image
    except Exception as e:
        logging.debug(f"加载浮层微信图标失败: {e}")
        overlay_logo_images[cache_key] = None
        return None


def get_notification_icon_path():
    """为系统通知提供一个临时图标文件路径"""
    global EMBEDDED_ICON_PATH
    if EMBEDDED_ICON_PATH and os.path.exists(EMBEDDED_ICON_PATH):
        return EMBEDDED_ICON_PATH

    try:
        icon_dir = os.path.join(tempfile.gettempdir(), "wechat-toast")
        os.makedirs(icon_dir, exist_ok=True)
        icon_path = os.path.join(icon_dir, "wx_logo.png")
        if not os.path.exists(icon_path):
            with open(icon_path, "wb") as icon_file:
                icon_file.write(base64.b64decode(WX_LOGO_BASE64))
        EMBEDDED_ICON_PATH = icon_path
        return EMBEDDED_ICON_PATH
    except Exception as e:
        logging.error(f"写出临时通知图标失败: {e}")
        return None


def split_overlay_message_content(message):
    compact = re.sub(r"\s+", " ", " ".join(part.strip() for part in str(message).splitlines() if part.strip())).strip()
    match = re.match(r"^(\[\d+条\])\s*(.*)$", compact)
    if match:
        return match.group(1), match.group(2).strip()
    return "", compact


def format_overlay_message_parts(message, layout):
    prefix_text, body_text = split_overlay_message_content(message)
    reserved_units = get_overlay_text_units(prefix_text) + (2 if prefix_text else 0)
    body_units = max(12, get_overlay_message_line_units(layout) - reserved_units)
    return prefix_text, format_overlay_message(
        body_text,
        layout["message_max_chars"],
        max_lines=1,
        line_units=body_units,
    )


def get_overlay_work_area():
    """获取排除任务栏后的桌面可用区域"""
    rect = RECT()
    SPI_GETWORKAREA = 0x0030
    try:
        success = ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
        if success:
            return rect.left, rect.top, rect.right, rect.bottom
    except Exception as e:
        logging.debug(f"读取桌面工作区失败，回退到全屏尺寸: {e}")

    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    return 0, 0, screen_width, screen_height


def get_overlay_geometry(stack_index, layout=None):
    """根据工作区计算浮层位置，确保不覆盖任务栏"""
    layout = layout or get_overlay_layout()
    right = layout["work_right"]
    bottom = layout["work_bottom"]
    x = right - layout["width"] - OVERLAY_RIGHT_MARGIN
    y = bottom - layout["height"] - OVERLAY_BOTTOM_MARGIN - stack_index * (layout["height"] + layout["stack_gap"])
    return x, y


def apply_overlay_geometry(window, stack_index, layout=None):
    layout = layout or getattr(window, "_overlay_layout", None) or get_overlay_layout()
    x, y = get_overlay_geometry(stack_index, layout)
    window.geometry(f"{layout['width']}x{layout['height']}+{x}+{y}")

def handle_overlay_click(action_target=None):
    """处理通知点击行为"""
    try:
        logging.info(f"收到通知点击: target={action_target}")
        open_wechat_session_from_notification(action_target)
    except Exception as e:
        logging.error(f"处理通知点击失败: {e}")

def remove_overlay_window(window):
    with overlay_lock:
        overlay_key = getattr(window, "_overlay_key", None)
        if overlay_key and active_overlay_by_key.get(overlay_key) is window:
            active_overlay_by_key.pop(overlay_key, None)
        if window in active_overlay_windows:
            active_overlay_windows.remove(window)
        for index, existing in enumerate(active_overlay_windows):
            try:
                apply_overlay_geometry(existing, index)
            except Exception:
                continue

def reset_overlay_timer(window, duration_ms):
    after_id = getattr(window, "_dismiss_after_id", None)
    if after_id:
        try:
            window.after_cancel(after_id)
        except Exception:
            pass
    window._dismiss_after_id = window.after(duration_ms, lambda: destroy_overlay_window(window))

def destroy_overlay_window(window):
    remove_overlay_window(window)
    try:
        after_id = getattr(window, "_dismiss_after_id", None)
        if after_id:
            try:
                window.after_cancel(after_id)
            except Exception:
                pass
            window._dismiss_after_id = None
        window.destroy()
    except Exception:
        pass

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

def update_overlay_window(window, title, message, duration_ms):
    try:
        canvas = getattr(window, "_canvas", None)
        title_item = getattr(window, "_title_item", None)
        message_prefix_item = getattr(window, "_message_prefix_item", None)
        message_item = getattr(window, "_message_item", None)
        time_item = getattr(window, "_time_item", None)
        message_x = getattr(window, "_message_x", 0)
        message_y = getattr(window, "_message_y", 0)
        message_gap = getattr(window, "_message_gap", 0)
        layout = getattr(window, "_overlay_layout", None) or get_overlay_layout()
        if (
            canvas is None
            or title_item is None
            or message_prefix_item is None
            or message_item is None
            or time_item is None
        ):
            return False

        prefix_text, body_text = format_overlay_message_parts(message, layout)
        canvas.itemconfigure(title_item, text=title)
        canvas.itemconfigure(message_prefix_item, text=prefix_text)
        prefix_bbox = canvas.bbox(message_prefix_item)
        body_x = message_x if not prefix_bbox or not prefix_text else prefix_bbox[2] + message_gap
        canvas.coords(message_item, body_x, message_y)
        canvas.itemconfigure(message_item, text=body_text)
        canvas.itemconfigure(time_item, text=datetime.now().strftime("%H:%M"))
        window.lift()
        window.update_idletasks()
        reset_overlay_timer(window, duration_ms)
        logging.info(f"本地浮层已刷新: {title} | {message}")
        return True
    except Exception as e:
        logging.error(f"刷新本地浮层失败: {e}")
        return False

def create_overlay_window(root, title, message, duration_ms, overlay_key=None):
    transparent_color = "#F000F0"
    action_target = overlay_key or title
    layout = get_overlay_layout()
    outer_inset = max(5, scale_overlay_x(layout, 5))
    card_radius = max(18, scale_overlay_x(layout, 24))
    shadow_offset_soft = max(1, scale_overlay_x(layout, 1))
    shadow_offset_strong = max(2, scale_overlay_x(layout, 2))
    content_left = scale_overlay_x(layout, 30)
    header_left = content_left + scale_overlay_x(layout, 8)
    logo_gap = max(6, scale_overlay_x(layout, 6))
    brand_x = header_left
    header_y = scale_overlay_y(layout, 26)
    time_x = layout["width"] - scale_overlay_x(layout, 30)
    title_x = content_left
    title_y = scale_overlay_y(layout, 54)
    time_y = title_y
    message_x = content_left
    message_y = scale_overlay_y(layout, 84)
    message_gap = max(6, scale_overlay_x(layout, 6))

    existing_window = None
    if overlay_key:
        with overlay_lock:
            existing_window = active_overlay_by_key.get(overlay_key)
    if existing_window is not None:
        if update_overlay_window(existing_window, title, message, duration_ms):
            return
        destroy_overlay_window(existing_window)

    window = tk.Toplevel(root)
    window.overrideredirect(True)
    window.attributes("-topmost", True)
    window.configure(bg=transparent_color)
    try:
        window.wm_attributes("-transparentcolor", transparent_color)
    except Exception:
        pass

    with overlay_lock:
        stack_index = len(active_overlay_windows)
    apply_overlay_geometry(window, stack_index, layout)
    window.configure(cursor="hand2")

    canvas = tk.Canvas(
        window,
        width=layout["width"],
        height=layout["height"],
        bg=transparent_color,
        bd=0,
        highlightthickness=0,
    )
    canvas.pack(fill="both", expand=True)
    canvas.configure(cursor="hand2")

    draw_rounded_rect(
        canvas,
        outer_inset + shadow_offset_strong,
        outer_inset + shadow_offset_strong,
        layout["width"] - outer_inset + shadow_offset_soft,
        layout["height"] - outer_inset + shadow_offset_soft,
        card_radius,
        fill=WECHAT_SHADOW_SOFT,
        outline="",
    )
    draw_rounded_rect(
        canvas,
        outer_inset + shadow_offset_soft,
        outer_inset + shadow_offset_soft,
        layout["width"] - outer_inset,
        layout["height"] - outer_inset,
        max(16, card_radius - 1),
        fill=WECHAT_SHADOW_STRONG,
        outline="",
    )
    draw_rounded_rect(
        canvas,
        outer_inset,
        outer_inset,
        layout["width"] - outer_inset,
        layout["height"] - outer_inset,
        card_radius,
        fill=WECHAT_SURFACE,
        outline=WECHAT_BORDER,
    )

    logo_image = get_overlay_logo_image(layout)
    if logo_image is not None:
        logo_center_x = header_left - logo_gap - (logo_image.width() / 2)
        canvas.create_image(
            logo_center_x,
            header_y,
            image=logo_image,
            anchor="center",
        )
    else:
        dot_size = max(8, scale_overlay_x(layout, 10))
        dot_left = header_left - dot_size - logo_gap
        dot_top = scale_overlay_y(layout, 21)
        canvas.create_oval(
            dot_left,
            dot_top,
            dot_left + dot_size,
            dot_top + dot_size,
            fill=WECHAT_GREEN,
            outline="",
        )
    canvas.create_text(
        brand_x,
        header_y,
        text="微信",
        anchor="w",
        font=("Microsoft YaHei UI", layout["brand_font"], "bold"),
        fill=WECHAT_GREEN,
    )
    time_item = canvas.create_text(
        time_x,
        time_y,
        text=datetime.now().strftime("%H:%M"),
        anchor="e",
        font=("Microsoft YaHei UI", layout["time_font"]),
        fill=WECHAT_TEXT_SECONDARY,
    )

    title_item = canvas.create_text(
        title_x,
        title_y,
        text=title,
        anchor="w",
        font=("Microsoft YaHei UI", layout["title_font"], "bold"),
        fill=WECHAT_TEXT_PRIMARY,
    )

    prefix_text, body_text = format_overlay_message_parts(message, layout)
    message_prefix_item = canvas.create_text(
        message_x,
        message_y,
        text=prefix_text,
        anchor="w",
        font=("Microsoft YaHei UI", layout["message_font"]),
        fill=WECHAT_TEXT_SECONDARY,
    )
    prefix_bbox = canvas.bbox(message_prefix_item)
    body_x = message_x if not prefix_bbox or not prefix_text else prefix_bbox[2] + message_gap
    message_item = canvas.create_text(
        body_x,
        message_y,
        text=body_text,
        anchor="w",
        font=("Microsoft YaHei UI", layout["message_font"]),
        fill=WECHAT_TEXT_BODY,
    )

    def on_click(_event=None):
        threading.Thread(
            target=handle_overlay_click,
            args=(action_target,),
            daemon=True,
        ).start()
        destroy_overlay_window(window)

    window.bind("<Button-1>", on_click)
    canvas.bind("<Button-1>", on_click)

    with overlay_lock:
        window._overlay_key = overlay_key
        window._canvas = canvas
        window._time_item = time_item
        window._title_item = title_item
        window._message_prefix_item = message_prefix_item
        window._message_item = message_item
        window._message_x = message_x
        window._message_y = message_y
        window._message_gap = message_gap
        window._overlay_action_target = action_target
        window._overlay_layout = layout
        active_overlay_windows.append(window)
        if overlay_key:
            active_overlay_by_key[overlay_key] = window

    reset_overlay_timer(window, duration_ms)

def ensure_overlay_manager():
    global overlay_manager_thread

    if overlay_manager_thread and overlay_manager_thread.is_alive():
        return

    overlay_manager_ready.clear()

    def _run():
        try:
            root = tk.Tk()
            root.withdraw()

            def pump_queue():
                try:
                    pending = {}
                    while True:
                        title, message, duration_ms, overlay_key = overlay_queue.get_nowait()
                        queue_key = overlay_key or f"__standalone__:{time.time_ns()}"
                        pending[queue_key] = (title, message, duration_ms, overlay_key)
                except queue.Empty:
                    pass
                except Exception as e:
                    logging.error(f"处理浮层队列失败: {e}")
                for title, message, duration_ms, overlay_key in pending.values():
                    create_overlay_window(root, title, message, duration_ms, overlay_key=overlay_key)
                root.after(15, pump_queue)

            overlay_manager_ready.set()
            root.after(0, pump_queue)
            root.mainloop()
        except Exception as e:
            logging.error(f"浮层管理器启动失败: {e}")

    overlay_manager_thread = threading.Thread(target=_run, daemon=True)
    overlay_manager_thread.start()
    overlay_manager_ready.wait(timeout=2)

def show_overlay_popup(title, message, duration_ms=OVERLAY_DURATION_MS, overlay_key=None):
    """显示一个始终置顶的本地浮层，作为本地提醒"""
    ensure_overlay_manager()
    overlay_queue.put((title, message, duration_ms, overlay_key))

def send_notification(title, message):
    """发送Windows系统通知"""
    try:
        logging.debug(f"准备发送通知: title={title}, message={message}")
        icon_path = get_notification_icon_path()

        # 分割消息内容
        message_parts = message.split('\n')
        title_text = message_parts[0]
        content_text = message_parts[1] if len(message_parts) > 1 else ""

        if is_notification_mode("system"):
            toast = Notification(
                app_id="微信",
                title=title_text,
                msg=content_text,
                icon=icon_path,
                duration="short"
            )
            toast.set_audio(NOTIFICATION_SOUND, loop=False)
            toast.show()
            logging.info(f"系统通知已发送: {message}")
        else:
            show_overlay_popup(title_text, content_text or title_text, overlay_key=title_text)
            logging.info(f"本地浮层已显示: {message}")
    except Exception as e:
        logging.error(f"发送通知失败: {e}")

def extract_message_content(control):
    """从控件中提取消息内容"""
    try:
        if not control.Name:
            return None
            
        # 检查是否包含"条新消息"
        if "条新消息" not in control.Name:
            return None
            
        # 修正后的正则表达式，明确分离联系人名称和消息数量
        match = re.match(r"^(.+?)(?:已置顶)?(\d+)条新消息$", control.Name)
        if not match:
            return None
            
        contact_name = match.group(1).strip()
        message_count = match.group(2)
        
        # 获取最新消息内容
        latest_message = ""
        
        def find_text_controls(ctrl):
            nonlocal latest_message
            # 按深度优先顺序遍历控件
            for child in ctrl.GetChildren():
                # 优先处理深层嵌套的控件
                find_text_controls(child)
                
                # 后判断当前控件是否符合条件（确保深层控件优先）
                if child.ControlType == 50020:
                    # 增加筛选条件：控件高度必须大于30像素（过滤数字角标）
                    if (child.BoundingRectangle.height() > 30 and 
                        is_valid_message_content(child.Name, contact_name)):
                        
                        logging.debug(f"有效消息内容: {child.Name}")
                        latest_message = child.Name
                        return  # 优先取深层控件后立即返回

        # 移除process_special_message函数
        def is_valid_message_content(message, contact_name):
            """判断是否为有效消息内容"""
            return (not re.match(r"\d{1,2}:\d{2}", message) and
                    message != contact_name)

        def process_special_message(message):
            """处理特殊消息类型"""
            # 语音消息处理
            if message == '1':
                return '[语音]'
            # 其他消息直接返回
            return message
        
        # 开始递归查找文本控件
        find_text_controls(control)
        
        # 检查消息是否有变化
        if contact_name in notified_messages:
            old_count, old_content = notified_messages[contact_name]
            if old_count == message_count and old_content == latest_message:
                return None
        
        # 更新消息历史
        notified_messages[contact_name] = (message_count, latest_message)
            
        # 构建通知消息
        notification = contact_name
        if int(message_count) > 1:  # 只在消息数量大于1时显示数量
            notification += f" ({message_count})"
        if latest_message:
            notification += f"\n{latest_message}"
        
        return notification
        
    except Exception as e:
        logging.error(f"提取消息内容失败: {e}")
    return None

def main():
    """主函数"""
    # 检查微信是否运行
    wechat_info = get_wechat_process_info()
    wechat_process = wechat_info["process"] if wechat_info else None
    
    if not wechat_process:
        # 发送通知提醒用户启动微信
        toast = Notification(
            app_id="微信监控",
            title="微信未运行",
            msg="请先启动微信客户端，程序将在微信启动后自动运行",
            icon=get_notification_icon_path(),
            duration="short"
        )
        toast.set_audio(NOTIFICATION_SOUND, loop=False)
        toast.show()
        logging.error("微信未运行")
        
        # 持续检测微信进程
        while not wechat_process:
            time.sleep(2)  # 每2秒检查一次
            wechat_info = get_wechat_process_info()
            wechat_process = wechat_info["process"] if wechat_info else None

    wechat_version = wechat_info.get("version") if wechat_info else None
    wechat_process_name = wechat_info.get("process_name") if wechat_info else None
    wechat_exe_path = wechat_info.get("exe_path") if wechat_info else None
    if wechat_process_name:
        logging.info(f"检测到微信进程: {wechat_process_name}")
    if wechat_version:
        logging.info(f"检测到微信版本: {wechat_version}")

    if is_wechat_v4(wechat_version, wechat_process_name, wechat_exe_path):
        if Desktop is None:
            toast = Notification(
                app_id="微信监控",
                title="缺少微信 4.x 依赖",
                msg="请先安装 pywinauto 以启用微信 4.x 监控。",
                icon=get_notification_icon_path(),
                duration="short"
            )
            toast.set_audio(NOTIFICATION_SOUND, loop=False)
            toast.show()
            logging.error("检测到微信 4.x，但当前环境未安装 pywinauto。")
            return

        logging.info("检测到微信 4.x，启用 pywinauto 兼容监控。")
        try:
            monitor_wechat_messages_v4()
        except KeyboardInterrupt:
            logging.info("程序已停止")
        return
    
    # 等待并检测微信窗口
    wechat_window = find_wechat_window()
    if not wechat_window:
        toast = Notification(
            app_id="微信监控",
            title="等待微信窗口",
            msg="请确保微信窗口已打开，程序将在检测到窗口后自动运行",
            icon=get_notification_icon_path(),
            duration="short"
        )
        toast.set_audio(NOTIFICATION_SOUND, loop=False)
        toast.show()
        
        # 持续检测微信窗口
        while not wechat_window:
            time.sleep(2)  # 每2秒检查一次
            wechat_window = find_wechat_window()
    
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_wechat_messages, daemon=True)
    monitor_thread.start()
    
    # 主线程保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("程序已停止")

if __name__ == "__main__":
    # 默认使用 INFO，必要时可通过环境变量 WECHAT_NOTIFIER_LOG_LEVEL=DEBUG 打开详细日志
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('wechat_monitor.log', encoding='utf-8')
        ],
        force=True
    )
    main()
