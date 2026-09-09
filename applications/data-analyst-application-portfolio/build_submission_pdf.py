from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Ahn_Seongchan_Data_Analyst_Application_Portfolio.pdf"
FONT_REGULAR = Path("C:/Windows/Fonts/malgun.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/malgunbd.ttf")

NAVY = colors.HexColor("#14213D")
TEAL = colors.HexColor("#007C78")
ORANGE = colors.HexColor("#E58B35")
INK = colors.HexColor("#233247")
MUTED = colors.HexColor("#5E6C7B")
LINE = colors.HexColor("#D8E0E8")
PALE = colors.HexColor("#F4F8FA")
WHITE = colors.white
W, H = A4
MARGIN = 22 * mm


def setup_fonts():
    pdfmetrics.registerFont(TTFont("Malgun", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("MalgunBold", str(FONT_BOLD)))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="MalgunBold", fontSize=28, leading=38, textColor=NAVY),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName="Malgun", fontSize=11.5, leading=18, textColor=MUTED),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="MalgunBold", fontSize=20, leading=28, textColor=NAVY, spaceAfter=8),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="MalgunBold", fontSize=13, leading=19, textColor=TEAL, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Malgun", fontSize=10, leading=16, textColor=INK),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="Malgun", fontSize=8.3, leading=12, textColor=MUTED),
        "caption": ParagraphStyle("caption", parent=base["BodyText"], fontName="Malgun", fontSize=8.5, leading=12, textColor=MUTED),
        "metric": ParagraphStyle("metric", parent=base["BodyText"], fontName="MalgunBold", fontSize=21, leading=25, textColor=NAVY, alignment=TA_CENTER),
        "metric_label": ParagraphStyle("metric_label", parent=base["BodyText"], fontName="Malgun", fontSize=8.2, leading=11, textColor=MUTED, alignment=TA_CENTER),
        "table": ParagraphStyle("table", parent=base["BodyText"], fontName="Malgun", fontSize=8.3, leading=11, textColor=INK),
        "table_bold": ParagraphStyle("table_bold", parent=base["BodyText"], fontName="MalgunBold", fontSize=8.3, leading=11, textColor=NAVY),
    }


def p(text, style):
    return Paragraph(text, style)


def draw_footer(c, number):
    c.setStrokeColor(LINE)
    c.line(MARGIN, 15 * mm, W - MARGIN, 15 * mm)
    c.setFillColor(MUTED)
    c.setFont("Malgun", 7.5)
    c.drawString(MARGIN, 10 * mm, "안성찬 | Data Analyst Application Portfolio | Public-data case studies")
    c.drawRightString(W - MARGIN, 10 * mm, f"{number} / 9")


