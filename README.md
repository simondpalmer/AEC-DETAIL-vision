# AEC-VA-DETAIL-vision
AEC vision model for technical documents. Dataset created from Veteran Affairs website of construction details and specs

This uses poetry. Once poetry is installed 
run the following in the root directory:

```bash
$ poetry install
```

Then you can run the scraper and create the relevant dataframe: 
run the following:

```bash
$ poetry run main.py
```

### DataFrames

#### Specification DataFrame

| number  | title                    | body                                        | link                                          |
| ------- | ------------------------ | ------------------------------------------- | --------------------------------------------- |
| 00 01 15| List of Drawing Sheets   | SECTION 00 01 15\nLIST OF DRAWING SHEETS\nThe.. | https://www.cfm.va.gov/TIL/spec/000110.docx   |

#### Detail DataFrame

| number     | title                         | images      | link                                                               |
| ---------- | ----------------------------- | ----------- | ------------------------------------------------------------------ |
| SD000115-01| Architectural Abbreviations   | [PIL.Image] | https://www.cfm.va.gov/til/sDetail/Div00SpclSect/SD000115-26.pdf   |


#### Merged DataFrames

| detail_number  | detail_title                | detail_description | detail_link                                                        | spec_number | spec_title              | spec_body                                       |  spec_link                                  |
| -------------- | --------------------------- | ------------------ | ------------------------------------------------------------------ | ----------- | ----------------------- | ----------------------------------------------- | ------------------------------------------- |
| SD000115-01    | Architectural Abbreviations | description        | https://github.com/simondpalmer/AEC-DETAIL-vision/raw/main/data/SD000115-01_1.png   | 00 01 15    |  List of Drawing Sheets | SECTION 00 01 15\nLIST OF DRAWING SHEETS\nThe.. |  https://www.cfm.va.gov/TIL/spec/000110.docx|

Then a dataset can be created by iterating over this data and creating an image file of the detail and adding a description using [LLaVa](https://llava-vl.github.io/). As a simple example, below we are linking the image of the construction image / sheet (Arch. Abreviations in this case) to the relevant specification:

```json
[
  {
    "file_name": "SD000115-01_1.png",
    "detail_number": "SD000115-01",
    "detail_title": "Architectural Abbreviations",
    "detail_description": [
      {
        "from": "user",
        "value": "Can you explain what this Architectural Abbreviations drawing indicates? Provide as much detail as possible"
      },
      {
        "from": "assistant",
        "value": "This drawing helps to streamline communication and maintain consistency in architectural documentation. By using these abbreviations, architects and designers can efficiently convey their ideas and intentions to clients, contractors, and other stakeholders involved in a construction project."
      }
    ],
    "detail_link": "https://github.com/simondpalmer/AEC-DETAIL-vision/raw/main/data/SD000115-01_1.png",
    "spec_number": "00 01 15",
    "spec_title": "List of Drawing Sheets",
    "spec_body": "SECTION 00 01 15\nLIST OF DRAWING SHEETS\nThe drawings listed below accompanying this specification form a part of the contract. \nDrawing No.\tTitle\nSPEC WRITER NOTE: List drawing numbers and titles under the classifications and in the relative order listed below. See Sample Section 00 01 15, LIST OF DRAWINGS on back of this sheet.\n\tSITE PLANNING \n\tSUB-SURFACE \n\tARCHITECTURAL \n\tSTRUCTURAL \n\tSANITARY \n\tEQUIPMENT \n\tPLUMBING \n\tHEATING, VENTILATING, AIR \n\tCONDITIONING AND REFRIGERATION \n\tSTEAM GENERATION \n\tOUTSIDE STEAM DISTRIBUTION \n\tELECTRICAL \n- - - END - - -\n(SAMPLE LIST OF DRAWINGS) \nVAMC (NAME)\t\t\t\t\t\t\t\t\t(SPEC No.) \nSECTION 00 01 15 \nLIST OF DRAWINGS \nThe drawings listed below accompanying this specification form a part of the contract. \nDrawing No.\t\t\t\tTitle \n\tSITE PLANNING \nL1\tSite Plan \nL2\tPlanting Plan \nL3\tSite and Planting Details \n\tARCHITECTURAL \n30-1\tGround Floor Plan \n30-2\tElevations \n30-3\tWall Sections and Details \n30-4\tIndustrial Stair, Dock Leveler, Areaway \n\tSections and Details \n30-5\tReflected Ceiling Plan \n30-6\tSchedules \n- - - E N D - - -",
    "spec_link": "https://www.cfm.va.gov/TIL/spec/000115.docx"
  },
  {....}]
```


The current dataset can be found here: https://huggingface.co/datasets/simondavidpalmer/AEC-VA-details-spec-dataset

Enjoy!
