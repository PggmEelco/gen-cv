import json

import pandas as pd

df = pd.read_excel("./data/pggm_QnA.xlsx", sheet_name="Answers")


def get_documents(df: pd.DataFrame) -> dict[str, str]:
    for _, row in df.iterrows():
        questions = json.loads(row.Questions)
        answer = row.Text
        if questions[0]["Text"].strip().endswith("?"):
            yield {
                "question": questions[0]["Text"],
                "answer": answer if isinstance(answer, str) else "",
                "keywords": " ".join({item["Text"] for item in questions[1:]}),
            }


with open("data/pggm_QnA.ndjson", "w", encoding="utf8") as outf:
    for doc in get_documents(df):
        outf.write(f"{json.dumps(doc)}\n")
