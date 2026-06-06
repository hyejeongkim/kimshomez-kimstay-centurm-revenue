Build a complete web application for KIMS HOMES monthly revenue settlement (수익금정산). 

## Project: kimstay-settlement
Single HTML file app (no build tools needed) using vanilla HTML/CSS/JavaScript + CDN libraries.

## Stack
- Single index.html file (self-contained, no server needed)
- Libraries via CDN: SheetJS (xlsx), jsPDF, html2canvas, FileSaver.js
- Pure vanilla JS, no framework needed
- Bootstrap 5 for styling

## Core Features

### 1. Navigation Tabs
- Tab 1: 매출 입력 (Sales Input)
- Tab 2: 비용 입력 (Cost Input)  
- Tab 3: 호실 정보 (Room Management)
- Tab 4: 성과보고서 (Performance Report)
- Tab 5: 정산배분표 (Distribution Table)

### 2. Header
- Company name: KIMS HOMES
- Month/Year selector (year dropdown + month 1-12)
- "새 정산 시작" button to reset all data

### 3. Tab 1: 매출 입력 (Sales Input)
Input fields for each sales channel:
- 야놀자(호텔나우), 에어비앤비, 아고다, 익스피디아, 부킹닷컴, 트립닷컴, 네이버, 여기어때 → OTA 매출 합계 (auto-sum)
- 현금매출_세금계산서, 현금매출_현금영수증, 포스카드(승인기준), 워크인 → 현장매출 합계 (auto-sum)
- 워크인 추가 입력 (부가세별도) field + auto-calculated VAT
- 매출총액 (A) = OTA + 현장 (displayed prominently)
- Excel upload button: upload PMS 매출보고서 xlsx → auto-parse channel amounts
- Download template button: download 매출입력_템플릿.xlsx

### 4. Tab 2: 비용 입력 (Cost Input)
Three sections (Annex 1/2/3):

**Annex 1. 고정비 (Fixed Costs)**
- 1. 인건비
- 2. 간접인건비 (sub-items: 도어락 전지교체비, 전등교체비, 물탱크수리비, 도어락A/S)
- 3. 지급수수료/렌탈 (sub-items: 정수기/비데렌탈 × 개수, 24시관제)
- 4. 선투자비
- 고정비 소계 (a) [auto-sum]

**Annex 2. 변동비 (Variable Costs)**
- 5. 채널수수료
- 6. 관리비
- 7. 하우스키핑 (sub: 이승주 합계, 주인숙 합계, 기타)
- 8. 세탁비
- 9. 사무용품
- 10. 어메니티(청소/비품 포함)
- 11. 복리후생
- 12. 차량유지
- 13. 세금(지급수수료/기장료)
- 변동비 소계 (b) [auto-sum]

**Annex 3. 특수비 (Special Costs)**
- 14. 광고/홍보 마케팅
- 15. 추가 소모품
- 16. 영업 및 출장비
- 17. 보험 및 보상비
- 18. 기타
- 특수비 소계 (c) [auto-sum]

비용 총액 (B = a+b+c) [auto-sum]
영업이익 (A-B) shown with green/red color

Each sub-section has:
- Excel upload button for that section
- Download template button

### 5. Tab 3: 호실 정보 (Room Management)
Pre-loaded with all 43 rooms from KIMS HOMES:
Room list (No, 층, 호실, 성함, 분양면적, 분양가격, 은행명, 계좌번호, 위탁자):
1,2,205,박재운,110.36,286000000,농협,351-0659-9244-23,김인옥
2,2,206,박재운,110.36,286000000,농협,351-0659-9244-23,김인옥
3,2,212,박재운,110.36,286000000,농협,351-0659-9244-23,공민우
4,2,214,박재운,110.36,286000000,농협,351-0659-9244-23,최종희
5,3,309,박재운,110.36,286000000,농협,351-0659-9244-23,공정숙
,3,313,박재운,110.36,286000000,농협,351-0659-9244-23,이귀애
,3,314,박재운,110.36,286000000,농협,351-0659-9244-23,이귀애
6,4,418,박재운,110.36,286000000,농협,351-0659-9244-23,박정희
7,5,502,박재운,110.36,286000000,농협,351-0659-9244-23,박진성
8,5,503,박재운,110.36,286000000,농협,351-0659-9244-23,문길순
9,5,510,박재운,110.36,286000000,농협,351-0659-9244-23,마이파파
,5,519,박재운,110.36,286000000,농협,351-0659-9244-23,오재연
10,6,602,박재운,110.36,286000000,농협,351-0659-9244-23,김형일
11,6,619,박재운,110.36,286000000,농협,351-0659-9244-23,권선아
12,7,706,박재운,110.36,286000000,농협,351-0659-9244-23,신병준
13,7,713,박재운,110.36,286000000,농협,351-0659-9244-23,송하숙
14,7,714,박재운,110.36,286000000,농협,351-0659-9244-23,신병준
15,8,816,박재운,110.36,286000000,농협,351-0659-9244-23,이강진
16,8,817,박재운,110.36,286000000,농협,351-0659-9244-23,이강진
17,9,906,박재운,110.36,286000000,농협,351-0659-9244-23,장금만
18,9,911,박재운,110.36,286000000,농협,351-0659-9244-23,하나공조시스템
19,9,917,박재운,110.36,286000000,농협,351-0659-9244-23,공정숙
20,11,1106,박재운,110.36,286000000,농협,351-0659-9244-23,장금만
21,11,1116,박재운,110.36,286000000,농협,351-0659-9244-23,송하숙
22,12,1205,박재운,110.36,286000000,농협,351-0659-9244-23,문길순
23,12,1209,박재운,110.36,286000000,농협,351-0659-9244-23,하나공조시스템
24,12,1210,박재운,110.36,286000000,농협,351-0659-9244-23,태경란
25,12,1218,박재운,110.36,286000000,농협,351-0659-9244-23,송하숙
26,13,1301,박재운,110.36,286000000,농협,351-0659-9244-23,오현진
27,13,1308,박재운,110.36,286000000,농협,351-0659-9244-23,이진화
28,13,1313,박재운,110.36,286000000,농협,351-0659-9244-23,이원오
29,13,1314,박재운,110.36,286000000,농협,351-0659-9244-23,이원오
30,14,1418,박재운,110.36,286000000,농협,351-0659-9244-23,김종
31,15,1505,박재운,110.36,286000000,농협,351-0659-9244-23,최은심
32,15,1518,박재운,110.36,286000000,농협,351-0659-9244-23,하나공조시스템
33,16,1607,박재운,110.36,286000000,농협,351-0659-9244-23,송하숙
34,17,1702,박재운,110.36,286000000,농협,351-0659-9244-23,오현진
35,17,1704,박재운,110.36,286000000,농협,351-0659-9244-23,송하숙
36,17,1711,박재운,110.36,286000000,농협,351-0659-9244-23,정미자
37,17,1712,박재운,110.36,286000000,농협,351-0659-9244-23,정미자
38,17,1713,박재운,110.36,286000000,농협,351-0659-9244-23,정미자
39,18,1801,박재운,110.36,286000000,농협,351-0659-9244-23,김혜정
40,18,1802,박재운,110.36,286000000,농협,351-0659-9244-23,김혜정

