# TC Manager - 카테고리 참조 데이터 (실 데이터 기반)

> 출처: Google Spreadsheet `1lgSbr5C2tTYXFw38P3I_ToNv2QtYjF-yDYN1mNtCWIg`
> 총 52개 TC 시트에서 추출 (메타/유틸 시트 제외)

---

## 1. 시트(Suite) 구조 및 거래소 분기 패턴

### 시트명 = Suite 코드

각 시트는 하나의 Suite에 대응합니다. 시트명 자체가 Suite의 식별자 역할을 합니다.

### 거래소별 분기 패턴

시트명에 `(거래소명)` 접미사가 붙으면 해당 거래소 전용 TC입니다.

```
{SuiteName}              → 공통 TC (모든 거래소 적용)
{SuiteName}(거래소)       → 해당 거래소 전용 TC
{SuiteName}(거래소A,거래소B)  → 복수 거래소 공유 TC
{SuiteName}(통합)         → 통합 시트 (모든 거래소 공통이지만 거래소별 차이가 있는 항목)
```

### 거래소 목록 (코드)

| 거래소 | 시트에서 사용하는 이름 |
|--------|----------------------|
| Bitget | Bitget |
| Gate | Gate |
| Hyperliquid | Hyperliquid |
| Bybit | Bybit |
| OKX | OKX |

### 거래소별 분기 현황

| Suite 기본명 | 공통 | 거래소별 시트 |
|-------------|------|-------------|
| 거래소 연동 | - | (Bitget), (Gate), (Hyperliquid), (Bybit), (OKX) |
| Trade-Account Info | O | (Hyperliquid) |
| Trade-Chart | O | (OKX,Bybit) |
| Trade-MarginMode | O | (OKX), (Hyperliquid), (Bybit) |
| Trade-Leverage | - | (통합), (Bitget), (Gate), (Hyperliquid), (OKX,Bybit) |
| Trade-Order | O | (통합), (Hyperliquid) |
| Trade-TPSL | O | (OKX,Bybit) |
| Trade-Close | O | (Bitget,Hyperliquid) |
| Trade-Full_TPSL | O | (OKX,Bybit) |
| Trade-Open_Orders | O | (OKX,Bybit) |
| Trade-Order_History | O | (Gate), (Hyperliquid) |
| Trade-Trade_History | O | (Hyperliquid) |

---

## 2. 전체 Suite 목록 및 카테고리 트리

### 거래소 무관 Suite

---

### Landing Page

```
대분류: 공통
  중분류: SEO
  중분류: 오픈그래프
  중분류: 접속

대분류: GNB
  중분류: ABOUT
  중분류: FEATURES
  중분류: LAUNCH APP
  중분류: MAIN
  중분류: VALUE
  중분류: 로고
  중분류: 로고 클릭

대분류: Hero Section (MAIN)
  중분류: Join Waitlist
  중분류: Open Beta
  중분류: START TRADING
  중분류: 타이틀

대분류: Join Waitlist
  중분류: 로그인
  중분류: 사전 등록
  중분류: 이메일 등록
  중분류: 쿠폰 등록

대분류: ABOUT
  중분류: 소개

대분류: FEATURE
  중분류: 서비스 소개

대분류: VALUE
  중분류: 소개

대분류: 하단
  중분류: Open beta service is starting 버튼
  중분류: SNS
  중분류: 타이틀

대분류: Footer
  중분류: SNS
  중분류: 약관
  중분류: 저작권

대분류: 반응형
  중분류: Desktop
  중분류: Laptop
  중분류: Mobile
  중분류: Tablet
```

---

### 접속

```
대분류: 공통
  중분류: PC
  중분류: 모바일/태블릿
  중분류: 반응형
  중분류: 오픈그래프
```

---

### GNB&Footer

