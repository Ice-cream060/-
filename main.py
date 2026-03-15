import sys
import os
from pathlib import Path
from openai import OpenAI
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel,
                             QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGraphicsRectItem, QFrame, QGraphicsDropShadowEffect,
                             QGraphicsProxyWidget, QMessageBox, QScrollArea,
                             QComboBox, QStackedWidget, QMenu, QInputDialog)  # 新增必要的UI组件
from PyQt6.QtCore import Qt, QPointF, QThread, pyqtSignal, QVariantAnimation, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (QColor, QPainter, QPen, QPainterPath, QFont, QAction)
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_TAB_ALIGNMENT
import pdfkit
from PyQt6.QtCore import Qt, QPointF, QThread, pyqtSignal, QVariantAnimation, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize, QBuffer, QByteArray, QIODevice
from PyQt6.QtGui import (QColor, QPainter, QPen, QPainterPath, QFont, QAction, QPixmap, QImage)
from PyQt6.QtWidgets import QDialog, QFileDialog  # 确保有这两个
# 找到这一行并将其替换为（在末尾加上 QRectF）：
from PyQt6.QtCore import Qt, QPointF, QThread, pyqtSignal, QVariantAnimation, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize, QBuffer, QByteArray, QIODevice, QRectF

# ==========================================
# 🎨 1. 动态主题引擎配置
# ==========================================
THEMES = {
    "黑色": {
        "bg": "#0D0D12", "panel": "rgba(20, 20, 28, 220)", "drawer": "#12121A",
        "text": "#D4D4D8", "title": "#FFFFFF", "btn": "#2A2A35", "btn_hover": "#3A3A4A",
        "canvas_bg": QColor(13, 13, 18), "dot": QColor(255, 255, 255, 12), "border": "rgba(255,255,255,15)"
    },
    "白色": {
        "bg": "#F5F5F7", "panel": "rgba(255, 255, 255, 230)", "drawer": "#FFFFFF",
        "text": "#333333", "title": "#000000", "btn": "#E5E5EA", "btn_hover": "#D1D1D6",
        "canvas_bg": QColor(245, 245, 247), "dot": QColor(0, 0, 0, 15), "border": "rgba(0,0,0,10)"
    },
    "粉色": {
        "bg": "#FFF0F5", "panel": "rgba(255, 240, 245, 230)", "drawer": "#FFE4E1",
        "text": "#553344", "title": "#441122", "btn": "#FFC0CB", "btn_hover": "#FFB6C1",
        "canvas_bg": QColor(255, 240, 245), "dot": QColor(0, 0, 0, 15), "border": "rgba(0,0,0,8)"
    },
    "橙色": {
        "bg": "#FFF5E6", "panel": "rgba(255, 245, 230, 230)", "drawer": "#FFEBCD",
        "text": "#553311", "title": "#331100", "btn": "#FFDAB9", "btn_hover": "#FFC080",
        "canvas_bg": QColor(255, 245, 230), "dot": QColor(0, 0, 0, 15), "border": "rgba(0,0,0,8)"
    }
}


def get_stylesheet(theme_name):
    t = THEMES[theme_name]
    return f"""
    QMainWindow {{ background-color: {t['bg']}; }}
    QFrame#toolbar {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 24px; }}
    QFrame#drawer, QFrame#leftDrawer {{ background: {t['drawer']}; border: 1px solid {t['border']}; }}

    QLabel {{ color: {t['text']}; }}
    QLabel#mainTitle {{ color: {t['title']}; font-weight: bold; font-size: 16px; letter-spacing: 2px; }}

    QPushButton#menuBtn {{ background: transparent; color: {t['title']}; font-size: 16px; font-weight: bold; border: none; }}
    QPushButton#menuBtn:hover {{ color: #00E5FF; }}

    QPushButton#exportBtn {{ background: {t['title']}; color: {t['bg']}; border-radius: 6px; font-weight: bold; font-size: 14px; padding: 8px 18px; border: none; }}
    QPushButton#exportBtn:hover {{ background: #00E5FF; color: #FFFFFF; }}

    QPushButton#primary {{ background: {t['btn']}; color: {t['text']}; border-radius: 6px; font-weight: bold; padding: 8px 16px; border: 1px solid {t['border']}; }}
    QPushButton#primary:hover {{ background: {t['btn_hover']}; }}

    QPushButton#success {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00E5FF, stop:1 #007BFF); color: #FFFFFF; border-radius: 6px; font-weight: bold; padding: 8px 16px; border: none; }}
    QPushButton#success:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #33EEFF, stop:1 #3395FF); }}
    QPushButton#success:disabled {{ background: #888888; color: #DDDDDD; }}

    QPushButton#moduleBtn {{ background: transparent; border: 1px solid transparent; color: {t['text']}; border-radius: 16px; font-weight: bold; font-size: 13px; padding: 6px 12px; }}
    QPushButton#moduleBtn:hover {{ background: {t['btn']}; border: 1px solid {t['border']}; }}

    QPushButton#themeBtn {{ background: {t['btn']}; color: {t['text']}; border-radius: 6px; padding: 8px; margin: 4px 0px; text-align: left; padding-left: 15px; font-weight: bold; }}
    QPushButton#themeBtn:hover {{ background: {t['btn_hover']}; }}

    QLineEdit, QTextEdit {{ background: rgba(128,128,128,0.05); border: 1px solid {t['border']}; border-radius: 6px; color: {t['title']}; font-size: 14px; padding: 8px; line-height: 1.5; }}
    QLineEdit:focus, QTextEdit:focus {{ border: 1px solid #00E5FF; background: rgba(0,229,255,0.03); }}

    QScrollArea {{ border: none; background: transparent; }}
    QWidget#formContainer {{ background: transparent; }}
    """


# ==========================================
# ⚙️ 2. 结构化模块配置 (带动态表单字段)
# ==========================================
# 提取出通用规则，避免和前面的身份指令冲突
COMMON_RULE = "直接输出排版后的纯文本，绝对禁止输出任何废话、前言后语或Markdown代码块标签！\n具体附加要求如下："