Each room also has editable fields:
- 확정금, 법인부담금, 객실사용요금, 누적미수금, 선지급금, 미지급금, 수익금 (can be overridden or auto-calculated)
- 수익형/관리형 구분 checkbox
- 수익배분율 dropdown: 100%, 80%, 60%

수익형/관리형 호실 count shown at top.
호실 수익금 = 영업이익 / 수익형호실수 × 배분율 (auto-calculated when profit is positive)

Download room template button.

### 6. Tab 4: 성과보고서 (Performance Report Preview)
Read-only formatted preview showing:
- KIMS HOMES {year}년 {month}월 성과보고
- 매출현황 table (OTA/현장/총액)
- 채널별 매출 breakdown table
- 비용구조 table (Annex1/2/3 with subtotals)
- 영업이익 summary
- 호실당 기준수익 (100%/80%/60%)
- 수익형/관리형 호실 현황

### 7. Tab 5: 정산배분표 (Distribution Table Preview)
Read-only formatted table:
- {year}년 {month}월 정산배분
- All 43 rooms with: No, 층, 호실, 성함, 분양면적, 분양가격, 은행명, 계좌번호, 위탁자, 확정금, 법인부담금, 객실사용요금, 누적미수금, 선지급금, 미지급금, 수익금, 지급금, 부가세, 실지급수익금(VAT포함)
- Totals row at bottom

### 8. Download Section (floating bottom bar or dedicated panel)
Buttons:
- 📥 Excel 다운로드 (성과보고 + 정산배분 2개 시트)
- 📄 PDF 다운로드 (성과보고 + 정산배분)
- 📝 성과보고 PDF
- 📝 정산배분 PDF

### 9. Template Downloads
In each tab, provide download buttons for section-specific Excel templates:
- 매출보고서 템플릿.xlsx (channels as rows, one amount column)
- 고정비 템플릿.xlsx
- 변동비 템플릿.xlsx  
- 특수비 템플릿.xlsx
- 호실정보 템플릿.xlsx

## Calculation Logic

`
영업이익 = 매출총액(A) - 비용총액(B)
호실당기준수익 = 영업이익 / 수익형호실수  (if positive)
수익금(100%) = 기준수익
수익금(80%) = 기준수익 × 0.8
수익금(60%) = 기준수익 × 0.6
지급금 = 수익금 - 누적미수금 - 선지급금
부가세 = 지급금 × 0.1
실지급수익금 = 지급금 + 부가세
`

## Default Values (pre-fill)
- 렌탈(정수기/비데): 50,000원 × 11대 = 550,000
- 24시 관제: 3,300,000
- 관리비: 3,600,000
- 광고/홍보: 2,200,000
- 영업출장비: 150,000
- 기장료: 165,000

## Data Persistence
- Auto-save to localStorage (key: kimstay_settlement_{year}_{month})
- Load saved data when switching months
- "저장된 데이터 불러오기" toast notification when loading

## UI/UX
- Korean language throughout
- Mobile-friendly responsive layout
- Numbers formatted as Korean won (₩ or 원 with commas)
- Color coding: green for profit, red for loss
- Section headers with light blue background (#D9E1F2)
- Total rows with yellow background (#FFFF99)
- Tooltips on hover for field descriptions
- Input validation (numbers only, no negative costs)

## Excel Upload Parsing
When user uploads xlsx for sales:
- Look for channel names in any column
- Match keywords: 야놀자, 에어비앤비, 아고다, 익스피디아, 부킹, 트립, 네이버, 여기어때
- Extract numeric values from adjacent cells
- Show parsed results and ask user to confirm

## Important
- The entire app must work as a single index.html file
- No backend, no npm, no build step
- Must work when opened directly in a browser (file:// protocol)
- All CDN libraries loaded from unpkg or cdnjs
- Korean fonts: use Google Fonts Noto Sans KR

Create index.html in the current directory.

When completely finished, run this command:
openclaw system event --text "KIMS HOMES 수익금정산 웹앱 완성! workspace/kimstay-settlement/index.html" --mode now