```
대분류: GNB
  중분류: Docs 메뉴
  중분류: Event Zone 메뉴
  중분류: GNB 메뉴
  중분류: Log in 버튼
  중분류: Points 메뉴
  중분류: Trade 메뉴
  중분류: Trading Performance 메뉴
  중분류: 계정 드롭다운
  중분류: 로고

대분류: Footer
  중분류: Support Center
  중분류: 거래소 연결 상태
  중분류: 버전
  중분류: 소셜 미디어
  중분류: 약관
```

---

### 로그인

```
대분류: 접속
  중분류: 파트너 코드 링크

대분류: 로그인 동작
  중분류: 로그인 동기화
  중분류: 로그인 세션
  중분류: 로그인 시간
  중분류: 화면 새로고침

대분류: Log in
  중분류: Google 로그인
  중분류: email 로그인
  중분류: 로그인 모달
  중분류: 약관 동의

대분류: Wallet 로그인
  중분류: Coinbase Wallet
  중분류: Hana Wallet
  중분류: MetaMask
  중분류: OKX Wallet
  중분류: Rabby Wallet
  중분류: Trust Wallet
```

---

### Settings

```
대분류: Settings
  중분류: Export private key
  중분류: Manage Exchange Connections
  중분류: Profile
  중분류: Referral Status
  중분류: 계정 이름 수정 모달
  중분류: 로그아웃
  중분류: 타이틀
```

---

### Youthmeta

```
대분류: Log in - 일반 계정
  중분류: 일반 계정

대분류: Log in - youthmeta 계정
  중분류: youthmeta 계정
```

---

### Points

```
대분류: Points
  중분류: 요약 정보
  중분류: 히스토리
  중분류: 접속
```

---

### Trading Performance

```
대분류: Trading Performance
  중분류: Earning Analysis
  중분류: Period Summary
  중분류: Trading Summary
  중분류: 접속
```

---

### Event Zone

```
대분류: Event Zone
  중분류: Main
  중분류: Point Mission
  중분류: 접속
```

---

### Trade 관련 Suite (공통)

---

### Trade-Account Info

```
대분류: 거래소 연동 전
  중분류: 정보 표시

대분류: 거래소 연동 후
  중분류: Total Equity
  중분류: 정보 표시
```

---

### Trade-Deposit&Withdraw

```
대분류: Deposit&Withdraw
  중분류: 공통
  중분류: 입금
  중분류: 출금
```

---

### Trade-PositionMode

```
대분류: Position Mode
  중분류: Net Mode
  중분류: 기본
```

---

### Trade-Coin Info

```
대분류: Coin Info
  중분류: 공통
  중분류: 기본 정보
  중분류: 펀딩비 정보
```

---

### Trade-Chart

```
대분류: Chart
  중분류: 설정
  중분류: 차트 기능
  중분류: 초기 상태
```

---

### Trade-Orderbook

```
대분류: Orderbook
  중분류: Asks
  중분류: Bids
  중분류: 공통
  중분류: 탭
```

---

### Trade-MarginMode

```
대분류: MarginMode
  중분류: Cross
  중분류: Isolated
  중분류: 기본
```

---

### Trade-Order

```
대분류: 공통
  중분류: 주문 영역 공통

대분류: Market Order
  중분류: 매도
  중분류: 매수

대분류: Limit Order
  중분류: 매도
  중분류: 매수

대분류: Conditional Order
  중분류: 매도
  중분류: 매수
```

---

### Trade-TPSL

```
대분류: TP/SL
  중분류: Take Profit
  중분류: Stop Loss
  중분류: 공통
```

---

### Trade-Positions

```
대분류: 포지션 목록
  중분류: 공통
  중분류: 포지션 카드
  중분류: 포지션 없음
```

---

### Trade-Close

```
대분류: Close
  중분류: 청산 공통
  중분류: Market Close
  중분류: Limit Close
```

---

### Trade-Full_TPSL

```
대분류: Full TP/SL
  중분류: Take Profit
  중분류: Stop Loss
  중분류: 공통
```

---

### Trade-Partial_TPSL

```
대분류: Partial TP/SL
  중분류: Take Profit
  중분류: Stop Loss
  중분류: 공통
```

