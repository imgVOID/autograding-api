from pydantic import BaseModel


class CheckResult(BaseModel):
    answer: str
    your_result: str
    status: str

    class Config:
        schema_extra = {
            "example": {
                "answer": "Expected code output.",
                "your_result": "Actual code output.",
                "status": "OK or WRONG",
            }
        }
