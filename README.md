# Brickbot FAQ

`[2026][2권역]중등강사진` 단톡방의 최근 24시간 대화에서 공개 가능한 FAQ만 정리하는 정적 사이트입니다.

## 공개 원칙

- 카카오톡 원문, 작성자명, 메시지 ID를 저장하지 않습니다.
- 개인정보, 비밀번호, 인증정보를 게시하지 않습니다.
- 운영에 필요한 링크는 명시적으로 승인된 주소만 게시하고 검증 스크립트의 허용 목록으로 관리합니다.
- 일일 FAQ는 검증 스크립트를 통과한 경우에만 배포합니다.
- 랜딩 화면에서 접속 코드 확인 후 FAQ 화면을 표시합니다. 정적 GitHub Pages의 클라이언트 측 확인이므로 보안 경계로 간주하지 않습니다.
- 비밀번호·인증정보·개인정보는 접속 코드와 무관하게 게시하지 않습니다.

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
