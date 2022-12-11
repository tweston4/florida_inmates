
- [Introduction](#introduction)
    - [Quickstart](#quickstart)
  - [Dataset](#dataset)
    - [ROOT](#root)
    - [Offenses](#offenses)
    - [Scar Marks](#scar-marks)

# Introduction
Do tattoos on inmates correlate to there prison terms or charges? This project utilizes a dataset of Florida inmates and their tattoos from 1980 - 2017, to analyze the correlation between tattoos and crime. Analytics and results will be displayed on a streamlit app. 

---

### Quickstart

* Check out the [Streamlit App ](https://florida-inmate-tattoos.streamlit.app/)!

* To run locally follow the steps below:
    1. 

---

## Dataset

The dataset was shared to me from a colleague in a Data Analytics course and can be found [HERE](https://www.dropbox.com/sh/5mhudhvlx49sysw/AAAD0CBKKWs2WwbxyoHhKaM0a?dl=0).

---

### ROOT

| Race | Sex | BirthDate  | HairColor | EyeColor | Height | Weight | PrisonReleaseDate | ReceiptDate | releasedateflag\_descr | custody\_description | FACILITY\_description |
| ---- | --- | ---------- | --------- | -------- | ------ | ------ | ----------------- | ----------- | ---------------------- | -------------------- | --------------------- |
| W    | M   | 1/1/1940   | BLK       | BRO      | 601    | 160    |                   | 10/8/1976   | life sentence          | CLOSE                | ZEPHYRHILLS C.I.      |
| B    | M   | 6/28/1944  | BLK       | BRO      | 510    | 140    |                   | 10/12/1971  | life sentence          | CLOSE                | UNION C.I.            |
| B    | M   | 12/30/1937 | BLK       | BRO      | 510    | 155    |                   | 1/19/1960   | life sentence          | MEDIUM               | LAKE C.I.             |
| B    | M   | 6/8/1939   | BLK       | BRO      | 600    | 230    | 2/8/2019          | 12/15/2015  | valid release date     | CLOSE                | NWFRC ANNEX.          |
| B    | M   | 6/20/1941  | BLK       | BRO      | 508    | 140    |                   | 7/28/1976   | life sentence          | CLOSE                | S.F.R.C SOUTH UNIT    |

---

### Offenses

| DCNumber | Sequence | OffenseDate | DateAdjudicated | County    | CaseNumber | prisonterm | ProbationTerm | ParoleTerm | adjudicationcharge\_descr | qualifier\_descr | adjudication\_descr       |
| -------- | -------- | ----------- | --------------- | --------- | ---------- | ---------- | ------------- | ---------- | ------------------------- | ---------------- | ------------------------- |
| R32366   | 2        | 11/19/2017  | 12/18/2017      | PINELLAS  | 1714110    | 0010600    | 0000000       | 0000000    | COCAINE - POSSESSION      | PRINCIPAL        | ADJUDICATION NOT WITHHELD |
| Y45152   | 5        | 10/27/2017  | 11/28/2017      | GLADES    | 1700148    | 0030000    | 0000000       | 0000000    | COCAINE - POSSESSION      | PRINCIPAL        | ADJUDICATION NOT WITHHELD |
| V21385   | 4        | 10/25/2017  | 11/7/2017       | ST. JOHNS | 1701588    | 0010003    | 0000000       | 0000000    | COCAINE - POSSESSION      | PRINCIPAL        | ADJUDICATION NOT WITHHELD |
| G09824   | 7        | 10/12/2017  | 12/6/2017       | ALACHUA   | 1703733    | 0010600    | 0000000       | 0000000    | COCAINE - POSSESSION      | PRINCIPAL        | ADJUDICATION NOT WITHHELD |
| V14207   | 28       | 10/12/2017  | 11/30/2017      | VOLUSIA   | 1713094    | 0010001    | 0000000       | 0000000    | COCAINE - POSSESSION      | PRINCIPAL        | ADJUDICATION NOT WITHHELD |

---

### Scar Marks

| DCNumber | Type   | Location  | Description                      |
| -------- | ------ | --------- | -------------------------------- |
| 000735   | TATTOO | LEFT ARM  | BLACK PANTHER/ORIENTAL/YING YANG |
| 000735   | TATTOO | BACK      | EAGLE/UNICORN/ROSE/NAKED WOMAN   |
| 000735   | TATTOO | LEFT ARM  | TEXAS W YELLOW ROSE/HEART/DEVIL  |
| 000735   | TATTOO | RIGHT LEG | TIGAR/COBRA                      |
| 000735   | TATTOO | LEFT LEG  | TRIBAL EAGLE                     |


