# Horizon Attributes Reference

This page documents the PLEXOS Horizon class attributes and their default
values, validation rules, and descriptions.

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## Horizon Attributes

| Name                       | Units  | Default Value | Validation Rule     | Description                                                             |
| -------------------------- | ------ | ------------- | ------------------- | ----------------------------------------------------------------------- |
| Chrono At a Time           | -      | 1             | >= 1                | Number of steps in the chronological model                              |
| Chrono Date From           | -      | 43831         | >= 0                | Start date for the chronological model                                  |
| Chrono Period From         | -      | 1             | >= 1                | Start interval for the chronological model                              |
| Chrono Period To           | -      | 24            | >= 1                | End interval for the chronological model                                |
| Chrono Step Count          | -      | 1             | >= 1                | Number of step types in each step of the chronological model            |
| Chrono Step Type           | -      | 2             | In (-1,0,1,2,3)     | Chronological model step type                                           |
| Chronology                 | -      | 0             | In (0,1)            | Type of chronology used                                                 |
| Compression Factor         | -      | 1             | >= 1                | Number of intervals to output per interval simulated                    |
| Date From                  | -      | 43831         | >= 0                | Start date of the planning horizon                                      |
| Day Beginning              | -      | 0             | Between 0 And 23    | Start hour of the trading day                                           |
| Look-ahead At a Time       | -      | 1             | >= 1                | Number of step types in each step of the chronological model look-ahead |
| Look-ahead Count           | -      | 0             | >= 0                | Number of additional look-ahead steps in the planning horizon           |
| Look-ahead Indicator       | Yes/No | 0             | In (0,-1)           | Flag if chronological model used a look-ahead                           |
| Look-ahead Periods per Day | -      | 24            | Between 1 And 86400 | Number of intervals in each trading day of the look-ahead               |
| Look-ahead Type            | -      | 1             | In (0,1,2,6)        | Step type for look-ahead in chronological model                         |
| Periods per Day            | -      | 24            | Between 1 And 86400 | Number of intervals in each trading day                                 |
| Step Count                 | -      | 1             | >= 1                | Number of steps in the planning horizon                                 |
| Step Type                  | -      | 1             | In (1,2,3,4)        | Planning horizon step type                                              |
| Week Beginning             | -      | 0             | Between -1 And 7    | Start day for weekly constraints                                        |
| Year Ending                | -      | 0             | Between 0 And 12    | Last month of the fiscal year                                           |