---

### Trade-Open_Orders

```
대분류: Open Orders
  중분류: 공통
  중분류: 주문 카드
  중분류: 주문 수정
  중분류: 주문 취소
```

---

### Trade-Order_History

```
대분류: Order History
  중분류: 공통
  중분류: 필터
  중분류: 주문 상세
```

---

### Trade-Trade_History

```
대분류: Trade History
  중분류: 공통
  중분류: 필터
  중분류: 거래 상세
```

---

### Trade-Position_History

```
대분류: Position History
  중분류: 공통
  중분류: 필터
  중분류: 포지션 상세
```

---

### Trade-P&L_History

```
대분류: P&L History
  중분류: 공통
  중분류: 필터
  중분류: P&L 상세
```

---

### CBT_Whitelist

```
대분류: CBT Whitelist
  중분류: 화이트리스트 관리
```

---

## 3. 카테고리 네이밍 규칙 (실 데이터에서 관찰)

### 대분류 네이밍 패턴

| 패턴 | 예시 | 설명 |
|------|------|------|
| 영문 기능명 | `Chart`, `Orderbook`, `MarginMode` | Trade 관련 기능 |
| 한글 기능명 | `로그인 동작`, `포지션 목록` | 한글 사용 |
| 영문+한글 혼합 | `Log in`, `Wallet 로그인` | 영문 기능 + 한글 설명 |
| 공통 | `공통` | Suite 전체에 적용되는 공통 TC |
| 접속 | `접속` | 페이지 접속 관련 |
| 반응형 | `반응형` | 반응형 UI 관련 |

### 중분류 네이밍 패턴

| 패턴 | 예시 | 설명 |
|------|------|------|
| 기능 동작 | `매수`, `매도`, `청산` | 사용자 액션 기반 |
| UI 영역 | `타이틀`, `버전`, `탭` | UI 컴포넌트/영역 |
| 상태 기반 | `거래소 연동 전`, `포지션 없음` | 조건/상태 구분 |
| 영문 용어 | `Take Profit`, `Stop Loss`, `Cross`, `Isolated` | 거래 전문 용어 |
| 서비스명 | `Google 로그인`, `MetaMask` | 외부 서비스/지갑 이름 |

### 소분류 네이밍 패턴

| 패턴 | 예시 | 설명 |
|------|------|------|
| UI 요소 | `닫기 버튼`, `Edit 버튼` | 버튼/입력 등 |
| 테스트 조건 | `유효한 이메일`, `잘못된 쿠폰 코드 입력` | 정상/비정상 |
| 상태 | `로그인`, `로그아웃`, `연동 완료` | 시스템 상태 |
| 해상도 | `1920px 이상`, `767px-480px` | 반응형 해상도 |

---

## 4. TC Generator 연동 규칙 요약

### Suite 매핑

- 시트명(괄호 제외)을 Suite 코드로 사용
- 괄호 안 거래소명은 Exchange 매핑에 사용
- `(통합)` 접미사는 공통 TC로 처리

### 대분류/중분류 문구 일치

- **TC Generator가 출력하는 대분류/중분류 텍스트는 위 참조 데이터와 정확히 일치해야 합니다**
- 대소문자, 공백, 특수문자 모두 동일하게 맞춰야 함
- 새로운 대분류/중분류 추가 시 TC Manager Import에서 자동 생성됨

### 소분류

- 자유 텍스트이므로 TC Generator가 자유롭게 생성 가능
- 다만 기존 소분류와 일관성을 위해 위 참조 데이터의 패턴을 따르는 것을 권장

### 거래소 매핑

```
시트명: Trade-Order              → Exchange: (없음, 공통)
시트명: Trade-Order(Hyperliquid) → Exchange: Hyperliquid
시트명: Trade-Chart(OKX,Bybit)   → Exchange: OKX, Bybit
시트명: Trade-Leverage(통합)      → Exchange: (없음, 공통)
```
