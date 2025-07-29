from enum import Enum

from pydantic import BaseModel, Field

from backend.fixtures.time import is_date_string


class TakoDataFormatValueType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    FLOAT = "float"
    NULL = "null"
    ANY = "any"

    def is_numeric(self) -> bool:
        return self in [TakoDataFormatValueType.NUMBER, TakoDataFormatValueType.FLOAT]


class TakoDataFormatCellValue(BaseModel):
    variable_name: str = Field(
        description="The name of the variable",
        examples=["Company", "Revenue"],
    )
    value: str | int | float | bool | None = Field(
        description="The value of the variable. "
        "If the variable is a date, format it as an ISO 8601 string.",
        examples=["Apple", 1000000],
    )


class TakoDataFormatRowValues(BaseModel):
    cell_values: list[TakoDataFormatCellValue] = Field(
        description="Each cell contains a single aspect (variable + value)",
        examples=[
            [
                {"variable_name": "Company", "value": "Apple"},
                {"variable_name": "Revenue", "value": 1000000},
            ]
        ],
    )


class TakoDataFormatVariable(BaseModel):
    # Variable contains rich metadata about the variables for each observation
    name: str = Field(
        description="The human friendly name of the column variable",
        examples=["Company", "Revenue"],
    )
    type: TakoDataFormatValueType = Field(
        description="The type of the column variable",
        examples=[TakoDataFormatValueType.STRING, TakoDataFormatValueType.NUMBER],
    )
    units: str | None = Field(
        description="The units of the variable in the data",
        examples=["USD", "EUR"],
        default=None,
    )
    is_sortable: bool | None = Field(
        description="Whether the data is sortable by this variable",
        default=None,
    )
    is_higher_better: bool | None = Field(
        description="Whether a higher value of this variable is better",
        default=None,
    )

    def is_numeric(self) -> bool:
        return self.type.is_numeric()


class TakoDataFormatQuantitativeVariable(TakoDataFormatVariable):
    pass


class TakoDataFormatTemporalVariable(TakoDataFormatVariable):
    pass


class TakoDataFormatCategoricalVariable(TakoDataFormatVariable):
    pass


ValidTakoDataFormatVariable = (
    TakoDataFormatTemporalVariable
    | TakoDataFormatCategoricalVariable
    | TakoDataFormatVariable
    | TakoDataFormatQuantitativeVariable
)


class TakoDataFormatDataset(BaseModel):
    # A single dataset contains all column variables and all the rows of data
    title: str = Field(
        description="The title of the dataset",
        examples=["Walmart vs Verizon Total Revenue"],
    )
    description: str | None = Field(
        description="The description of the dataset",
        examples=["Comparison of Walmart and Verizon's Total Revenue (fiscal years)"],
    )
    variables: list[ValidTakoDataFormatVariable] = Field(
        description="Details about all variables in the dataset",
        examples=[
            [
                {
                    "name": "Company",
                    "type": TakoDataFormatValueType.STRING,
                    "units": None,
                    "is_sortable": True,
                    "is_higher_better": True,
                },
                {
                    "name": "Revenue",
                    "type": TakoDataFormatValueType.NUMBER,
                    "units": "$M",
                    "is_sortable": True,
                    "is_higher_better": True,
                },
            ]
        ],
    )
    rows: list[TakoDataFormatRowValues] = Field(
        description="Each row contains a single coherent set of values with each "
        "cell having different aspects (variable + value)",
        examples=[
            [
                {
                    "values": [
                        {"variable_name": "Company", "value": "Apple"},
                        {"variable_name": "Revenue", "value": 1000000},
                    ]
                },
            ]
        ],
    )

    def set_inferred_variable_types(self):
        for i, variable in enumerate(self.variables):
            if variable.type == TakoDataFormatValueType.DATE:
                variable = TakoDataFormatTemporalVariable(**variable.model_dump())
                self.variables[i] = variable
            elif variable.type.is_numeric():
                variable = TakoDataFormatQuantitativeVariable(**variable.model_dump())
                self.variables[i] = variable
            elif variable.type == TakoDataFormatValueType.STRING:
                # Check if all string values for this variable are dates
                is_date = True
                for row in self.rows:
                    for cell in row.cell_values:
                        if cell.variable_name == variable.name:
                            if not isinstance(cell.value, str) or not is_date_string(
                                cell.value
                            ):
                                is_date = False
                                break
                    if not is_date:
                        break

                if is_date:
                    variable = TakoDataFormatTemporalVariable(**variable.model_dump())
                else:
                    variable = TakoDataFormatCategoricalVariable(
                        **variable.model_dump()
                    )
                self.variables[i] = variable
            else:
                variable = TakoDataFormatVariable(**variable.model_dump())
                self.variables[i] = variable