MODULE_CONFIGS = {
    "基本信息": {
        "fields": [
            {"name": "name", "label": "姓名", "type": "line"},
            {"name": "phone", "label": "电话", "type": "line"},
            {"name": "email", "label": "邮箱", "type": "line"},
            {"name": "job", "label": "求职意向", "type": "line"},
            {"name": "github", "label": "个人主页/GitHub (选填)", "type": "line"}
        ],
        "guide": "【内容指引】请填写基础联系方式，这是HR第一眼看到的信息。",
        "prompt": COMMON_RULE + "1. 剔除多余的形容词。2. 将联系方式统一格式化排版。"
    },
    "教育背景": {
        "fields": [
            {"name": "school", "label": "学校名称", "type": "line"},
            {"name": "major", "label": "专业名称", "type": "line"},
            {"name": "degree", "label": "学历 (如 本科/硕士)", "type": "line"},
            {"name": "time", "label": "就读时间 (如 2018.09-2022.06)", "type": "line"},
            {"name": "course", "label": "主修课程/GPA (选填)", "type": "text"}
        ],
        "guide": "【内容指引】填写最高学历信息，建议倒序排列。",
        "prompt": COMMON_RULE + "1. 梳理为极简结构。2. 翻译非正式的学术词汇为专业术语。"
    },
    "项目经历": {
        "fields": [
            {"name": "proj_name", "label": "项目名称", "type": "line"},
            {"name": "role", "label": "担任角色", "type": "line"},
            {"name": "time", "label": "起止时间", "type": "line"},
            {"name": "tech", "label": "核心技术栈", "type": "line"},
            {"name": "desc", "label": "项目详情 (STAR法则：背景、任务、行动、结果)", "type": "text"}
        ],
        "guide": "【内容指引】重点在详情中突出“你具体做了什么”和“量化的成果”。",
        "prompt": COMMON_RULE + "1. 每句话必须用动作强动词开头。2. 提取并强化可量化的结果指标。3. 采用分点描述。"
    },
    "实习经历": {
        "fields": [
            {"name": "company", "label": "公司名称", "type": "line"},
            {"name": "position", "label": "职位名称", "type": "line"},
            {"name": "time", "label": "在职时间", "type": "line"},
            {"name": "desc", "label": "工作内容及产出", "type": "text"}
        ],
        "guide": "【内容指引】简述实习负责的业务线及团队成就。",
        "prompt": COMMON_RULE + "1. 将日常琐事转化为具有业务价值的职场语言。2. 强调“行动+结果”。"
    },
    "个人技能": {
        "fields": [
            {"name": "skills", "label": "技能清单 (按熟练度分类列出)", "type": "text"}
        ],
        "guide": "【内容指引】按技术栈或熟练度（精通、熟练、熟悉）归类。",
        "prompt": COMMON_RULE + "1. 纠正拼写错误。2. 按照技术类别合并同类项，列表输出。"
    },
    "个人荣誉": {
        "fields": [
            {"name": "honor_name", "label": "奖项名称 (如 国家励志奖学金)", "type": "line"},
            {"name": "time", "label": "获奖时间", "type": "line"},
            {"name": "level", "label": "获奖级别/说明 (如 国家级/排名前5%)", "type": "text"}
        ],
        "guide": "【内容指引】填写您的核心奖项，突出稀缺性和含金量。",
        "prompt": COMMON_RULE + "突出奖项的含金量和稀缺性，采用严谨的书面排版风格。"
    },
    "自我评价": {
        "fields": [
            {"name": "eval", "label": "自我评价 (核心竞争力、优势、驱动力)", "type": "text"}
        ],
        "guide": "【内容指引】拒绝套话。用3句话总结核心竞争力及职业热情。",
        "prompt": COMMON_RULE + "1. 删除假大空的套话。2. 提炼3个硬实力/软实力卖点，语气自信专业。"
    },
# --- 找到 MODULE_CONFIGS 并在里面加上这个 ---
    "个人肖像": {
        "fields": [
            {"name": "avatar", "label": "上传并裁剪个人相片 (正方形)", "type": "image"}
        ],
        "guide": "【内容指引】请上传一张清晰的高管职业照或证件照。建议背景干净，面部光线明亮。",
        "prompt": COMMON_RULE + "无需润色。" # 肖像模块会被代码拦截，不会发送给AI
    },
# ----------------------------------------
}

MODULE_LIST = ["基本信息","个人肖像", "教育背景", "项目经历", "实习经历", "个人技能", "个人荣誉", "自我评价"]


# ==========================================
# 💎 零边框高级弹窗组件
# ==========================================
class ModernMessageBox(QDialog):
    def __init__(self, title, text, msg_type="info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(360)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 主体容器 (深邃灰黑背景，细微描边)
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1A1A24;
                border: 1px solid #333344;
                border-radius: 12px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(25, 25, 25, 20)
        container_layout.setSpacing(15)

        # 标题与正文
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold; border: none;")
        container_layout.addWidget(self.title_label)

        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("color: #BBBBCC; font-size: 14px; line-height: 1.5; border: none;")
        container_layout.addWidget(self.text_label)

        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if msg_type == "question":
            self.no_btn = QPushButton("取消")
            self.no_btn.setStyleSheet(
                "background: transparent; color: #BBBBCC; border: 1px solid #555; padding: 8px 20px; border-radius: 6px;")
            self.no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.no_btn.clicked.connect(self.reject)
            btn_layout.addWidget(self.no_btn)

            self.yes_btn = QPushButton("确认")
            self.yes_btn.setStyleSheet(
                "background: #00E5FF; color: #000; padding: 8px 20px; border-radius: 6px; font-weight: bold; border: none;")
            self.yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.yes_btn.clicked.connect(self.accept)
            btn_layout.addWidget(self.yes_btn)
        else:
            self.ok_btn = QPushButton("我知道了")
            self.ok_btn.setStyleSheet(
                "background: #00E5FF; color: #000; padding: 8px 20px; border-radius: 6px; font-weight: bold; border: none;")
            self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.ok_btn.clicked.connect(self.accept)
            btn_layout.addWidget(self.ok_btn)

        container_layout.addLayout(btn_layout)
        self.layout.addWidget(self.container)

        # 高级质感阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)

    @staticmethod
    def information(parent, title, text):
        ModernMessageBox(title, text, "info", parent).exec()

    @staticmethod
    def warning(parent, title, text):
        ModernMessageBox(title, text, "warning", parent).exec()

    @staticmethod
    def critical(parent, title, text):
        ModernMessageBox(title, text, "critical", parent).exec()

    @staticmethod
    def question(parent, title, text):
        return ModernMessageBox(title, text, "question", parent).exec() == QDialog.DialogCode.Accepted
# ==========================================
# ✂️ 图像裁剪引擎组件
# ==========================================
class CropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.origin = QPoint()
        self.target_rect = QRect()
        self.drawing = False
        self._pixmap = None

    def set_image(self, pixmap):
        self._pixmap = pixmap
        self.setFixedSize(pixmap.size())

        # 默认：最大居中正方形裁剪
        side = min(pixmap.width(), pixmap.height())
        x = (pixmap.width() - side) // 2
        y = (pixmap.height() - side) // 2
        self.target_rect = QRect(x, y, side, side)
        self.update()

    def mousePressEvent(self, event):
        # 【修复1】：PyQt6 废弃了 event.pos()，必须使用 position().toPoint()
        self.origin = event.position().toPoint()
        self.target_rect = QRect(self.origin, QSize())
        self.drawing = True
        self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            # 【修复1】：同上
            current_pos = event.position().toPoint()
            rect = QRect(self.origin, current_pos).normalized()
            side = min(rect.width(), rect.height())
            rect.setWidth(side)
            rect.setHeight(side)
            self.target_rect = rect
            self.update()

    def mouseReleaseEvent(self, event):
        self.drawing = False

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._pixmap: return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)

        if not self.target_rect.isEmpty():
            # 绘制暗黑遮罩
            path = QPainterPath()
            # 【修复2】：PyQt6 极其严格，必须套上一层 QRectF 否则直接底层崩溃
            path.addRect(QRectF(self.rect()))
            crop_path = QPainterPath()
            crop_path.addRect(QRectF(self.target_rect))
            path = path.subtracted(crop_path)

            painter.setBrush(QColor(0, 0, 0, 160))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)

            # 绘制裁剪框高亮边框
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(0, 229, 255), 2))
            painter.drawRect(self.target_rect)

    def get_cropped(self):
        if not self._pixmap or self.target_rect.isEmpty():
            return self._pixmap
        return self._pixmap.copy(self.target_rect)

class ImageCropDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📸 裁剪职业照")
        self.setFixedSize(700, 750)
        self.setStyleSheet("QDialog { background-color: #12121A; color: #FFFFFF; }")

        layout = QVBoxLayout(self)

        hint = QLabel("💡 提示：点击下方按钮加载图片。在图片上【按住拖拽】可重新画正方形裁剪框。")
        hint.setStyleSheet("color: #A0A0B0; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(hint)

        self.select_btn = QPushButton("📂 从电脑选择图片")
        self.select_btn.setStyleSheet(
            "background: #2A2A35; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_btn.clicked.connect(self.load_image)
        layout.addWidget(self.select_btn)

        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setStyleSheet("background: #0D0D12; border: 1px dashed #333;")

        self.crop_label = CropLabel()
        self.scroll.setWidget(self.crop_label)
        layout.addWidget(self.scroll, 1)

        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet(
            "background: transparent; color: white; border: 1px solid #555; padding: 8px 20px; border-radius: 6px;")
        self.cancel_btn.clicked.connect(self.reject)

        self.confirm_btn = QPushButton("✅ 确认裁剪并保存")
        self.confirm_btn.setStyleSheet(
            "background: #00E5FF; color: #000; padding: 8px 20px; border-radius: 6px; font-weight: bold;")
        self.confirm_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)
        layout.addLayout(btn_layout)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            pixmap = QPixmap(path)
            # 【修复3】：正确的枚举应该是 KeepAspectRatio，多一个Smooth会崩溃
            if pixmap.width() > 800 or pixmap.height() > 800:
                pixmap = pixmap.scaled(800, 800, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            self.crop_label.set_image(pixmap)

    def get_cropped_pixmap(self):
        return self.crop_label.get_cropped()
# ==========================================
# 🧠 3. DeepSeek AI 引擎 (融合岗位信息)
# ==========================================
class DeepSeekWorker(QThread):
    finished = pyqtSignal(str, bool)

    def __init__(self, content, module_type, target_job):
        super().__init__()
        self.content = content
        self.module_type = module_type
        self.target_job = target_job if target_job else "通用岗位"

    def run(self):
        try:
            client = OpenAI(
                api_key="YOUR_APIKEY",
                base_url="https://api.deepseek.com"
            )

            # 【核心功能】：动态生成强关联岗位的 Prompt
            dynamic_identity = f"你作为一个具有20年经验的高级简历优化师，现在用户要应聘的职业是：【{self.target_job}】，请你优化他的【{self.module_type}】内容，使其变得专业，能够帮助面试官抓取重点。\n"
            module_specific_prompt = MODULE_CONFIGS.get(self.module_type, {}).get("prompt", COMMON_RULE)

            system_prompt = dynamic_identity + module_specific_prompt

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"需要润色的原始信息如下：\n{self.content}"},
                ],
                stream=False
            )
            result = response.choices[0].message.content.strip()
            self.finished.emit(result, True)
        except Exception as e:
            self.finished.emit(f"AI 引擎异常:\n{str(e)}", False)


# ==========================================
# 🔗 4. 霓虹连线组件 (保持不变)
# ==========================================
class ConnectionLine(QGraphicsItem):
    # 此部分与原版一致...
    def __init__(self, source_node, dest_node):
        super().__init__()
        self.source = source_node
        self.dest = dest_node
        self.setZValue(-1)
        self.dash_offset = 0.0
        self.anim = QVariantAnimation()
        self.anim.setDuration(800)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(20.0)
        self.anim.setLoopCount(-1)
        self.anim.valueChanged.connect(self._update_offset)
        self.anim.start()

    def _update_offset(self, val):
        self.dash_offset = val
        self.update()

    def get_path(self):
        start = self.source.scenePos() + QPointF(self.source.width / 2, self.source.height)
        end = self.dest.scenePos() + QPointF(self.dest.width / 2, 0)
        path = QPainterPath(start)
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        if abs(dy) >= abs(dx):
            ctrl_len = max(50.0, abs(dy) / 2.5)
            ctrl1 = QPointF(start.x(), start.y() + ctrl_len)
            ctrl2 = QPointF(end.x(), end.y() - ctrl_len)
        else:
            ctrl_len = max(50.0, abs(dx) / 2.5)
            offset_x = ctrl_len if dx > 0 else -ctrl_len
            ctrl1 = QPointF(start.x() + offset_x, start.y() + 30)
            ctrl2 = QPointF(end.x() - offset_x, end.y() - 30)
        path.cubicTo(ctrl1, ctrl2, end)
        return path

    def boundingRect(self):
        return self.get_path().boundingRect().adjusted(-20, -20, 20, 20)

    def paint(self, painter, option, widget):
        path = self.get_path()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        glow_pen = QPen(QColor(0, 229, 255, 30), 6, Qt.PenStyle.SolidLine)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen)
        painter.drawPath(path)
        core_pen = QPen(QColor(0, 229, 255, 210), 1.5, Qt.PenStyle.DashLine)
        core_pen.setDashPattern([6, 4])
        core_pen.setDashOffset(self.dash_offset)
        core_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(core_pen)
        painter.drawPath(path)


