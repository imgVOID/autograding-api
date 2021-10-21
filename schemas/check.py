from pydantic import BaseModel


class CheckResult(BaseModel):
    """
    `CheckResult` is a pydantic model defining the schema
    for displaying a Docker check result.
    """
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
