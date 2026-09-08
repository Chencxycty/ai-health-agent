from pydantic import BaseModel, Field


class BMIInput(BaseModel):
    """BMI（Body Mass Index，身体质量指数）输入数据模型。用于计算BMI值。(约束条件：身高范围为0-300厘米，体重范围为0-500公斤)"""

    height_cm: float = Field(gt=0, le=300)
    weight_kg: float = Field(gt=0, le=500)


class BloodPressureReading(BaseModel):
    """血压读数数据模型。用于计算平均血压值。(约束条件：收缩压范围为0-300毫米汞柱，舒张压范围为0-200毫米汞柱)"""

    systolic: float = Field(gt=0, le=300)
    diastolic: float = Field(gt=0, le=200)


class AverageBloodPressureInput(BaseModel):
    """平均血压输入数据模型。用于计算平均血压值。(约束条件：至少包含一个血压读数)"""

    readings: list[BloodPressureReading]


class AverageGlucoseInput(BaseModel):
    """平均血糖输入数据模型。用于计算平均血糖值。(约束条件：至少包含一个血糖值)"""

    values: list[float]