# ==========================================
# 🧩 5. 动态展示节点 (保持不变)
# ==========================================
class BaseNode(QGraphicsRectItem):
    # 此部分与原版一致...
    def __init__(self, title, app_controller, width=320):
        super().__init__()
        self.app_controller = app_controller
        self.width = width
        self.title = title
        self.form_data = {}
        self.connected_lines = []

        self.height = 100
        self.setRect(0, 0, self.width, self.height)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPen(QPen(Qt.PenStyle.NoPen))

        self.container = QWidget()
        self.container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 15, 20, 20)
        self.layout.setSpacing(10)

        # ✨ 需求3附加：调整白底上的文字颜色（深蓝黑与冷灰）
        self.t_label = QLabel(title)
        self.t_label.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 15px; letter-spacing: 1px;")

        self.content_label = QLabel("双击填写模块内容")
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("color: #64748B; font-size: 13px; line-height: 1.5;")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.layout.addWidget(self.t_label)
        self.layout.addWidget(self.content_label)
        self.layout.addStretch()

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.container)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 15)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)
        self.update_geometry()

    def get_display_text(self):
        if not self.form_data: return ""
        # 拦截肖像模块的超长代码
        if self.title == "个人肖像":
            return "✅ 已上传并保存职业照" if self.form_data.get("avatar") else "尚未上传职业照"

        lines = []
        fields = MODULE_CONFIGS.get(self.title, {}).get("fields", [])
        for f in fields:
            val = self.form_data.get(f['name'], "").strip()
            if val:
                prefix = f['label'].split(' ')[0]
                lines.append(f"{prefix}: {val}")
        return "\n".join(lines)
    def sync_from_dict(self, data_dict):
        self.form_data = data_dict
        display_text = self.get_display_text()
        if display_text:
            self.content_label.setText(display_text)
            self.content_label.setStyleSheet("font-size: 13px; line-height: 1.5;")
        else:
            self.content_label.setText("双击填写模块内容")
            self.content_label.setStyleSheet("color: #888899; font-size: 13px;")
        self.update_geometry()

    def update_geometry(self):
        self.content_label.adjustSize()
        calc_height = self.content_label.height() + 60
        self.height = max(100, calc_height)
        self.prepareGeometryChange()
        self.setRect(0, 0, self.width, self.height)
        self.container.setFixedSize(self.width, self.height)
        self.proxy.resize(self.width, self.height)
        self.app_controller.update_dynamic_connections()

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.boundingRect()

        # ✨ 需求3：强制将模块背景改为干净的高级白 (带有一点点透明度融入背景)
        painter.setBrush(QColor(255, 255, 255, 245))

        # 选中状态高亮青色边框，未选中状态为非常浅的冷灰边框
        if self.isSelected():
            painter.setPen(QPen(QColor(0, 229, 255, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 215, 120), 1))

        painter.drawRoundedRect(rect, 8, 8)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for line in self.connected_lines:
                line.prepareGeometryChange()
        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.app_controller.update_dynamic_connections()

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.app_controller.open_focus_drawer(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # ✨ 使用我们自定义的高级弹窗，直接判断返回布尔值
            if ModernMessageBox.question(None, '确认删除', f"确定要删除【{self.title}】模块吗？"):
                self.app_controller.delete_node(self)
        else:
            super().mousePressEvent(event)


# ==========================================
# 🖼️ 6. 动态主题画布
# ==========================================
class WorkflowCanvas(QGraphicsView):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.scene = QGraphicsScene(-2000, -2000, 4000, 4000)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setStyleSheet("border: none; background: transparent;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def drawBackground(self, painter, rect):
        theme = THEMES[self.app_controller.current_theme]
        painter.fillRect(rect, theme["canvas_bg"])
        left = int(rect.left()) - (int(rect.left()) % 30)
        top = int(rect.top()) - (int(rect.top()) % 30)
        painter.setPen(QPen(theme["dot"], 1))
        for x in range(left, int(rect.right()), 30):
            for y in range(top, int(rect.bottom()), 30):
                painter.drawPoint(x, y)


# ==========================================
# 🖥️ 7. 主控引擎 (带引导页与 QStackedWidget)
# ==========================================
class SimpleResumeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简面 Pro - 高管级简历架构引擎")
        self.resize(1400, 900)

        self.current_theme = "黑色"
        self.target_job = "未指定(通用岗位)"  # 全局记录用户的理想职业
        self.nodes = []
        self.lines = []
        self.current_focus_node = None
        self.active_form_widgets = {}

        # 引入页面管理器
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 构建页面
        self.setup_intro_page()
        self.setup_main_page()

        self.apply_theme(self.current_theme)

    def setup_intro_page(self):
        """需求1：制作整洁的引导页"""
        self.intro_page = QWidget()
        self.intro_page.setStyleSheet("background-color: #0D0D12;")
        layout = QVBoxLayout(self.intro_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 大标题
        title = QLabel("简 面")
        title.setStyleSheet("font-size: 72px; font-weight: bold; color: #FFFFFF; letter-spacing: 12px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 副标题
        subtitle = QLabel("助力每一个为写简历而烦恼的小孩")
        subtitle.setStyleSheet("font-size: 18px; color: #00E5FF; margin-bottom: 50px; font-weight: bold;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 输入框区域
        input_label = QLabel("你的理想职业是？")
        input_label.setStyleSheet("font-size: 15px; color: #A0A0B0; margin-bottom: 5px;")
        input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("例如：后端开发工程师、产品经理")
        self.job_input.setFixedSize(400, 50)
        self.job_input.setStyleSheet(
            "background: rgba(255,255,255,0.05); font-size: 16px; padding: 10px 15px; border-radius: 8px; border: 1px solid #444; color: white;")
        self.job_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.job_input.returnPressed.connect(self.enter_main_app)  # 按回车也能进入

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(20)

        start_btn = QPushButton("开启简面之旅")
        start_btn.setFixedSize(180, 45)
        start_btn.setStyleSheet(
            "background: #00E5FF; color: #000; font-weight: bold; font-size: 15px; border-radius: 6px;")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self.enter_main_app)

        skip_btn = QPushButton("跳过")
        skip_btn.setFixedSize(80, 45)
        skip_btn.setStyleSheet(
            "background: transparent; color: #666; font-size: 15px; text-decoration: underline; border: none;")
        skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        skip_btn.clicked.connect(self.skip_intro)

        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(skip_btn)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(input_label)
        layout.addWidget(self.job_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        layout.addLayout(btn_layout)

        self.stacked_widget.addWidget(self.intro_page)

    def enter_main_app(self):
        job = self.job_input.text().strip()
        if job:
            self.target_job = job
        self.stacked_widget.setCurrentIndex(1)

    def skip_intro(self):
        self.target_job = "未指定(通用岗位)"
        self.stacked_widget.setCurrentIndex(1)

    def setup_main_page(self):
        self.main_page = QWidget()
        main_layout = QVBoxLayout(self.main_page)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Header ---
        header_container = QWidget()
        header_panel = QHBoxLayout(header_container)
        header_panel.setContentsMargins(20, 15, 30, 15)

        self.menu_btn = QPushButton("☰ 更多")
        self.menu_btn.setObjectName("menuBtn")
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_left_drawer)

        slogan = QLabel("简面 PRO")
        slogan.setObjectName("mainTitle")

        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "👔 投行咨询风 (极简黑白)",
            "💻 大厂技术风 (紧凑高信息密度)",
            "🎨 产品设计风 (层次色彩)"
        ])
        self.template_combo.setStyleSheet("""
            QComboBox { background: #2A2A35; color: #E2E2E2; border-radius: 6px; padding: 6px 15px; border: 1px solid rgba(255,255,255,20); font-size: 13px; font-weight: bold; }
            QComboBox::drop-down { border: none; }
        """)
        self.template_combo.setFixedSize(220, 36)
        self.template_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.gen_btn = QPushButton("🚀 生成 pdf 文档")
        self.gen_btn.setObjectName("exportBtn")
        self.gen_btn.setFixedSize(160, 36)
        self.gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.gen_btn.clicked.connect(self.generate_pdf)

        header_panel.addWidget(self.menu_btn)
        header_panel.addSpacing(20)
        header_panel.addWidget(slogan)
        header_panel.addStretch()
        header_panel.addWidget(self.template_combo)
        header_panel.addSpacing(10)
        header_panel.addWidget(self.gen_btn)
        main_layout.addWidget(header_container)

        # --- 工作区 (左侧主题抽屉 + 画布 + 右侧编辑抽屉) ---
        workspace_layout = QHBoxLayout()
        workspace_layout.setSpacing(0)

        # 左侧抽屉
        self.left_drawer = QFrame()
        self.left_drawer.setObjectName("leftDrawer")
        self.left_drawer.setFixedWidth(0)
        ld_layout = QVBoxLayout(self.left_drawer)
        ld_layout.setContentsMargins(20, 20, 20, 20)
        ld_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        ld_layout.setSpacing(15)

        ld_title = QLabel("⚙️ 更多设置")
        ld_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        ld_layout.addWidget(ld_title)
        ld_layout.addSpacing(10)

        # 【需求5】修改目标职业按钮
        self.job_edit_btn = QPushButton("💼 修改目标职业")
        self.job_edit_btn.setObjectName("themeBtn")
        self.job_edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.job_edit_btn.clicked.connect(self.edit_target_job)
        ld_layout.addWidget(self.job_edit_btn)

        # 【需求4】主题选择集成到一个按钮下拉菜单中
        self.theme_btn = QPushButton("🎨 切换界面主题")
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 挂载 QMenu
        self.theme_menu = QMenu(self)
        self.theme_menu.setStyleSheet("""
            QMenu { background-color: #2A2A35; color: #E2E2E2; border: 1px solid #555; border-radius: 4px; padding: 5px; }
            QMenu::item { padding: 8px 25px; font-size: 13px; font-weight: bold; border-radius: 4px; }
            QMenu::item:selected { background-color: #00E5FF; color: #000; }
        """)
        for t_name in THEMES.keys():
            action = self.theme_menu.addAction(t_name)
            action.triggered.connect(lambda checked, t=t_name: self.apply_theme(t))
        self.theme_btn.setMenu(self.theme_menu)
        ld_layout.addWidget(self.theme_btn)

        workspace_layout.addWidget(self.left_drawer)

        # 画布
        canvas_container = QFrame()
        cc_layout = QVBoxLayout(canvas_container)
        cc_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = WorkflowCanvas(self)
        cc_layout.addWidget(self.canvas)
        workspace_layout.addWidget(canvas_container, 1)

        # 右侧抽屉：动态填空表单
        self.drawer = QFrame()
        self.drawer.setObjectName("drawer")
        self.drawer.setFixedWidth(0)
        drawer_layout = QVBoxLayout(self.drawer)
        drawer_layout.setContentsMargins(25, 25, 25, 25)
        drawer_layout.setSpacing(15)

        self.drawer_title = QLabel("模块编辑")
        self.drawer_title.setStyleSheet("font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        drawer_layout.addWidget(self.drawer_title)

        self.guide_label = QLabel()
        self.guide_label.setWordWrap(True)
        self.guide_label.setStyleSheet(
            "color: #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 12px; border-radius: 6px; font-size: 13px; line-height: 1.4;")
        drawer_layout.addWidget(self.guide_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.form_container = QWidget()
        self.form_container.setObjectName("formContainer")
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.form_container)
        drawer_layout.addWidget(scroll, 1)

        ai_tools_layout = QHBoxLayout()
        self.ai_polish_btn = QPushButton("✨ DeepSeek 智能润色")
        self.ai_polish_btn.setObjectName("success")
        self.ai_polish_btn.setFixedHeight(36)
        self.ai_polish_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_polish_btn.clicked.connect(self.trigger_ai_polish)
        ai_tools_layout.addStretch()
        ai_tools_layout.addWidget(self.ai_polish_btn)
        drawer_layout.addLayout(ai_tools_layout)

        drawer_layout.addWidget(QLabel("<span style='font-size: 12px;'>AI 润色结果预览：</span>"))
        self.result_editor = QTextEdit()
        self.result_editor.setFixedHeight(120)
        drawer_layout.addWidget(self.result_editor)

        bottom_btn_layout = QHBoxLayout()
        apply_btn = QPushButton("应用 AI 结果")
        apply_btn.setStyleSheet(
            "background: transparent; border: 1px solid #00E5FF; color: #00E5FF; border-radius: 6px; font-weight: bold; padding: 8px 16px;")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.clicked.connect(self.apply_ai_result)

        self.save_btn = QPushButton("保存并收起")
        self.save_btn.setObjectName("primary")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_and_close_drawer)

        bottom_btn_layout.addWidget(apply_btn)
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(self.save_btn)
        drawer_layout.addLayout(bottom_btn_layout)

        workspace_layout.addWidget(self.drawer)
        main_layout.addLayout(workspace_layout, 1)

        # --- 底部 ---
        dock_container = QVBoxLayout()
        dock_container.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        dock_container.setContentsMargins(0, 0, 0, 20)
        dock_container.setSpacing(8)

        global_hint = QLabel("💡 提示：一段经历对应一个模块！有多段经历请多次添加相同模块。")
        global_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dock_container.addWidget(global_hint)

        self.toolbar = QFrame()
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setFixedHeight(50)
        tool_layout = QHBoxLayout(self.toolbar)
        tool_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tool_layout.setContentsMargins(15, 0, 15, 0)
        tool_layout.setSpacing(5)

        for name in MODULE_LIST:
            btn = QPushButton(name)
            btn.setObjectName("moduleBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self.add_node_to_canvas(n))
            tool_layout.addWidget(btn)

        toolbar_wrapper = QHBoxLayout()
        toolbar_wrapper.addStretch()
        toolbar_wrapper.addWidget(self.toolbar)
        toolbar_wrapper.addStretch()
        dock_container.addLayout(toolbar_wrapper)
        main_layout.addLayout(dock_container)

        self.stacked_widget.addWidget(self.main_page)

    def edit_target_job(self):
        """【需求5】弹出对话框修改当前理想职业"""
        current_job = self.target_job if self.target_job != "未指定(通用岗位)" else ""
        text, ok = QInputDialog.getText(self, "目标职业", "请输入你想应聘的理想职业：\n(该信息将用于AI精准润色简历)",
                                        QLineEdit.EchoMode.Normal, current_job)
        if ok and text.strip():
            self.target_job = text.strip()
            QMessageBox.information(self, "成功", f"目标职业已成功更新为：【{self.target_job}】")

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        self.setStyleSheet(get_stylesheet(theme_name))
        self.canvas.viewport().update()
        for node in self.nodes:
            node.update()

    def toggle_left_drawer(self):
        target_width = 200 if self.left_drawer.width() == 0 else 0
        self.ld_anim = QPropertyAnimation(self.left_drawer, b"minimumWidth")
        self.ld_anim.setDuration(300)
        self.ld_anim.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.ld_anim.setEndValue(target_width)
        self.ld_anim.start()

    def add_node_to_canvas(self, name):
        node = BaseNode(name, self)
        start_y = -50 + len(self.nodes) * 150
        node.setPos(0, start_y)
        self.canvas.scene.addItem(node)
        self.nodes.append(node)
        self.update_dynamic_connections()
        self.canvas.centerOn(node)
        self.canvas.viewport().update()

    def delete_node(self, node):
        lines_to_remove = [line for line in self.lines if line.source == node or line.dest == node]
        for line in lines_to_remove:
            self.canvas.scene.removeItem(line)
            if line in self.lines: self.lines.remove(line)
        self.canvas.scene.removeItem(node)
        if node in self.nodes: self.nodes.remove(node)
        if self.current_focus_node == node:
            self.close_focus_drawer_animation()
        self.update_dynamic_connections()
        self.canvas.viewport().update()

    def update_dynamic_connections(self):
        if len(self.nodes) < 2:
            for line in self.lines: self.canvas.scene.removeItem(line)
            self.lines.clear()
            return
        for line in self.lines: self.canvas.scene.removeItem(line)
        self.lines.clear()
        for node in self.nodes: node.connected_lines.clear()
        sorted_nodes = sorted(self.nodes, key=lambda n: n.scenePos().y())
        for i in range(len(sorted_nodes) - 1):
            source, dest = sorted_nodes[i], sorted_nodes[i + 1]
            line = ConnectionLine(source, dest)
            source.connected_lines.append(line)
            dest.connected_lines.append(line)
            self.canvas.scene.addItem(line)
            self.lines.append(line)

    def open_focus_drawer(self, node):
        self.current_focus_node = node
        self.drawer_title.setText(f"编辑 · {node.title}")
        config = MODULE_CONFIGS.get(node.title, {})
        self.guide_label.setText(config.get("guide", "填写本模块内容。"))
        self.result_editor.clear()

        # 清除旧表单
        for i in reversed(range(self.form_layout.count())):
            widget = self.form_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        self.active_form_widgets.clear()

        # 动态生成填空或图片上传控件
        for field in config.get("fields", []):
            lbl = QLabel(field["label"])
            lbl.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 8px;")
            self.form_layout.addWidget(lbl)

            val = node.form_data.get(field["name"], "")

            # 核心判断：如果是图片类型
            if field["type"] == "image":
                w = QWidget()
                w_layout = QVBoxLayout(w)
                w_layout.setContentsMargins(0, 0, 0, 0)

                preview = QLabel("尚未上传")
                preview.setFixedSize(140, 140)
                preview.setStyleSheet(
                    "background: rgba(255,255,255,0.05); border-radius: 20px; border: 1px dashed #555; color: #888;")
                preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # 如果之前传过，解码展示
                if val:
                    pm = QPixmap()
                    pm.loadFromData(QByteArray.fromBase64(val.encode()))
                    # 【修复3】：修正此处的枚举名称
                    preview.setPixmap(pm.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
                    preview.setProperty("b64", val)

                btn = QPushButton("📸 选取并裁剪照片")
                btn.setObjectName("primary")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)

                # ✨ 修复1：使用 *args 吸收掉 clicked 信号发出的 bool 干扰值
                def pick_image(*args):
                    dlg = ImageCropDialog(self)
                    if dlg.exec():
                        cp = dlg.get_cropped_pixmap()
                        if cp:
                            # ✨ 修复2：直接使用外层作用域的 preview 变量，绝对安全
                            preview.setPixmap(cp.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio,
                                                        Qt.TransformationMode.SmoothTransformation))

                            # ✨ 修复3：将 QPixmap 转换为 QImage (脱离底层显存，纯内存操作，彻底杜绝 Segfault)
                            img = cp.toImage()

                            # 安全转码 Base64
                            ba = QByteArray()
                            buf = QBuffer(ba)
                            buf.open(QIODevice.OpenModeFlag.WriteOnly)
                            img.save(buf, "PNG")

                            preview.setProperty("b64", ba.toBase64().data().decode('utf-8'))

                btn.clicked.connect(pick_image)
                w_layout.addWidget(btn)
                w_layout.addWidget(preview)
                self.form_layout.addWidget(w)

                # 将 preview 标签存入字典以便后续提取 Base64
                self.active_form_widgets[field["name"]] = preview

            elif field["type"] == "line":
                w = QLineEdit()
                w.setText(val)
                self.form_layout.addWidget(w)
                self.active_form_widgets[field["name"]] = w
            else:
                w = QTextEdit()
                w.setPlainText(val)
                w.setFixedHeight(100)
                self.form_layout.addWidget(w)
                self.active_form_widgets[field["name"]] = w

        self.drawer_anim = QPropertyAnimation(self.drawer, b"minimumWidth")
        self.drawer_anim.setDuration(400)
        self.drawer_anim.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.drawer_anim.setEndValue(480)
        # ✨ 需求1：动态控制 AI 润色按钮的状态
        if node.title == "个人肖像":
            self.ai_polish_btn.setEnabled(False)
            self.ai_polish_btn.setText("🚫 纯图片模块，无需 AI 润色")
            self.ai_polish_btn.setStyleSheet(
                "background: #2A2A35; color: #555566; border-radius: 6px; font-weight: bold; padding: 8px 16px; border: none;")
        else:
            self.ai_polish_btn.setEnabled(True)
            self.ai_polish_btn.setText("✨ DeepSeek 智能润色")
            self.ai_polish_btn.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00E5FF, stop:1 #007BFF); color: #FFFFFF; border-radius: 6px; font-weight: bold; padding: 8px 16px; border: none;")

        # 🚀 抽屉弹出动画 (确保在最后统一配置并启动)
        self.drawer_anim = QPropertyAnimation(self.drawer, b"minimumWidth")
        self.drawer_anim.setDuration(400)
        self.drawer_anim.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.drawer_anim.setEndValue(480)
        self.drawer_anim.start()

    def save_and_close_drawer(self):
        if self.current_focus_node:
            new_data = {}
            for name, widget in self.active_form_widgets.items():
                if isinstance(widget, QLineEdit):
                    new_data[name] = widget.text().strip()
                elif isinstance(widget, QTextEdit):
                    new_data[name] = widget.toPlainText().strip()
                elif isinstance(widget, QLabel):
                    # 存储图片 Base64 数据
                    b64 = widget.property("b64")
                    new_data[name] = b64 if b64 else ""

            self.current_focus_node.sync_from_dict(new_data)
        self.close_focus_drawer_animation()

    def close_focus_drawer_animation(self):
        self.current_focus_node = None
        self.drawer_anim = QPropertyAnimation(self.drawer, b"minimumWidth")
        self.drawer_anim.setDuration(350)
        self.drawer_anim.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.drawer_anim.setEndValue(0)
        self.drawer_anim.start()

    def get_current_draft_text(self):
        parts = []
        fields = MODULE_CONFIGS.get(self.current_focus_node.title, {}).get("fields", [])
        for f in fields:
            w = self.active_form_widgets.get(f["name"])
            if w:
                val = w.text().strip() if isinstance(w, QLineEdit) else w.toPlainText().strip()
                if val: parts.append(f"{f['label']}: {val}")
        return "\n".join(parts)

    def trigger_ai_polish(self):
        # 拦截肖像模块的 AI 润色请求
        if self.current_focus_node and self.current_focus_node.title == "个人肖像":
            QMessageBox.information(self, "提示", "个人肖像模块为纯图片格式，无需 AI 润色。")
            return

        content = self.get_current_draft_text()
        if not content:
            QMessageBox.warning(self, "提示", "请先在填空中输入内容后再进行润色。")
            return

        module_type = self.current_focus_node.title
        self.ai_polish_btn.setText("网络请求中...")
        self.ai_polish_btn.setEnabled(False)
        self.result_editor.setPlainText(f"DeepSeek 正在为您的【{self.target_job}】岗位重构描述...")

        # 传入 target_job 使得 AI 根据职业进行专门优化
        self.ai_worker = DeepSeekWorker(content, module_type, self.target_job)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.start()

    def on_ai_finished(self, result, success):
        self.ai_polish_btn.setText("✨ DeepSeek 智能润色")
        self.ai_polish_btn.setEnabled(True)
        self.result_editor.setPlainText(result)
        if not success: QMessageBox.critical(self, "API 错误", result)

    def apply_ai_result(self):
        ai_text = self.result_editor.toPlainText().strip()
        if not ai_text or "重构描述..." in ai_text or "异常" in ai_text: return

        for w in self.active_form_widgets.values():
            if isinstance(w, QTextEdit):
                w.setPlainText(ai_text)
                return
        QMessageBox.information(self, "提示", "未找到适合长文本的输入框，请手动复制结果。")

    def generate_pdf(self):
        if not self.nodes:
            QMessageBox.warning(self, "提示", "画布为空，请先添加模块。")
            return

        desktop_path = str(Path.home() / "Desktop")
        html_path = os.path.join(desktop_path, "resume_temp.html")
        pdf_path = os.path.join(desktop_path, "简面_高管尊享版.pdf")

        # ==========================================
        # 【防崩溃检测】：确保 PDF 文件没有被阅读器占用
        # ==========================================
        if os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'a'):
                    pass
            except PermissionError:
                QMessageBox.critical(self, "导出失败",
                                     f"文件正在被使用！\n\n请先关闭已打开的 PDF 文件：\n{pdf_path}\n然后再点击生成。")
                return

        # ==========================================
        # 1. 殿堂级 CSS 样式表 (投行/大厂高管风)
        # ==========================================
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page { margin: 0; size: A4; }

                html, body {
                    margin: 0; 
                    padding: 0;
                    height: 100%; 
                }

                body { 
                    /* 字体栈优化：苹果系优先，兼容 Windows 雅黑，呈现最锐利的边缘 */
                    font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif; 
                    color: #334155; /* 深岩灰，比纯黑更高级 */
                    -webkit-print-color-adjust: exact;

                    /* 重新编码的 SVG 底纹：左侧 66% 纯白，2px 浅灰分割线，右侧 34% 极浅冷灰 (#F8FAFC) */
                    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAwIiBoZWlnaHQ9IjEiPjxyZWN0IHdpZHRoPSI2NjAiIGhlaWdodD0iMSIgZmlsbD0iI2ZmZmZmZiIvPjxyZWN0IHg9IjY2MCIgd2lkdGg9IjIiIGhlaWdodD0iMSIgZmlsbD0iI0UyRThGMCIvPjxyZWN0IHg9IjY2MiIgd2lkdGg9IjMzOCIgaGVpZ2h0PSIxIiBmaWxsPSIjRjhGQUZDIi8+PC9zdmc+");
                    background-size: 100% 1px;
                    background-repeat: repeat-y;
                }

                .resume-container { width: 100%; }
                .resume-container::after { content: ""; display: block; clear: both; }

                /* 边距精心调优，留出呼吸感 */
                .left-col { 
                    float: left; width: 66%; 
                    padding: 65px 55px; box-sizing: border-box; 
                }
                .right-col { 
                    float: left; width: 34%; 
                    padding: 65px 45px; box-sizing: border-box;
                    background: transparent; border: none; 
                }

                /* --- 头部信息 --- */
                .name { 
                    font-size: 46px; font-weight: 900; color: #0F172A; /* 极夜蓝黑 */
                    margin: 0 0 6px 0; letter-spacing: 4px; line-height: 1.1; 
                }
                .job-title { 
                    font-size: 14px; font-weight: 700; color: #3B82F6; /* 科技亮蓝点缀 */
                    margin-bottom: 45px; letter-spacing: 2px; text-transform: uppercase; 
                }

                /* --- 模块标题 (中英双语混合设计) --- */
                .sec-title-wrap {
                    margin-top: 35px; margin-bottom: 22px; 
                    border-bottom: 2px solid #0F172A; padding-bottom: 8px;
                }
                .sec-cn { font-size: 17px; font-weight: 900; color: #0F172A; margin-right: 10px; letter-spacing: 1px;}
                .sec-en { font-size: 12px; font-weight: 500; color: #94A3B8; letter-spacing: 1.5px; text-transform: uppercase; }

                .right-col .sec-title-wrap { border-bottom: 2px solid #CBD5E1; margin-top: 40px; }
                .right-col .sec-cn { font-size: 15px; color: #1E293B; }
                .right-col .sec-en { font-size: 11px; }

                /* --- 内容块 --- */
                .item-block { 
                    margin-bottom: 26px; 
                    page-break-inside: avoid; /* 【神级属性】防止一个项目跨两页被切断！ */
                }
                .item-header-container { display: table; width: 100%; margin-bottom: 6px; }
                .item-title { display: table-cell; text-align: left; font-weight: 800; font-size: 15px; color: #0F172A; }
                .item-date { display: table-cell; text-align: right; font-size: 13px; color: #64748B; font-weight: 600; }

                /* 副标题（如职位、专业等），采用斜体或不同字重区隔 */
                .item-subtitle { font-size: 13.5px; font-weight: 600; color: #475569; margin-bottom: 10px; }
                .tech-stack { color: #3B82F6; font-weight: 500; font-size: 12px; border: 1px solid #BFDBFE; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-left: 8px; vertical-align: middle;}

                /* --- 正文与列表定制 --- */
                .item-desc { font-size: 13px; color: #475569; line-height: 1.8; text-align: justify; }
                .item-desc p { margin: 0 0 6px 0; }

                /* 高级定制列表符号：扁平小方块 */
                .bullet-item { position: relative; padding-left: 18px; margin-bottom: 8px; }
                .bullet-point { 
                    position: absolute; left: 0; top: 8px; 
                    width: 4px; height: 4px; background-color: #3B82F6; border-radius: 1px; 
                }

                /* --- 右侧栏专属：联系方式 & 头像 --- */
                .avatar-wrapper { text-align: center; margin-bottom: 45px; margin-top: -10px; }
                .avatar { 
                    display: inline-block;
                    width: 140px; height: 140px; 
                    background: #E2E8F0; 
                    border-radius: 20px; /* Squircle 现代圆角矩形 */
                    border: 4px solid #FFFFFF;
                    box-shadow: 0 12px 25px -5px rgba(0,0,0,0.08);
                    line-height: 140px; color: #94A3B8; font-size: 13px; font-weight: 600; letter-spacing: 1px;
                    object-fit: cover; /* 保证注入的照片不被拉伸变形 */
                }

                .contact-block { margin-bottom: 20px; }
                .contact-label { font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px; }
                .contact-val { font-size: 13.5px; color: #1E293B; font-weight: 600; word-break: break-all; }

                .right-col .item-desc { font-size: 12.5px; line-height: 1.7; color: #475569; }
            </style>
        </head>
        <body>
            <div class="resume-container">
                <div class="left-col">
                    {LEFT_CONTENT}
                </div>
                <div class="right-col">
                    <div class="avatar-wrapper">
                        {AVATAR_CONTENT}
                    </div>
                    {RIGHT_CONTENT}
                </div>
            </div>
        </body>
        </html>
        """

        # ==========================================
        # 2. 辅助函数：列表解析
        # ==========================================
        def format_desc_html(text):
            if not text: return ""
            html = ""
            for line in text.split('\n'):
                line = line.strip()
                if not line: continue
                if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                    clean_line = line.lstrip("-•* ")
                    html += f"<div class='bullet-item'><span class='bullet-point'></span>{clean_line}</div>"
                else:
                    html += f"<p>{line}</p>"
            return html

        # ==========================================
        # 3. 提取头像模块
        # ==========================================
        avatar_html = '<div class="avatar">IMAGE</div>'
        for node in self.nodes:
            if node.title == "个人肖像" and node.form_data.get("avatar"):
                avatar_b64 = node.form_data.get("avatar")
                avatar_html = f'<img src="data:image/png;base64,{avatar_b64}" class="avatar" />'
                break

        # ==========================================
        # 4. 数据路由与精准解析
        # ==========================================
        RIGHT_MODULES = ["联系方式", "教育背景", "个人荣誉"]
        left_html = ""
        right_html = ""

        sorted_nodes = sorted(self.nodes, key=lambda n: n.scenePos().y())
        previous_title = None

        for node in sorted_nodes:
            data = node.form_data
            if not data: continue

            # 跳过肖像模块，防止其作为文本被渲染
            if node.title == "个人肖像":
                continue

            # --- 基本信息 ---
            if node.title == "基本信息":
                name = data.get('name', '未命名')
                job = data.get('job', self.target_job)
                left_html += f"<div class='name'>{name}</div>"
                left_html += f"<div class='job-title'>{job}</div>"

                right_html += """
                    <div class='sec-title-wrap'>
                        <span class='sec-cn'>联系方式</span><span class='sec-en'>Contact</span>
                    </div>
                """
                contact_map = {'phone': 'Phone', 'email': 'Email', 'github': 'Homepage'}
                for key, label in contact_map.items():
                    val = data.get(key)
                    if val:
                        right_html += f"<div class='contact-block'><div class='contact-label'>{label}</div><div class='contact-val'>{val}</div></div>"
                continue

            # --- 模块标题 (中英双语) ---
            eng_map = {"自我评价": "About Me", "项目经历": "Work Experience", "实习经历": "Experience",
                       "个人技能": "Professional Skills", "教育背景": "Education", "个人荣誉": "Honors & Awards"}
            eng_title = eng_map.get(node.title, "Details")

            section_html = ""
            if node.title != previous_title:
                section_html += f"""
                    <div class='sec-title-wrap'>
                        <span class='sec-cn'>{node.title}</span><span class='sec-en'>{eng_title}</span>
                    </div>
                """
                previous_title = node.title

            # --- 内容解析 ---
            section_html += "<div class='item-block'>"

            if node.title == "教育背景":
                section_html += f"""
                    <div class='item-header-container'>
                        <div class='item-title'>{data.get('school', '')}</div>
                        <div class='item-date'>{data.get('time', '')}</div>
                    </div>
                    <div class='item-subtitle'>{data.get('degree', '')} &nbsp;|&nbsp; {data.get('major', '')}</div>
                    <div class='item-desc'>{format_desc_html(data.get('course', ''))}</div>
                """
            elif node.title == "项目经历":
                tech_badge = f"<span class='tech-stack'>{data.get('tech')}</span>" if data.get('tech') else ""
                section_html += f"""
                    <div class='item-header-container'>
                        <div class='item-title'>{data.get('proj_name', '')}</div>
                        <div class='item-date'>{data.get('time', '')}</div>
                    </div>
                    <div class='item-subtitle'>{data.get('role', '')}{tech_badge}</div>
                    <div class='item-desc'>{format_desc_html(data.get('desc', ''))}</div>
                """
            elif node.title == "实习经历":
                section_html += f"""
                    <div class='item-header-container'>
                        <div class='item-title'>{data.get('company', '')}</div>
                        <div class='item-date'>{data.get('time', '')}</div>
                    </div>
                    <div class='item-subtitle'>{data.get('position', '')}</div>
                    <div class='item-desc'>{format_desc_html(data.get('desc', ''))}</div>
                """
            elif node.title == "个人荣誉":
                section_html += f"""
                    <div class='item-header-container'>
                        <div class='item-title'>{data.get('honor_name', '')}</div>
                        <div class='item-date'>{data.get('time', '')}</div>
                    </div>
                    <div class='item-desc'>{format_desc_html(data.get('level', ''))}</div>
                """
            else:
                raw_text = data.get('skills', '') or data.get('eval', '')
                section_html += f"<div class='item-desc'>{format_desc_html(raw_text)}</div>"

            section_html += "</div>"

            if node.title in RIGHT_MODULES:
                right_html += section_html
            else:
                left_html += section_html

        final_html = html_template.replace("{LEFT_CONTENT}", left_html).replace("{RIGHT_CONTENT}", right_html).replace(
            "{AVATAR_CONTENT}", avatar_html)

        # ==========================================
        # 5. 调用 PDFKit 渲染引擎导出
        # ==========================================
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(final_html)

            path_wkhtmltopdf = r'D:\wkhtmltopdf\bin\wkhtmltopdf.exe'

            if os.path.exists(path_wkhtmltopdf):
                config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
                options = {
                    'page-size': 'A4',
                    'margin-top': '0',
                    'margin-right': '0',
                    'margin-bottom': '0',
                    'margin-left': '0',
                    'encoding': "UTF-8",
                    'enable-local-file-access': None
                }

                pdfkit.from_file(html_path, pdf_path, configuration=config, options=options)

                if os.path.exists(html_path):
                    os.remove(html_path)

                QMessageBox.information(self, "SUCCESS",
                                        f"✨ 尊享级高管简历 PDF 已成功生成至桌面！\n包含高清个人肖像及防跨页截断设计。")
            else:
                QMessageBox.warning(self, "配置错误",
                                    f"在 D 盘指定位置未找到引擎：\n{path_wkhtmltopdf}\n\n请确认 bin 文件夹下是否存在 wkhtmltopdf.exe")

        except Exception as e:
            QMessageBox.critical(self, "渲染失败",
                                 f"错误详情：{str(e)}\n\n(临时的 HTML 文件已保留在桌面，您可以手动用 Chrome 浏览器打开并按 Ctrl+P 打印为 PDF)")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("-apple-system", 10))
    gui = SimpleResumeApp()
    gui.show()
    sys.exit(app.exec())
