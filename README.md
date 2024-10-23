# AEC-DETAIL-vision
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

### Datasets

#### Specification dataset

| number  | title                    | body                                        | link                                          |
| ------- | ------------------------ | ------------------------------------------- | --------------------------------------------- |
| 00 01 15| List of Drawing Sheets   | SECTION 00 01 15\nLIST OF DRAWING SHEETS\nThe.. | https://www.cfm.va.gov/TIL/spec/000110.docx   |

#### Detail dataset

| number     | title                         | images      | link                                                               |
| ---------- | ----------------------------- | ----------- | ------------------------------------------------------------------ |
| SD000115-01| Architectural Abbreviations   | [PIL.Image] | https://www.cfm.va.gov/til/sDetail/Div00SpclSect/SD000115-26.pdf   |


#### Merged dataset

| detail_number  | detail_title                | detail_images | detail_link                                                        | spec_number | spec_title              | spec_body                                       |  spec_link                                  |
| -------------- | --------------------------- | ------------- | ------------------------------------------------------------------ | ----------- | ----------------------- | ----------------------------------------------- | ------------------------------------------- |
| SD000115-01    | Architectural Abbreviations | [PIL.Image]   | https://www.cfm.va.gov/til/sDetail/Div00SpclSect/SD000115-26.pdf   | 00 01 15    |  List of Drawing Sheets | SECTION 00 01 15\nLIST OF DRAWING SHEETS\nThe.. |  https://www.cfm.va.gov/TIL/spec/000110.docx|

Then a conversational dataset can be created by iterating over this data and creating image files of the detail pdf and referencing them via URL's. As a simple example, below we are linking the image of the construction image / sheet (Arch. Abreviations in this case) to the relevant specification:

```json
{
    "id": "construction_0",
    "conversations": [
      {
        "from": "user",
        "value": "Drawing: <img src='https:\\github.com\\simondpalmer\\AEC-DETAIL-vision\\blob\\main\\output_images\\drawing_0_0.png'></img>\nCan you explain what this drawing shows?"
      },
      {
        "from": "assistant",
        "value": "The specification List of Drawing Sheets for Architectural Abbreviations can be found in the following document: SECTION 00 01 15\nLIST OF DRAWING SHEETS\nThe drawings listed below accompanying this specification form a part of the contract. \nDrawing No.\tTitle\nSPEC WRITER NOTE: List drawing numbers and titles under the classifications and in the relative order listed below. See Sample Section 00 01 15, LIST OF DRAWINGS on back of this sheet.\n\tSITE PLANNING \n\tSUB-SURFACE \n\tARCHITECTURAL \n\tSTRUCTURAL \n\tSANITARY \n\tEQUIPMENT \n\tPLUMBING \n\tHEATING, VENTILATING, AIR \n\tCONDITIONING AND REFRIGERATION \n\tSTEAM GENERATION \n\tOUTSIDE STEAM DISTRIBUTION \n\tELECTRICAL \n- - - END - - -\n(SAMPLE LIST OF DRAWINGS) \nVAMC (NAME)\t\t\t\t\t\t\t\t\t(SPEC No.) \nSECTION 00 01 15 \nLIST OF DRAWINGS \nThe drawings listed below accompanying this specification form a part of the contract. \nDrawing No.\t\t\t\tTitle \n\tSITE PLANNING \nL1\tSite Plan \nL2\tPlanting Plan \nL3\tSite and Planting Details \n\tARCHITECTURAL \n30-1\tGround Floor Plan \n30-2\tElevations \n30-3\tWall Sections and Details \n30-4\tIndustrial Stair, Dock Leveler, Areaway \n\tSections and Details \n30-5\tReflected Ceiling Plan \n30-6\tSchedules \n- - - E N D - - -"
      }
    ]
  },
```

From here this conversational dataset can be scaled to include all drawings and used to train a LVM

If you want to publish to Hugging Face you will need to add your own token and repo id and uncomment the last bit of code.
The current dataset can be found here: https://huggingface.co/datasets/simondavidpalmer/AEC-VA-details-spec-dataset

Enjoy!
