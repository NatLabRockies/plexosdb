# MT Schedule Attributes Reference

This page documents the PLEXOS MT Schedule attributes and their default values,
validation rules, and descriptions.

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## MT Schedule Attributes

| Name                                  | Units  | Default Value | Validation Rule      | Description                                                                                                     |
| ------------------------------------- | ------ | ------------- | -------------------- | --------------------------------------------------------------------------------------------------------------- |
| At a Time                             | -      | 0             | >= 0                 | Number of day/week/months/years in each MT Schedule simulation step.                                           |
| Block Count                           | -      | 3             | >= 1                 | Number of load duration curve blocks in each day/week/month.                                                   |
| Chronology                            | -      | 2             | In (2,3,4,5)         | Type of chronology used.                                                                                        |
| Discount Period Type                  | -      | 2             | In (1,2,3,4,6,7)     | A unique discount factor will be computed for each of these periods.                                           |
| Discount Rate                         | %      | 0             | >= 0                 | Discount rate.                                                                                                  |
| End Effects Method                    | -      | 1             | In (0,1)             | Method used to account for end of horizon discounting.                                                          |
| Last Block Count                      | -      | 0             | >= 0                 | Number of load duration curve blocks in the last load duration curve of the horizon, or zero if same as Block Count. |
| LDC Pin Bottom                        | -      | -1            | >= -1                | Number of points at the bottom of the LDC that are pinned and cannot be aggregated into blocks.              |
| LDC Pin Top                           | -      | -1            | >= -1                | Number of points at the top of the LDC that are pinned and cannot be aggregated into blocks.                 |
| LDC Slicing Method                    | -      | 0             | In (0,1)             | Method used to slice the LDC into blocks.                                                                       |
| LDC Type                              | -      | 1             | In (1,2,3,4,7)       | Create one LDC for each period of this type in the horizon.                                                     |
| LDC Weight a                          | -      | 0             |                      | LDC weighting polynomial function 'a' parameter.                                                                |
| LDC Weight b                          | -      | 1             |                      | LDC weighting polynomial function 'b' parameter.                                                                |
| LDC Weight c                          | -      | 0             |                      | LDC weighting polynomial function 'c' parameter.                                                                |
| LDC Weight d                          | -      | 0             |                      | LDC weighting polynomial function 'd' parameter.                                                                |
| New Entry Capacity Mechanism          | -      | 0             | In (0,1,2)           | Capacity payment mechanism.                                                                                     |
| New Entry Driver                      | -      | 0             | In (0,1,2,3)         | New entry driver.                                                                                                |
| New Entry Time Lag                    | month  | 12            | >= 0                 | Lag time for entrepreneurial entry.                                                                             |
| Outage Increment                      | MW     | 10            | >= 1                 | Generator outage bin size in convolution.                                                                       |
| Pricing Method                        | -      | 0             | In (0,1)             | Type of generator pricing used in MT Schedule.                                                                  |
| Reduced Sample Count                  | -      | 4             | >= 1                 | Statistically reduce the Sample Type periods to at most this number of samples each year.                      |
| Reduction Relative Accuracy           | -      | 1             | Between 0 And 1      | Stop sample reduction when the accuracy of the reduced sample set reaches this level.                          |
| Reliability Min Contiguous Block      | h      | 0             | >= 0                 | For reliability based sampled chronology ensure sampled periods are contained in contiguous blocks of at least this many hours. |
| Sample Type                           | -      | 2             | In (1,2,3,4)         | For Chronology = Sampled, take this type of sample.                                                             |
| Sampled Block Count                   | -      | 0             | >= 0                 | Number of blocks modeled in each sample period (day/week) where zero means the original number of intervals.   |
| Sampled Shallow Storage Cutoff        | h      | 0             | >= 0                 | For Chronology = Sampled and Sampled Shallow Storage Treatment = Custom, maximum storage duration in hours for shallow storage formulation. |
| Sampled Shallow Storage Treatment     | -      | 1             | In (1,2,3)           | Sampled shallow storage treatment.                                                                              |
| Sampling Interval                     | -      | 4             | In (-1,2,3,4,7)      | For Chronology = Sampled, take Sample Type samples in each of these intervals of time.                         |
| Start Cost Amortization Period        | h      | 0             | >= 0                 | Number of hours over which generator start costs are amortized.                                                 |
| Step Link Mode                        | -      | 0             | In (0,1,2)           | Controls how the solutions of each step are linked together.                                                    |
| Step Type                             | -      | 4             | In (1,2,3,4,7)       | Each simulation step will span steps of this type.                                                              |
| Stochastic Algorithm                  | -      | 0             | In (0,1)             | Algorithm invoked by the Stochastic Method when a scenario tree is present.                                     |
| Stochastic Method                     | -      | 0             | In (0,1,2,3)         | Stochastic optimization method for MT Schedule.                                                                  |
| Storage Formulate Head Effects        | Yes/No | -1            | In (0,-1)            | If storage head effects should be formulated in MT Schedule.                                                    |
| Use Effective Load Approach           | Yes/No | 0             | In (0,-1)            | If MT Schedule uses the effective load approach.                                                                |
| Write Bridge Text Files               | Yes/No | 0             | In (0,-1)            | If bridge information such as constraint decomposition and storage targets should be written to text files.     |
