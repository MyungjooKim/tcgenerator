# TC Manager - TC ID 체계 및 카테고리 규칙

TC Manager에서 사용하는 TC ID 생성 규칙, 카테고리 구조, 버전 관리 체계를 정리한 문서입니다.
TC Generator 프로그램에서 TC를 생성할 때 이 규칙을 따라야 합니다.

---

## 1. 전체 계층 구조

```
Project (프로젝트)
  └── Suite (스위트)
        ├── Category1 (대분류)
        │     └── Category2 (중분류)
        │           └── TestCase (TC)
        │                 └── category3 (소분류) — 자유 텍스트
        └── TestCase.seqNumber (Suite 내 일련번호)
```

---

## 2. TC ID 체계

### 형식

```
{ProjectCode}-{SuiteCode}-{SeqNumber}
```

### 구성 요소

| 구성 | 설명 | 예시 |
|------|------|------|
| ProjectCode | 프로젝트 코드 (대문자 영숫자) | `SC`, `BN` |
| SuiteCode | Suite 코드 (영숫자 + 하이픈 허용) | `ORD`, `TRD-MRGN` |
| SeqNumber | Suite 내 일련번호 (3자리 zero-padding) | `001`, `012`, `100` |

### 예시

```
SC-ORD-001          → Project: SC, Suite: ORD, Seq: 1
SC-TRD-MRGN-012     → Project: SC, Suite: TRD-MRGN, Seq: 12
SC-AUTH-100          → Project: SC, Suite: AUTH, Seq: 100
BN-ORD-003           → Project: BN, Suite: ORD, Seq: 3
```

### ID 생성 로직

```typescript
function buildTcId(projectCode: string, suiteCode: string, seq: number): string {
  return `${projectCode}-${suiteCode}-${String(seq).padStart(3, "0")}`;
}
```

### ID 파싱 규칙

- 마지막 하이픈(-)으로 구분된 숫자 부분 = SeqNumber
- 첫 번째 하이픈 앞 = ProjectCode
- 중간 나머지 전체 = SuiteCode (하이픈 포함 복원)

```
SC-TRD-MRGN-012
 │    │       │
 │    │       └─ SeqNumber: 12
 │    └───────── SuiteCode: TRD-MRGN (하이픈 포함)
 └────────────── ProjectCode: SC
```

### 주의사항

- SeqNumber가 1000 이상이면 zero-padding 없이 그대로 표기 (예: `SC-ORD-1000`)
- ProjectCode 비교는 **대소문자 무시** (`sc` = `SC`)
- TC ID는 **전역 고유** (프로젝트가 달라도 중복 불가)

---

## 3. Project (프로젝트)

| 필드 | 규칙 |
|------|------|
| name | 자유 텍스트 (예: "Supercycl") |
| code | 대문자 영숫자, **전역 고유** (예: "SC", "BN") |

---

## 4. Suite (스위트)

| 필드 | 규칙 |
|------|------|
| code | 영숫자 + 하이픈 허용, **프로젝트 내 고유** |
| name | 자유 텍스트 (예: "Margin Trading") |
| displayOrder | 정수, 표시 순서 |
| deletedAt | soft delete 지원 |

### Suite 코드 규칙

- 단일 코드: `ORD`, `AUTH`, `WLLT`
- 복합 코드 (하이픈 포함): `TRD-MRGN`, `TRD-SPOT`
- TC ID의 중간 부분에 그대로 포함됨
- 대소문자 구분함

### Suite 코드 예시

```
ORD          → 주문 관련
TRD-MRGN     → 거래-마진
TRD-SPOT     → 거래-현물
AUTH         → 인증
WLLT         → 지갑
```

---

## 5. Category1 (대분류)

| 필드 | 규칙 |
|------|------|
| name | 자유 텍스트, **Suite 내 고유** (대소문자 구분) |
| displayOrder | 정수, 표시 순서 |
| deletedAt | soft delete 지원 |

### 규칙

- 같은 Suite 안에서 동일 이름 불가 (DB unique: `[suiteId, name]`)
- 대소문자 구분: "Trading" ≠ "trading"
- Import 시에는 대소문자 무시로 매칭하되, 생성 시에는 원본 대소문자 유지

### 예시

```
Suite: TRD-MRGN (Margin Trading)
  ├── 대분류: 로그인         (로그인 관련 TC들)
  ├── 대분류: 주문 생성       (주문 생성 관련 TC들)
  └── 대분류: 포지션 관리     (포지션 관련 TC들)
```

---

## 6. Category2 (중분류)

| 필드 | 규칙 |
|------|------|
| name | 자유 텍스트, **대분류 내 고유** (대소문자 구분) |
| displayOrder | 정수, 표시 순서 |
| deletedAt | soft delete 지원 |

### 규칙

- 같은 Category1 안에서 동일 이름 불가 (DB unique: `[category1Id, name]`)
- TC는 반드시 하나의 Category2에 연결 (필수 FK)

### 예시

```
Suite: TRD-MRGN
  └── 대분류: 주문 생성
        ├── 중분류: 시장가       (시장가 주문 관련 TC들)
        ├── 중분류: 지정가       (지정가 주문 관련 TC들)
        └── 중분류: 조건부       (조건부 주문 관련 TC들)
```

---

## 7. Category3 (소분류)

| 필드 | 규칙 |
|------|------|
| category3 | nullable 자유 텍스트, 구조 없음 |

### 규칙