class LlmTakoDataFormatDataset(BaseModel):
    """
    This is the dataset that is returned by the LLM. There are more JSON
    schema restrictions that OpenAI imposes on the returned format hence we
    can't directly use the TakoDataFormatDataset schema. Instead we have this
    LlmTakoDataFormatDataset schema that closely matches the TakoDataFormatDataset
    schema but with more JSON schema restrictions. There is a conversion function
    that converts the LlmTakoDataFormatDataset to a TakoDataFormatDataset.
    """

    title: str = Field(
        description="The title of the dataset",
        examples=["Walmart vs Verizon Total Revenue"],
    )
    description: str | None = Field(
        description="The description of the dataset",
        examples=["Comparison of Walmart and Verizon's Total Revenue (fiscal years)"],
    )
    temporal_variables: list[TakoDataFormatTemporalVariable] = Field(
        description="Details about all temporal variables in the dataset",
        examples=[
            [
                {
                    "name": "Revenue",
                    "type": TakoDataFormatValueType.NUMBER,
                    "units": "$M",
                    "is_sortable": True,
                    "is_higher_better": True,
                },
            ]
        ],
    )
    categorical_variables: list[TakoDataFormatCategoricalVariable] = Field(
        description="Details about all categorical variables in the dataset",
        examples=[
            [
                {
                    "name": "Company",
                    "type": TakoDataFormatValueType.STRING,
                    "units": None,
                    "is_sortable": True,
                    "is_higher_better": True,
                },
            ]
        ],
    )

    quantitative_variables: list[TakoDataFormatQuantitativeVariable] = Field(
        description="Details about all quantitative variables in the dataset",
        default=[],
    )

    other_variables: list[TakoDataFormatVariable] = Field(
        description="Details about all other variables in the dataset",
        default=[],
    )

    rows: list[TakoDataFormatRowValues] = Field(
        description="Each row contains a single coherent set of values with each "
        "cell having different aspects (variable + value)",
        examples=[
            [
                {
                    "values": [
                        {"variable_name": "Company", "value": "Apple"},
                        {"variable_name": "Revenue", "value": 1000000},
                    ]
                },
            ]
        ],
    )


def convert_llm_tdf_dataset_to_tdf_dataset(
    llm_tdf_dataset: LlmTakoDataFormatDataset,
) -> TakoDataFormatDataset:
    variables = []
    for variable in llm_tdf_dataset.temporal_variables:
        variables.append(variable)
    for variable in llm_tdf_dataset.categorical_variables:
        if variable.name not in [v.name for v in variables]:
            variables.append(variable)
    for variable in llm_tdf_dataset.quantitative_variables:
        if variable.name not in [v.name for v in variables]:
            variables.append(variable)
    for variable in llm_tdf_dataset.other_variables:
        if variable.name not in [v.name for v in variables]:
            variables.append(variable)
    return TakoDataFormatDataset(
        title=llm_tdf_dataset.title,
        description=llm_tdf_dataset.description,
        variables=variables,
        rows=llm_tdf_dataset.rows,
    )


class SimpleDataPoint(BaseModel):
    variable_name: str = Field(
        description="The name of the variable",
        examples=["Company", "Revenue"],
    )
    value: str | int | float | bool | None = Field(
        description="The value of the variable",
        examples=["Apple", 1000000],
    )


class SimpleDataset(BaseModel):
    title: str = Field(
        description="The title of the dataset",
        examples=["Walmart vs Verizon Total Revenue"],
    )
    description: str | None = Field(
        description="The description of the dataset",
        examples=["Comparison of Walmart and Verizon's Total Revenue (fiscal years)"],
    )
    data_points: list[list[SimpleDataPoint]] = Field(
        description="The data points to visualize",
        examples=[
            [
                {"variable_name": "Year", "value": "2018"},
                {"variable_name": "Walmart Revenue ($M)", "value": 500343},
                {"variable_name": "Verizon Revenue ($M)", "value": 130863},
            ],
            [
                {"variable_name": "Year", "value": "2019"},
                {"variable_name": "Walmart Revenue ($M)", "value": 514405},
                {"variable_name": "Verizon Revenue ($M)", "value": 131868},
            ],
        ],
    )


tdf_description = """
A Tako Data Format (TDF) dataset is a dataset that is formatted in a way that is easy to visualize.

This is based on the tidy data format. See:
* https://cran.r-project.org/web/packages/tidyr/vignettes/tidy-data.html
* https://dimewiki.worldbank.org/Tidying_Data
* https://aeturrell.github.io/python4DS/data-tidy.html#introduction

There are three interrelated features that make a dataset tidy:

1. Each variable is a column; each column is a variable.
2. Each observation is row; each row is an observation.
3. Each value is a cell; each cell is a single value.

There are two common problems you find in data that are ingested that make them not tidy:

1. A variable might be spread across multiple columns - if this is the case, you should
   "melt" the wide data, with multiple columns, into long data.
2. An observation might be scattered across multiple rows - if this is the case, you should
   "unstack" or "pivot" the multiple rows into columns (ie go from long to wide.)
"""


class VisualizeRequest(BaseModel):
    simple_dataset: SimpleDataset | None = Field(
        description="The simple dataset to visualize", default=None
    )
    tako_formatted_dataset: TakoDataFormatDataset | None = Field(
        description=tdf_description, default=None
    )
    file_id: str | None = Field(
        description="The file id of the dataset to visualize", default=None
    )
    query: str | None = Field(
        description="Query with instructions to visualize the dataset", default=None
    )
