from pymongo import ASCENDING, DESCENDING
from typing import Optional, Callable
from datetime import datetime

from utils_hj3415 import tools, setup_logger
from db_hj3415.mymongo.corps import Corps
from chatgpt_hj3415 import gpt, message_maker


mylogger = setup_logger(__name__,'WARNING')


class AIReport(Corps):
    def __init__(self, code: str):
        super().__init__(code=code, page='ai_report')

    @classmethod
    def _save(cls, code: str, temperature: float, content: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        client = cls.get_client()
        page = 'ai_report'

        # MongoDB는 datetime.date 타입을 저장할 수 없고 datetime.datetime만 허용
        today = datetime.today()
        report_date = datetime(today.year, today.month, today.day)

        client[code][page].create_index([('report_date', ASCENDING)], unique=True)

        # 덮어쓰기 (업서트)
        client[code][page].update_one(
            {"report_date": report_date},  # 조건: 오늘 날짜
            {
                "$set": {
                    "temperature": temperature,
                    "content": content
                }
            },
            upsert=True  # 없으면 insert, 있으면 update
        )

    @classmethod
    def save_with_progress(cls, code: str, temperature = 0.7, on_progress: Callable[[dict], None] | None = None) -> dict:
        assert tools.is_6digit(code), f'Invalid value : {code}'

        # ── 헬퍼 ─────────────────────────────────────────
        def report(pct: int, snippet: str | None = None):
            if on_progress:
                payload = {"progress": pct}
                if snippet is not None:
                    payload["content"] = snippet
                on_progress(payload)

        # 0 % → 10 %
        report(0, "작업을 시작합니다.")
        messages = message_maker.make_messages(code)
        report(10, "인공지능에게 문의중...")

        # GPT 스트리밍 (단일 쿼리)
        token_cnt, pct = 0, 10
        snippet_buf = ""

        stream = gpt.call_stream(messages, temperature)
        try:
            while True:
                delta = next(stream)  # 토큰 단위
                snippet_buf += delta
                token_cnt += 1

                # 20토큰마다 1 % 상승, 최대 90 %
                if token_cnt % 20 == 0 and pct < 90:
                    pct += 1
                    report(pct, snippet=snippet_buf[-400:])
        except StopIteration as st:
            content = st.value  # GPT 전체 답변

        # 90 % → 99 %
        report(90, "데이터베이스에 저장중…")
        AIReport._save(code, temperature, content)
        report(99, content)

        return {
            "temperature": temperature,
            "content": content,
        }

    def get_recent_date(self) -> Optional[datetime]:
        """
        저장된 보고서 중 가장 최근 report_date 를 반환.
        저장 문서가 하나도 없으면 None 반환.
        """
        # report_date 내림차순 정렬 후 맨 위 문서 하나 조회
        doc = self._col.find_one(
            {},  # 조건 없음 (컬렉션 전체)
            sort=[("report_date", DESCENDING)],  # 최신순
            projection={"_id": 0, "report_date": 1}
        )

        return doc["report_date"] if doc else None

    def get_recent(self) -> Optional[str]:
        """
        저장된 AI 리포트 중 가장 최근 날짜의 content를 반환.
        없으면 None 반환.
        """
        # 가장 최근(report_date DESC) 한 건 조회
        doc = self._col.find_one(
            {},  # 조건: 해당 종목 전체
            {"_id": 0, "content": 1},  # projection: content만
            sort=[("report_date", DESCENDING)]  # 최신순 정렬
        )

        return doc["content"] if doc else None
