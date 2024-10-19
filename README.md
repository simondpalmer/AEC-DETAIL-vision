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

### Dataset

Combined spec and detail data for conversational training dataset:

| spec_number  | spec_title               | spec_link                                   | detail_number | detail_title                 | detail_link |
| ------------ | ------------------------ | ------------------------------------------- | ------------- | ---------------------------- | ----------- |
| 00 01 15     | List of Drawing Sheets   | https://www.cfm.va.gov/TIL/spec/000110.docx | SD000115-01   |  Architectural Abbreviations | https://www.cfm.va.gov/til/sDetail/Div00SpclSect/SD000115-01.pdf |
| 00 01 15     | List of Drawing Sheets   | https://www.cfm.va.gov/TIL/spec/000110.docx | SD000115-02   |  Architectural Abbr. Cont. | https://www.cfm.va.gov/til/sDetail/Div00SpclSect/SD000115-02.pdf |

If you want to publish to Hugging Face you will need to add your token and uncomment the last bit of code.
Enjoy!