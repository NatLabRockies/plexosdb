# Production Attributes Reference

This page documents the PLEXOS Production class attributes and their default
values, validation rules, and descriptions.

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## Production Attributes

| Name                                   | Units  | Default Value | Validation Rule   | Description                                                                                                            |
| -------------------------------------- | ------ | ------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Battery Station Aggregation Mode       | -      | 0             | In (0,1,2)        | Automatically create Battery Station objects by aggregating Batteries                                                  |
| Capacity Factor Constraint Basis       | -      | 0             | In (0,1)          | Basis for capacity factor constraints.                                                                                 |
| Cooling States Enabled                 | Yes/No | -1            | In (0,-1)         | If generator unit cooling states are enabled                                                                           |
| Dispatch by Battery Station            | Yes/No | -1            | In (0,-1)         | If batteries should be aggregated through manual or automatic battery stations for dispatch.                           |
| Dispatch by Power Station              | Yes/No | -1            | In (0,-1)         | If generators in power stations should be treated in aggregate for dispatch.                                           |
| DP Capacity Factor Error Threshold     | %      | 20            | >= 0              | Error in DP capacity factor compared to MT Schedule capacity factor below which the DP solution is accepted            |
| DP Capacity Factor Threshold           | %      | 20            | >= 0              | Minimum capacity factor for generators to be dispatched by the DP                                                      |
| Forced Outage Relaxes Min Down Time    | Yes/No | 0             | In (0,-1)         | If ramp constraints should all be formulated upfront rather than checked iteratively.                                  |
| Formulate Ramp Upfront                 | Yes/No | -1            | In (0,-1)         | If ramp constraints should all be formulated upfront rather than checked iteratively.                                  |
| Formulate Upfront                      | Yes/No | -1            | In (0,-1)         | If production constraints should all be formulated upfront rather than checked iteratively.                            |
| Fuel Use Function Precision            | -      | 0             | >= 0              | Precision for calculation of linear approximation to fuel function.                                                    |
| Gas Demand Resolution                  | -      | 0             | In (0,1,2)        | Resolution of input gas demands                                                                                        |
| Heat Rate Detail                       | -      | 0             | In (0,1,2)        | Level of detail for Generator heat rate modelling                                                                      |
| Heat Rate Error Method                 | -      | 2             | In (0,1,2,3,4)    | Method for handling non-convex heat rate functions.                                                                    |
| Increment and Decrement                | Yes/No | -1            | In (0,-1)         | If simultaneous closure of increment and decrement bids/offers around a base is allowed                                |
| Integers in Look-ahead                 | -      | 1             | In (0,1,2)        | Controls when the look-ahead contains integers for unit commitment and other decisions.                                |
| Max Heat Rate Tranches                 | -      | 10            | Between 1 And 100 | Maximum number of tranches in the fuel function piecewise linear approximation                                         |
| Min Heat Rate Tranche Size             | -      | 0             | >= 0              | Minimum tranche size in fuel function piecewise linear approximation                                                   |
| Power Station Aggregation Mode         | -      | 0             | In (0,1,2)        | Automatically create Power Station objects by aggregating Generators                                                   |
| Pump and Generate                      | Yes/No | -1            | In (0,-1)         | If pumped storage/battery is allowed to pump/charge and generate/discharge simultaneously                              |
| Ramping Constraints Enabled            | Yes/No | -1            | In (0,-1)         | If facility ramping constraints are modeled                                                                            |
| Rounded Relaxation Commitment Model    | -      | 0             | In (0,1)          | Determines if the unit commitment decisions are made centrally or by self-commitment                                   |
| Rounded Relaxation End Threshold       | -      | 0.75          | <= 1              | End value for [Rounding Up Threshold] when Rounded Relaxation is running self-tune.                                    |
| Rounded Relaxation Start Threshold     | -      | 0.25          | >= 0              | Start value for [Rounding Up Threshold] when Rounded Relaxation is running self-tune.                                  |
| Rounded Relaxation Threshold Increment | -      | 0.05          | >= 0.01           | Increment value for [Rounding Up Threshold] when Rounded Relaxation is running self-tune.                              |
| Rounded Relaxation Tuning              | Yes/No | 0             | In (0,-1)         | If the Rounded Relaxation method should self-tune the [Rounding Up Threshold].                                         |
| Rounding Up Threshold                  | -      | 0.5           | Between 0 And 1   | Threshold at which non-integers are rounded up.                                                                        |
| Run Up and Down Enabled                | Yes/No | -1            | In (0,-1)         | If generator run up and run down are modeled                                                                           |
| Start and Stop Enabled                 | Yes/No | -1            | In (0,-1)         | If facility start up and shut down are modeled                                                                         |
| Start Cost Method                      | -      | 0             | In (0,1)          | Method for handling start costs in the mathematical formulation (integrate into the formulation, or calculate ex-post) |
| Transitions Enabled                    | Yes/No | -1            | In (0,-1)         | If generator transitions are modeled                                                                                   |
| Unit Commitment Heat Rate Detail       | Yes/No | -1            | In (0,-1)         | If modeling fully detailed heat rates for unit commitment. Otherwise perform a two-pass UC/ED.                         |
| Unit Commitment Optimality             | -      | 0             | In (0,1,2,3)      | Unit commitment integerization scheme.                                                                                 |
| Warm Up Process Enabled                | Yes/No | -1            | In (0,-1)         | If modeling of Facility Warm Up Process is enabled                                                                     |