def draw_header(c, section, number):
    c.setFillColor(TEAL)
    c.rect(0, H - 10 * mm, W, 10 * mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("MalgunBold", 7.5)
    c.drawString(MARGIN, H - 6.8 * mm, section)
    draw_footer(c, number)


def para(c, text, style, x, y_top, width):
    block = p(text, style)
    _, height = block.wrap(width, 1000)
    block.drawOn(c, x, y_top - height)
    return y_top - height


def panel(c, x, y_top, width, height, fill=PALE, stroke=LINE):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.roundRect(x, y_top - height, width, height, 4 * mm, fill=1, stroke=1)


def metric_card(c, x, y_top, width, value, label, s):
    panel(c, x, y_top, width, 31 * mm, fill=PALE)
    para(c, value, s["metric"], x + 4 * mm, y_top - 8 * mm, width - 8 * mm)
    para(c, label, s["metric_label"], x + 4 * mm, y_top - 20 * mm, width - 8 * mm)


def simple_table(c, data, x, y_top, widths, s, header=True, row_heights=None):
    formatted = []
    for row_index, row in enumerate(data):
        style = s["table_bold"] if header and row_index == 0 else s["table"]
        formatted.append([cell if isinstance(cell, Paragraph) else p(str(cell), style) for cell in row])
    table = Table(formatted, colWidths=widths, rowHeights=row_heights, repeatRows=1 if header else 0)
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands.extend([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F3F2")), ("TEXTCOLOR", (0, 0), (-1, 0), NAVY)])
    table.setStyle(TableStyle(commands))
    _, height = table.wrap(sum(widths), 1000)
    table.drawOn(c, x, y_top - height)
    return y_top - height


def page_cover(c, s):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.circle(W - 15 * mm, H - 24 * mm, 24 * mm, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.circle(W - 43 * mm, H - 46 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#A8DDD8"))
    c.rect(MARGIN, H - 57 * mm, 48 * mm, 2.2 * mm, fill=1, stroke=0)
    cover_title = ParagraphStyle("cover_title", parent=s["title"], textColor=WHITE, fontSize=30, leading=41)
    cover_subtitle = ParagraphStyle("cover_subtitle", parent=s["subtitle"], textColor=colors.HexColor("#D1E6E3"), fontSize=12, leading=19)
    para(c, "데이터 분석가<br/>채용 지원 포트폴리오", cover_title, MARGIN, H - 77 * mm, 125 * mm)
    para(c, "공개 데이터로 검증한 고객 행동 분석, 재구매 우선순위화, 그리고 실험 설계의 경계", cover_subtitle, MARGIN, H - 121 * mm, 130 * mm)
    c.setFillColor(colors.HexColor("#D1E6E3"))
    c.setFont("MalgunBold", 12)
    c.drawString(MARGIN, 45 * mm, "안성찬")
    c.setFont("Malgun", 9.5)
    c.drawString(MARGIN, 37 * mm, "Data Analyst | SQL · Python · Product & CRM Analytics")
    c.setFont("Malgun", 7.5)
    c.drawString(MARGIN, 20 * mm, "All observations are from public-data offline analyses. No company performance or experiment outcome is claimed.")


def page_summary(c, s):
    draw_header(c, "OVERVIEW", 2)
    y = H - 28 * mm
    y = para(c, "문제를 측정 가능한 판단으로 바꾸는 분석", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "분석 결과 자체보다, 어떤 의사결정을 바꿀 수 있는지와 결과가 말해 주지 않는 범위를 함께 제시합니다.", s["subtitle"], MARGIN, y - 3 * mm, W - 2 * MARGIN)
    card_w = 50 * mm
    card_y = y - 16 * mm
    metric_card(c, MARGIN, card_y, card_w, "2", "public-data case studies", s)
    metric_card(c, MARGIN + 56 * mm, card_y, card_w, "397,884", "clean transaction lines", s)
    metric_card(c, MARGIN + 112 * mm, card_y, card_w, "24,026", "clickstream sessions", s)
    y = card_y - 41 * mm
    y = para(c, "포트폴리오의 두 가지 질문", s["h2"], MARGIN, y, W - 2 * MARGIN)
    data = [
        ["프로젝트", "사업 질문", "의사결정으로의 연결"],
        ["고객 재구매 우선순위화", "검토 자원이 제한될 때 누구를 먼저 볼 것인가?", "점수를 자동 발송이 아닌 CRM 검토 큐의 입력으로 제한"],
        ["세션 탐색 행동 분석", "사용자는 상품을 얼마나 깊게 탐색하는가?", "짧고 긴 탐색을 제품 문제로 단정하지 않고 필요한 이벤트와 실험을 정의"],
    ]
    y = simple_table(c, data, MARGIN, y - 4 * mm, [43 * mm, 62 * mm, 63 * mm], s)
    y = para(c, "작성 원칙", s["h2"], MARGIN, y - 14 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 4 * mm, W - 2 * MARGIN, 38 * mm)
    para(c, "• 공개 원천과 재현 경로를 명시합니다.<br/>• 오프라인 예측 성능, 실제 캠페인 증분 효과, 운영 성과를 서로 다른 증거 수준으로 구분합니다.<br/>• 실제 기업 고객·매출·실험 결과를 주장하지 않습니다.", s["body"], MARGIN + 7 * mm, y - 11 * mm, W - 2 * MARGIN - 14 * mm)


def page_case1_question(c, s):
    draw_header(c, "CASE 1 · CRM ANALYTICS", 3)
    y = H - 28 * mm
    y = para(c, "고객 재구매 우선순위화", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "Question: CRM 검토 자원이 제한돼 있을 때 어떤 고객을 먼저 검토할 것인가?", s["subtitle"], MARGIN, y - 2 * mm, W - 2 * MARGIN)
    y = para(c, "문제와 데이터", s["h2"], MARGIN, y - 14 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 4 * mm, W - 2 * MARGIN, 48 * mm)
    para(c, "UCI Online Retail의 공개 거래 데이터를 사용했습니다. 취소 송장, Customer ID가 없는 행, 수량 또는 단가가 0 이하인 행을 제외하고 분석했습니다. 원천은 2010-12-01부터 2011-12-09까지의 영국 기반 온라인 소매 거래입니다.", s["body"], MARGIN + 7 * mm, y - 12 * mm, W - 2 * MARGIN - 14 * mm)
    metric_card(c, MARGIN, y - 59 * mm, 50 * mm, "397,884", "clean transaction lines", s)
    metric_card(c, MARGIN + 56 * mm, y - 59 * mm, 50 * mm, "4,338", "unique customers", s)
    metric_card(c, MARGIN + 112 * mm, y - 59 * mm, 50 * mm, "90 days", "prediction horizon", s)
    y = y - 101 * mm
    y = para(c, "검증 설계", s["h2"], MARGIN, y, W - 2 * MARGIN)
    data = [
        ["구성", "정의"],
        ["분석 단위", "Customer ID당 1행"],
        ["타깃", "기준일 이후 90일 내 양의 구매가 1회 이상 있는지 여부"],
        ["피처", "최근성, 주문 수, 구매 수량, 매출, 평균 주문금액, 상품 다양성, 이전 구매 이력"],
        ["평가", "상위 10% CRM 검토 용량에서 최근성 기준선과 로지스틱 회귀 비교"],
    ]
    y = simple_table(c, data, MARGIN, y - 4 * mm, [40 * mm, 128 * mm], s)
    para(c, "누수 방지를 위해 무작위 분할 대신 과거 3개 시점으로 학습하고, 2011-09-08 이후의 보지 않은 90일을 최종 평가에 사용했습니다.", s["caption"], MARGIN, y - 11 * mm, W - 2 * MARGIN)


def page_case1_result(c, s):
    draw_header(c, "CASE 1 · EVIDENCE", 4)
    y = H - 28 * mm
    y = para(c, "동일한 검토 용량에서 56명을 더 포착", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "최종 평가 대상 3,357명 중 57.0%가 이후 90일 내 재구매했습니다.", s["subtitle"], MARGIN, y - 2 * mm, W - 2 * MARGIN)
    y = para(c, "오프라인 우선순위 성능", s["h2"], MARGIN, y - 15 * mm, W - 2 * MARGIN)
    data = [
        ["방법", "ROC-AUC", "검토 고객", "Precision@Top 10%", "Recall@Top 10%", "포착 고객"],
        ["최근성 기준선", "0.687", "336", "78.9%", "13.8%", "265"],
        ["로지스틱 회귀", "0.735", "336", "95.5%", "16.8%", "321"],
    ]
    y = simple_table(c, data, MARGIN, y - 4 * mm, [34 * mm, 22 * mm, 24 * mm, 31 * mm, 29 * mm, 28 * mm], s)
    y = para(c, "무엇이 달라졌나", s["h2"], MARGIN, y - 17 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 3 * mm, W - 2 * MARGIN, 51 * mm, fill=colors.HexColor("#E8F3F2"), stroke=colors.HexColor("#B7D9D6"))
    para(c, "같은 336명 검토 용량에서, 최근성만 사용한 기준선보다 재구매 고객을 <b>56명 더 포착</b>했습니다. 이는 고객을 먼저 검토할 순서를 정하는 오프라인 근거입니다.", s["body"], MARGIN + 8 * mm, y - 12 * mm, W - 2 * MARGIN - 16 * mm)
    para(c, "이 결과가 의미하지 않는 것", s["h2"], MARGIN, y - 65 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 69 * mm, W - 2 * MARGIN, 47 * mm, fill=colors.HexColor("#FFF5EB"), stroke=colors.HexColor("#F1D0AE"))
    para(c, "모델이 메시지·할인·추천으로 재구매를 <b>일으켰다</b>는 증거는 아닙니다. 원천에 마진, 재고, 수신 동의, 접촉 빈도, 마케팅 노출 정보가 없어 실제 캠페인 정책을 결정할 수 없습니다.", s["body"], MARGIN + 8 * mm, y - 78 * mm, W - 2 * MARGIN - 16 * mm)
    para(c, "Metric note: Precision@Top 10%는 검토 고객 중 향후 재구매자의 비율, Recall@Top 10%는 전체 향후 재구매자 중 검토 큐가 포착한 비율입니다.", s["caption"], MARGIN, y - 128 * mm, W - 2 * MARGIN)


def page_case1_action(c, s):
    draw_header(c, "CASE 1 · DECISION DESIGN", 5)
    y = H - 28 * mm
    y = para(c, "모델 결과를 자동 발송 규칙으로 바꾸지 않는다", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "점수는 사람 검토가 필요한 CRM 후보군을 좁히는 입력으로만 사용하고, 실제 효과는 실험으로 확인합니다.", s["subtitle"], MARGIN, y - 2 * mm, W - 2 * MARGIN)
    y = para(c, "제안된 운영 흐름", s["h2"], MARGIN, y - 15 * mm, W - 2 * MARGIN)
    steps = [
        ("1", "점수화", "구매 이력으로 고객 우선순위를 계산"),
        ("2", "사람 검토", "최근 카테고리·주문금액·구매 주기와 운영 제약을 확인"),
        ("3", "무작위 홀드아웃", "고점수 고객 안에서 처리군과 대조군을 무작위 배정"),
        ("4", "확대 또는 중단", "증분 효과와 가드레일을 근거로 다음 행동 결정"),
    ]
    for index, (num, title, text) in enumerate(steps):
        top = y - 7 * mm - index * 28 * mm
        c.setFillColor(TEAL if index < 3 else ORANGE)
        c.circle(MARGIN + 8 * mm, top - 8 * mm, 6 * mm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("MalgunBold", 9)
        c.drawCentredString(MARGIN + 8 * mm, top - 10.8 * mm, num)
        para(c, title, s["h2"], MARGIN + 20 * mm, top, 45 * mm)
        para(c, text, s["body"], MARGIN + 64 * mm, top, 103 * mm)
        if index < 3:
            c.setStrokeColor(LINE)
            c.line(MARGIN + 8 * mm, top - 15 * mm, MARGIN + 8 * mm, top - 22 * mm)
    y = y - 124 * mm
    y = para(c, "실제 테스트의 성공·보호 지표", s["h2"], MARGIN, y, W - 2 * MARGIN)
    data = [
        ["성공 지표", "가드레일", "결정"],
        ["증분 재구매율, 공헌이익", "수신거부율, 접촉 빈도, 할인 의존도", "확대, 수정 실험, 또는 중단"],
    ]
    simple_table(c, data, MARGIN, y - 4 * mm, [57 * mm, 63 * mm, 48 * mm], s)


def page_case2_question(c, s):
    draw_header(c, "CASE 2 · PRODUCT ANALYTICS", 6)
    y = H - 28 * mm
    y = para(c, "세션 탐색 행동 분석", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "Question: 사용자는 상품을 얼마나 깊게 탐색하며, 짧거나 긴 탐색 세션은 어떤 비중인가?", s["subtitle"], MARGIN, y - 2 * mm, W - 2 * MARGIN)
    y = para(c, "데이터와 지표", s["h2"], MARGIN, y - 15 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 4 * mm, W - 2 * MARGIN, 48 * mm)
    para(c, "UCI Clickstream Data for Online Shopping의 CC BY 4.0 공개 데이터를 사용했습니다. 2008년 4~8월 의류 쇼핑몰 클릭스트림이며, 세션 ID별 클릭 수와 최대 클릭 순서를 집계해 탐색 깊이를 정의했습니다.", s["body"], MARGIN + 7 * mm, y - 12 * mm, W - 2 * MARGIN - 14 * mm)
    metric_card(c, MARGIN, y - 59 * mm, 50 * mm, "165,474", "public click events", s)
    metric_card(c, MARGIN + 56 * mm, y - 59 * mm, 50 * mm, "24,026", "sessions", s)
    metric_card(c, MARGIN + 112 * mm, y - 59 * mm, 50 * mm, "6.89", "mean clicks per session", s)
    y = y - 101 * mm
    y = para(c, "분석 질문", s["h2"], MARGIN, y, W - 2 * MARGIN)
    data = [
        ["관측", "분석 방식"],
        ["탐색 깊이", "세션별 클릭 수를 1회, 2-3회, 4-6회, 7회 이상으로 분류"],
        ["카테고리", "첫 클릭의 주 카테고리별 평균 클릭 수를 비교"],
        ["해석 경계", "구매·매출·실험군·장기 사용자 식별자가 없어 기술 통계로만 해석"],
    ]
    simple_table(c, data, MARGIN, y - 4 * mm, [40 * mm, 128 * mm], s)


def page_case2_result(c, s):
    draw_header(c, "CASE 2 · EVIDENCE", 7)
    y = H - 28 * mm
    y = para(c, "탐색 깊이는 분포로 읽고, 제품 문제로 단정하지 않는다", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "세션별 클릭 수의 분포는 관측값입니다. 클릭이 짧은 세션이 불만족을 뜻하는지는 별도 결과 이벤트가 있어야 판단할 수 있습니다.", s["subtitle"], MARGIN, y - 2 * mm, W - 2 * MARGIN)
    y = para(c, "탐색 깊이 분포", s["h2"], MARGIN, y - 15 * mm, W - 2 * MARGIN)
    bars = [("1회", 5042, TEAL), ("2-3회", 5940, TEAL), ("4-6회", 5032, TEAL), ("7회 이상", 8012, ORANGE)]
    max_value = 8012
    top = y - 10 * mm
    for label, value, color in bars:
        c.setFillColor(INK)
        c.setFont("MalgunBold", 9)
        c.drawString(MARGIN, top - 4 * mm, label)
        c.setFillColor(colors.HexColor("#E8EEF2"))
        c.roundRect(MARGIN + 28 * mm, top - 8 * mm, 110 * mm, 6 * mm, 2 * mm, fill=1, stroke=0)
        c.setFillColor(color)
        c.roundRect(MARGIN + 28 * mm, top - 8 * mm, 110 * mm * value / max_value, 6 * mm, 2 * mm, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.setFont("Malgun", 8.5)
        c.drawRightString(W - MARGIN, top - 4 * mm, f"{value:,} sessions")
        top -= 16 * mm
    y = top - 8 * mm
    y = para(c, "첫 카테고리별 평균 클릭 수", s["h2"], MARGIN, y, W - 2 * MARGIN)
    data = [
        ["첫 카테고리", "세션 수", "평균 클릭 수"],
        ["Trousers", "9,247", "7.91"],
        ["Sale", "3,862", "7.21"],
        ["Blouses", "4,445", "5.99"],
        ["Skirts", "6,472", "5.85"],
    ]
    y = simple_table(c, data, MARGIN, y - 4 * mm, [70 * mm, 49 * mm, 49 * mm], s)
    para(c, "카테고리별 차이는 인과 관계가 아닙니다. 유입 채널, 가격, 재고, 노출 수, 정렬, 필터 사용처럼 누락된 변수의 영향을 이 데이터만으로 분리할 수 없습니다.", s["caption"], MARGIN, y - 11 * mm, W - 2 * MARGIN)


def page_experiment(c, s):
    draw_header(c, "FROM OBSERVATION TO EXPERIMENT", 8)
    y = H - 28 * mm
    y = para(c, "관측 결과를 다음 실험으로 바꾸는 방식", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "제품 분석에서 행동 지표는 출발점입니다. 결과 지표와 가드레일을 갖춘 실험을 통해서만 변경의 효과를 판단합니다.", s["subtitle"], MARGIN, y - 2 * mm, W - 2 * MARGIN)
    y = para(c, "클릭스트림 관측에서 이어지는 검증 질문", s["h2"], MARGIN, y - 15 * mm, W - 2 * MARGIN)
    data = [
        ["관측", "추가로 필요한 데이터", "검증할 가설", "성공 판단"],
        ["1회 탐색 세션 21.0%", "구매·이탈·검색어·오류·유입 채널", "특정 진입면의 상품 적합성 또는 탐색 흐름이 약한가?", "구매/장바구니 전환, 검색 재시도, 오류율"],
        ["카테고리별 탐색 깊이 차이", "노출 수·가격·재고·정렬·필터 사용", "정렬 또는 필터가 탐색 부담을 낮추는가?", "탐색 후 전환, 필터 사용률, 재방문"],
        ["7회 이상 세션 33.3%", "세션 종료 이유·구매·페이지 성능", "긴 탐색은 높은 관심인가, 탐색 마찰인가?", "전환, 체류, 반복 클릭, 오류율"],
    ]
    y = simple_table(c, data, MARGIN, y - 4 * mm, [33 * mm, 44 * mm, 48 * mm, 43 * mm], s, row_heights=[None, 35 * mm, 35 * mm, 35 * mm])
    y = para(c, "실험 설계 체크", s["h2"], MARGIN, y - 14 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 4 * mm, W - 2 * MARGIN, 45 * mm, fill=colors.HexColor("#E8F3F2"), stroke=colors.HexColor("#B7D9D6"))
    para(c, "<b>Primary metric</b> 변경이 해결하려는 결과를 직접 측정하는 지표<br/><b>Guardrail</b> 고객 경험·수익성·품질 악화를 막는 지표<br/><b>Decision rule</b> 사전에 정한 효과 크기와 가드레일을 기준으로 확대, 추가 실험, 중단을 선택", s["body"], MARGIN + 8 * mm, y - 12 * mm, W - 2 * MARGIN - 16 * mm)


def page_sources(c, s):
    draw_header(c, "REPRODUCIBILITY & SOURCES", 9)
    y = H - 28 * mm
    y = para(c, "재현성, 데이터 사용 원칙, 프로젝트 링크", s["h1"], MARGIN, y, W - 2 * MARGIN)
    y = para(c, "원천 데이터 행은 저장소에 포함하지 않습니다. 공개 원천을 직접 내려받아 분석 코드와 문서를 따라 재현할 수 있도록 구성했습니다.", s["subtitle"], MARGIN, y - 2 * mm, W - 2 * MARGIN)
    y = para(c, "프로젝트 저장소", s["h2"], MARGIN, y - 15 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 4 * mm, W - 2 * MARGIN, 44 * mm)
    para(c, "GitHub: github.com/RaphaelAhn/data-portfolio<br/>• projects/customer-repurchase-analytics - analysis code, requirements, output summary<br/>• projects/clickstream-behavior-analysis - case-study documentation and scope boundaries<br/>• applications/data-analyst-application-portfolio - this portfolio's source document and validation record", s["body"], MARGIN + 8 * mm, y - 12 * mm, W - 2 * MARGIN - 16 * mm)
    y = para(c, "공개 원천", s["h2"], MARGIN, y - 61 * mm, W - 2 * MARGIN)
    data = [
        ["원천", "사용 범위"],
        ["Chen, D. (2015). Online Retail. UCI Machine Learning Repository. DOI: 10.24432/C5BW33", "거래 정제, 고객별 시간 기준 피처, 재구매 우선순위 오프라인 평가"],
        ["Clickstream Data for Online Shopping. UCI Machine Learning Repository. CC BY 4.0", "세션 단위 탐색 깊이의 기술 통계와 후속 실험 가설"],
    ]
    y = simple_table(c, data, MARGIN, y - 4 * mm, [84 * mm, 84 * mm], s, row_heights=[None, 28 * mm, 28 * mm])
    y = para(c, "분석의 경계", s["h2"], MARGIN, y - 15 * mm, W - 2 * MARGIN)
    panel(c, MARGIN, y - 4 * mm, W - 2 * MARGIN, 42 * mm, fill=colors.HexColor("#FFF5EB"), stroke=colors.HexColor("#F1D0AE"))
    para(c, "공개 데이터의 2008년·2010-2011년 시장 특성이 현재 특정 기업의 사용자 행동을 대표하는지는 확인하지 않았습니다. 실제 온라인 실험, 운영 성과, 고객 영향은 검증하지 않았습니다.", s["body"], MARGIN + 8 * mm, y - 12 * mm, W - 2 * MARGIN - 16 * mm)
def build():
    setup_fonts()
    s = styles()
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Ahn Seongchan - Data Analyst Application Portfolio")
    c.setAuthor("Ahn Seongchan")
    c.setSubject("Public-data portfolio case studies")
    for page in [page_cover, page_summary, page_case1_question, page_case1_result, page_case1_action, page_case2_question, page_case2_result, page_experiment, page_sources]:
        page(c, s)
        c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