- **유일성 제약 없음** (같은 값 여러 TC에서 사용 가능)
- **TC ID에 포함되지 않음** (순수 메타데이터)
- 선택 사항 (null 또는 빈 문자열 가능)
- 동일 중분류 내에서 기존 소분류 값을 참고용으로 제안

### 예시

```
Suite: TRD-MRGN
  └── 대분류: 주문 생성
        └── 중분류: 시장가
              ├── TC: SC-TRD-MRGN-001 (소분류: "정상 케이스")
              ├── TC: SC-TRD-MRGN-002 (소분류: "정상 케이스")
              └── TC: SC-TRD-MRGN-003 (소분류: "예외 케이스")
```

---

## 8. SeqNumber (일련번호)

### 규칙

- Suite 내에서 고유 (같은 Suite에 동일 번호 불가)
- 자동 채번: 해당 Suite의 `max(seqNumber) + 1`
- 수동 지정 가능 (충돌 시 409 에러)
- 삭제된 번호는 재사용되지 않음 (자동 채번 시)
- TC ID에 3자리 zero-padding으로 표기

### 채번 알고리즘 (신규 생성 시)

```
Suite 내 사용 중인 seqNumber: {1, 2, 5, 7}
→ 자동 채번 시 next-seq 방식: 빈 번호부터 (3)
→ 또는 max+1 방식: 8
```

---

## 9. 버전 관리

### 필드

| 필드 | 초기값 | 설명 |
|------|--------|------|
| versionMajor | 1 | 주 버전 (QA 재확인 필요한 변경) |
| versionMinor | 0 | 부 버전 (경미한 변경) |

### 버전 증가 규칙

| 변경 유형 | 동작 | 예시 |
|-----------|------|------|
| Major 변경 | versionMajor++, versionMinor=0, engineerChecked=false | v1.0 → v2.0 |
| Minor 변경 | versionMinor++ | v1.0 → v1.1, v2.3 → v2.4 |
| 비QA 변경 | 버전 유지 | 자동화 상태 변경 등 |

### QA 추적 필드 (변경 시 버전 관리 대상)

- category2Id, category3
- precondition, steps, expectedResult
- priority, isExchangeSpecific

---

## 10. 거래소 (Exchange) 매핑

### 규칙

- TC에 거래소 매핑이 **없으면** = 공통 TC (모든 거래소 적용)
- TC에 거래소 매핑이 **있으면** = 해당 거래소 전용 TC
- 전체 거래소를 모두 선택 → 공통 TC로 정규화 (매핑 삭제)

### 거래소 코드

```
BN    → Binance
OKX   → OKX
UPB   → Upbit
```

---

## 11. Import 시트 컬럼 구조

TC Generator에서 생성하는 시트는 다음 컬럼 구조를 따릅니다.

```
A: TC ID (또는 Suite 접두사)
B: 대분류 (Category1)
C: 중분류 (Category2)
D: 소분류 (Category3) [선택]
E~H: 사전조건 / 테스트 스텝 / 기대결과 / 중요도
I: 관련 거래소 [선택]
```

### 셀 병합 / Forward-Fill 규칙

- 대분류, 중분류, 소분류: 빈 셀이면 **이전 행 값을 이어받음**
- 사전조건, 스텝, 기대결과: 빈 셀이면 **이전 행 값을 이어받음**
- 중요도: 빈 셀이면 **기본값 MEDIUM** (이어받지 않음)
- 거래소: 빈 셀이면 **공통 TC** (이어받지 않음)

### 중요도 키워드 매핑

| 값 | 매핑 |
|----|------|
| HIGH, 높음 | HIGH |
| MEDIUM, 보통 | MEDIUM |
| LOW, 낮음 | LOW |

### TC ID 컬럼 규칙

```
SC-ORD-001       → 기존 TC 업데이트 (숫자로 끝남)
SC-ORD           → 신규 TC 생성 (숫자 없음 = Suite 접두사)
SC-TRD-MRGN      → 신규 TC 생성 (TRD-MRGN Suite)
```

- 마지막 하이픈 뒤가 숫자 → 기존 TC ID (업데이트 대상)
- 마지막 하이픈 뒤가 문자 → Suite 접두사 (신규 생성, 자동 채번)

### 거래소 컬럼 파싱

- 콤마(,), 세미콜론(;), 공백으로 구분
- 대소문자 무시 매칭
- 빈 값 = 공통 TC

```
BN,OKX          → Binance, OKX 전용
BN              → Binance 전용
(빈 값)          → 공통 TC
```

---

## 12. TC Generator 연동 시 체크리스트

TC Generator에서 TC를 생성할 때 다음 사항을 반드시 확인하세요.

1. **TC ID 형식**: `{ProjectCode}-{SuiteCode}-{Seq}` 또는 신규 시 `{ProjectCode}-{SuiteCode}` (접두사만)
2. **Suite 코드**: TC Manager에 등록된 Suite 코드와 정확히 일치 (없으면 Import 시 자동 생성 가능)
3. **대분류 이름**: 같은 Suite 내 기존 대분류와 동일한 문자열 사용 (대소문자 주의)
4. **중분류 이름**: 같은 대분류 내 기존 중분류와 동일한 문자열 사용
5. **소분류**: 자유 텍스트, 일관성을 위해 기존 값 참고 권장
6. **중요도**: HIGH/MEDIUM/LOW 또는 높음/보통/낮음
7. **거래소**: 등록된 Exchange 코드 사용, 빈 값이면 공통 TC
8. **시트 컬럼 순서**: A(TC ID) B(대분류) C(중분류) D(소분류) E~H(내용) I(거래소) 순서 준수
