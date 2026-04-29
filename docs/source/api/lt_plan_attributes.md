# LT Plan Attributes Reference

This page documents the PLEXOS LT Plan attributes and their default values,
validation rules, and descriptions.

To look at the open access PLEXOS documentation, go to
[PLEXOS LT Plan Index](https://portal.energyexemplar.com/unified-help/plexos-desktop/index.htm#t=Index.LTPlan.html&rhsearch=lt%20plan).

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## LT Plan Attributes

| Name                                           | Units  | Default Value | Validation Rule   | Description                                                                                                                                 |
| ---------------------------------------------- | ------ | ------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Allow Capacity Sharing                         | Yes/No | 0             | In (0,-1)         | If regions/zones can share capacity reserves to meet requirements.                                                                          |
| Always Annualize Build Cost                    | -      | 0             | In (0,-1)         | If Build Cost is always annualized even when an option retires inside the horizon.                                                          |
| At a Time                                      | -      | 0             | >= 0              | Number of years solved in each step of LT Plan.                                                                                             |
| Block Count                                    | -      | 12            | >= 1              | Number of load duration curve blocks in each day/week/month.                                                                                |
| Bridge Constraints                             | Yes/No | -1            | In (0,-1)         | If LT Plan should bridge (decompose) constraints for subsequent simulation phases.                                                          |
| Bridge Storage                                 | Yes/No | -1            | In (0,-1)         | If LT Plan should bridge (decompose) storage for subsequent simulation phases.                                                              |
| Capacity Payments Enabled                      | Yes/No | 0             | In (0,-1)         | If payments are made for generation capacity.                                                                                               |
| Chronology                                     | -      | 2             | In (2,3,4)        | Type of chronology used.                                                                                                                    |
| Co-optimize Unit Commitment                    | Yes/No | 0             | In (0,-1)         | If unit commitment is co-optimized rather than sequentially optimized with expansion.                                                       |
| Compute Multi-area Reliability Indices         | Yes/No | 0             | In (0,-1)         | Master switch for computation of reliability indices LOLP, LOLE, etc across multiple areas.                                                 |
| Compute Reliability Indices                    | Yes/No | 0             | In (0,-1)         | Master switch for computation of reliability indices LOLP, LOLE, etc.                                                                       |
| Decomposition                                  | -      | 1             | >= 1              | Reduce the number of simulated periods by this factor in the first pass of a two-pass decomposition.                                        |
| Depreciation Method                            | -      | 0             | In (0,1,2)        | Depreciation method for computing annuities.                                                                                                |
| Discount Period Type                           | -      | 4             | In (1,2,3,4,6,7)  | A unique discount factor and expansion decisions will be computed for each of these periods.                                                |
| Discount Rate                                  | %      | 0             | >= 0              | Discount rate.                                                                                                                              |
| End Effects Method                             | -      | 1             | In (0,1)          | Method used to account for end of horizon effects.                                                                                          |
| Inflation Rate                                 | %      | 0             |                   | Inflation rate used in depreciation calculations.                                                                                           |
| Integerization Horizon                         | yr     | -1            | >= -1             | Number of years over which the expansion decisions are integerized.                                                                         |
| Last Block Count                               | -      | 0             | >= 0              | Number of load duration curve blocks in the last load duration curve of the horizon, or zero if same as Block Count.                        |
| LDC Pin Bottom                                 | -      | -1            | >= -1             | Number of points at the bottom of the LDC that are pinned and cannot be aggregated into blocks.                                             |
| LDC Pin Top                                    | -      | -1            | >= -1             | Number of points at the top of the LDC that are pinned and cannot be aggregated into blocks.                                                |
| LDC Slicing Method                             | -      | 0             | In (0,1)          | Method used to slice the LDC into blocks.                                                                                                   |
| LDC Type                                       | -      | 3             | In (1,2,3,4,7)    | One LDC is created for each period of this type in horizon.                                                                                 |
| LDC Weight a                                   | -      | 0             |                   | LDC weighting polynomial function 'a' parameter.                                                                                            |
| LDC Weight b                                   | -      | 1             |                   | LDC weighting polynomial function 'b' parameter.                                                                                            |
| LDC Weight c                                   | -      | 0             |                   | LDC weighting polynomial function 'c' parameter.                                                                                            |
| LDC Weight d                                   | -      | 0             |                   | LDC weighting polynomial function 'd' parameter.                                                                                            |
| Limit Capital Cost Perpetuity by Economic Life | -      | -1            | In (0,-1)         | With perpetuity end effect, if annuity calculation should extend beyond the end of the horizon up to the Economic Life.                     |
| Maintenance Rate Output Basis                  | -      | 0             | In (0,1)          | Basis for Maintenance Rate (%) Output due to Maintenance Sculpting.                                                                         |
| Maintenance Sculpting                          | Yes/No | 0             | In (0,-1)         | If LT Plan should sculpt maintenance derating according to the inverse of load.                                                             |
| Optimality                                     | -      | 2             | In (0,1,2)        | LT Plan integerization scheme.                                                                                                              |
| Optimize Expansion                             | Yes/No | -1            | In (0,-1)         | If expansion is optimized by this simulation phase.                                                                                         |
| Outage Increment                               | MW     | 10            | >= 1              | Generator outage bin size in convolution.                                                                                                   |
| Overlap                                        | -      | 0             | >= -1             | Number of years overlap between steps where -1 invokes Rolling Horizon.                                                                     |
| Pricing Method                                 | -      | 0             | In (0,1)          | Type of generator pricing used in LT Plan.                                                                                                  |
| Reduced Sample Count                           | -      | 4             | >= 1              | Statistically reduce the Sample Type periods to at most this number of samples each year.                                                   |
| Reduction Relative Accuracy                    | -      | 1             | Between 0 And 1   | Stop sample reduction when the accuracy of the reduced sample set reaches this level.                                                       |
| Sample Type                                    | -      | 2             | In (1,2,3,4)      | For Chronology = Sampled, take this type of sample.                                                                                         |
| Sample Year Count                              | -      | 0             | >= 0              | For Chronology = Sampled, first select this many years then sample within only those years.                                                 |
| Sampled Block Count                            | -      | 0             | >= 0              | Number of blocks modeled in each sample period (day/week) where zero means the original number of intervals.                                |
| Sampled Shallow Storage Cutoff                 | h      | 0             | >= 0              | For Chronology = Sampled and Sampled Shallow Storage Treatment = Custom, maximum storage duration in hours for shallow storage formulation. |
| Sampled Shallow Storage Treatment              | -      | 1             | In (1,2,3)        | For Chronology = Sampled, method used for formulating low duration storages and batteries.                                                  |
| Sampling Interval                              | -      | 4             | In (-1,2,3,4,7)   | For Chronology = Sampled, take Sample Type samples in each of these intervals of time.                                                      |
| Solution Count                                 | -      | 1             | >= 1              | Maximum number of solutions produced in the solution hierarchy.                                                                             |
| Solution Quality                               | %      | 0             | Between 0 And 100 | Continue producing solutions up to Solution Count or when Solution Quality falls to this level.                                             |
| Start Cost Amortization Period                 | h      | 0             | >= 0              | Number of hours over which generator start costs are amortized.                                                                             |
| Stochastic Method                              | -      | 0             | In (0,1,2,3)      | Stochastic optimization method for LT Plan.                                                                                                 |
| Storage Formulate Head Effects                 | Yes/No | -1            | In (0,-1)         | If storage head effects should be formulated in LT Plan.                                                                                    |
| Storage Restart                                | Yes/No | 0             | In (0,-1)         | If recycled storage should restart from their initial volume at the start of each capacity optimization period.                             |
| Tax Rate                                       | %      | 0             |                   | Tax rate used to compute tax credits.                                                                                                       |
| Use Effective Load Approach                    | Yes/No | 0             | In (0,-1)         | If LT Plan uses the effective load approach.                                                                                                |
| Write Expansion Plan Text Files                | Yes/No | 0             | In (0,-1)         | If expansion plans should be written to text files.                                                                                         |
