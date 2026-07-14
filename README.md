# Brickbot FAQ

`[2026][2권역]중등강사진` 단톡방의 최근 24시간 대화에서 공개 가능한 FAQ만 정리하는 정적 사이트입니다.

## 공개 원칙

- 카카오톡 원문, 작성자명, 메시지 ID를 저장하지 않습니다.
- 개인정보, 비밀번호, 인증정보, 내부 링크를 게시하지 않습니다.
- 내부 자료는 `단톡방 종합안내에서 확인`하도록 안내합니다.
- 일일 FAQ는 검증 스크립트를 통과한 경우에만 배포합니다.

## 로컬 확인

```bash
python3 -m http.server 4173
```

브라우저에서 `http://localhost:4173`을 엽니다.

## 검증

```bash
python3 scripts/rebuild_index.py
python3 scripts/validate_public_site.py
```

## 배포

`main` 브랜치 push 시 GitHub Actions가 GitHub Pages에 배포합니다.
