# Transmission Attributes Reference

This page documents the PLEXOS Transmission class attributes and their default
values, validation rules, and descriptions.

To look at the open access PLEXOS documentation, go to
[PLEXOS Transmission Index](https://portal.energyexemplar.com/unified-help/plexos-desktop/index.htm#t=Index.Transmission.html&rhsearch=transmission).

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## Transmission Attributes

| Name                                  | Units  | Default Value | Validation Rule                | Description                                                                                                              |
| ------------------------------------- | ------ | ------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| Allow Dump Energy                     | Yes/No | -1            | In (0,-1)                      | Model Dump Energy in OPF                                                                                                 |
| Allow Unserved Energy                 | Yes/No | -1            | In (0,-1)                      | Model Unserved Energy in OPF                                                                                             |
| Bound Node Phase Angles               | Yes/No | 0             | In (0,-1)                      | If the Node [Phase Angle] values are subject to bounds in absolute value.                                                |
| Cache Transmission Matrices           | Yes/No | 0             | In (0,-1)                      | Cache the transmission matrices to disk for future use.                                                                  |
| Calculate Node LPF from Load          | -      | 0             | In (0,1)                       | Automatically calculate Node LPF from input Load property                                                                |
| Commitment PTDF Threshold             | -      | 0             | >= 0                           | Minimum absolute value of PTDF coefficient in commitment solves.                                                         |
| Constraint Limit Penalty              | $/MWh  | -1            |                                | Penalty for exceeding line and transformer limits.                                                                       |
| Constraint Voltage Threshold          | kV     | 0             | >= 0                           | Voltage level at which thermal limits are modelled.                                                                      |
| Constraints Enabled                   | Yes/No | -1            | In (0,-1)                      | If transmission line constraints are enabled.                                                                            |
| Contingency Limit Penalty             | $/MWh  | -1            |                                | Penalty for exceeding contingency flow limits.                                                                           |
| Contingency Monitoring Threshold      | %      | 100           | Between 0 And 100              | Monitor only this percentage of most affected Line/Transformer/Interface flows.                                          |
| Convergence Report Level              | -      | 1             | In (0,1,2)                     | Level of screen reporting during transmission convergence iterations (none, normal, verbose)                             |
| Detail                                | -      | 1             | In (0,1,2)                     | Level of detail used in transmission modeling                                                                            |
| Detect Non-physical Losses            | Yes/No | 0             | In (0,-1)                      | If non-physical losses should be detected (in the piecewise linear loss model) and removed via mixed-integer programming |
| Energy Balance Violation Variables    | Yes/No | 0             | In (0,-1)                      | Include violation variables on the transmission system energy balance equations                                          |
| Enforce Limits On Lines In Interfaces | Yes/No | 0             | In (0,-1)                      | If lines and transformers in interfaces should have their limits enforced regardless of voltage                          |
| Enforce N-1 Contingencies             | Yes/No | 0             | In (0,-1)                      | If N-1 contingencies should be automatically enforced.                                                                   |
| Filter Limits                         | Yes/No | 0             | In (0,-1)                      | If transmission limits are filtered using extreme flows from MT Schedule                                                 |
| Flow PTDF Threshold                   | -      | 0.01          | >= 0                           | Minimum absolute value of PTDF as coefficient in transmission flow constraints.                                          |
| Formulate Upfront                     | Yes/No | 0             | In (0,-1)                      | If transmission constraints should all be formulated upfront rather than checked iteratively.                            |
| Interface Constraints Enabled         | Yes/No | -1            | In (0,-1)                      | If interface constraints are enabled.                                                                                    |
| Interface Limit Penalty               | $/MWh  | -1            |                                | Penalty for exceeding interface flow limits.                                                                             |
| Internal VoLL                         | $      | 100000        | Between 0 And 1E+9             | Value of Lost Load used internally                                                                                       |
| Interruption Sharing                  | Yes/No | 0             | In (0,-1)                      | If region interruption sharing is activated.                                                                             |
| Kron-reduced Model Input              | -      | 0             | In (0,1)                       | Input properties and files written out for Kron-reduced model.                                                           |
| Limit Bootstrap Initial Threshold     | -      | 2             | >= 0                           | Initial value of [Limit Threshold] during transmission constraint bootstrap phase.                                       |
| Limit Bootstrap Threshold Decrement   | -      | 0.25          | Between 0 And 1                | [Limit Threshold] decrement used for each iteration of transmission bootstrap phase.                                     |
| Limit Threshold                       | -      | 0.95          | Between 0 And 1                | Line, Transformer, or Interface flow loading threshold above which limits are added.                                     |
| LODF Threshold                        | -      | 0.03          | >= 0                           | Minimum absolute value of LODF to be used in contingency flow constraints.                                               |
| Loss Method                           | -      | 0             | In (0,1,3,4,5)                 | Formulation method used to model transmission losses.                                                                    |
| Loss Tolerance                        | -      | 1E-05         | >= 0                           | Relative gap between real and modelled losses.                                                                           |
| Loss Voltage Threshold                | kV     | 0             | >= 0                           | Voltage level at which losses are modelled.                                                                              |
| Losses Enabled                        | Yes/No | 0             | In (0,-1)                      | If transmission losses are enabled.                                                                                      |
| Max Absolute Phase Angle              | rad    | 6.28          | Between 0 And 6.28318530717958 | Maximum absolute value allowed for any Node [Phase Angle].                                                               |
| Max Embedded Loss Iterations          | -      | 2             | >= 0                           | Maximum number of iterations for removing embedded losses from load.                                                     |
| Max Limit Iterations                  | -      | 1000          | >= 0                           | Maximum number of iterations during any one call to enforce transmission limits.                                         |
| Max Loss Absolute Error               | -      | 0             | >= 0                           | Maximum allowed absolute error in the piecewise linear loss function.                                                    |
| Max Loss Iterations                   | -      | 50            | >= 1                           | Maximum number of iterations for converging the losses.                                                                  |
| Max Loss Relative Error               | -      | 0             | >= 0                           | Maximum allowed relative error in the piecewise linear loss function.                                                    |
| Max Loss Tranches                     | -      | 100           | >= 1                           | Maximum number of tranches in piecewise linear line loss function.                                                       |
| MVA Base                              | -      | 100           | >= 0                           | MVA base for AC line parameters.                                                                                         |
| N-1 Contingency Voltage Threshold     | kV     | 0             | >= 0                           | Voltage level at which N-1 contingencies are automatically enforced.                                                     |
| OPF Method                            | -      | 0             | In (0,1)                       | Method for solving optimal power flow.                                                                                   |
| PTDF Method                           | -      | 0             | In (0,1,2,3,4)                 | Method for computation of shift factors                                                                                  |
| Reactance Cut-off                     | -      | 0             |                                | Smallest allowable reactance when performing OPF.                                                                        |
| Rental Method                         | -      | 0             | In (0,1)                       | Method used to calculate transmission rentals                                                                            |
| Report All Interregional Flows        | Yes/No | -1            | In (0,-1)                      | If line flows between regions should be reported regardless of kV.                                                       |
| Report All Interzonal Flows           | Yes/No | -1            | In (0,-1)                      | If line flows between zones should be reported regardless of kV.                                                         |
| Report Enabled                        | Yes/No | -1            | In (0,-1)                      | If transmission reporting is enabled.                                                                                    |
| Report Injection and Load Nodes       | Yes/No | 0             | In (0,-1)                      | If all injection and load buses (nodes) are reported on (regardless of voltage)                                          |
| Report Lines In Interfaces            | Yes/No | 0             | In (0,-1)                      | If all flows on lines selected interfaces are reported                                                                   |
| Report Voltage Threshold              | kV     | 0             | >= 0                           | Voltage level at which transmission reporting begins.                                                                    |
| SCUC Constraint Voltage Threshold     | kV     | 0             | >= 0                           | Voltage level at which SCUC line thermal limits are modelled.                                                            |
| SCUC Enabled                          | Yes/No | 0             | In (0,-1)                      | If security constrained unit commitment (SCUC) is enabled                                                                |
| SCUC Interface Constraints Enabled    | Yes/No | 0             | In (0,-1)                      | If enabled interface constraints are monitored in SCUC.                                                                  |
| USE Threshold                         | %      | 100           | Between 0 And 100              | Formulates the [Unserved Energy] variables on the top x% nodes (highest load).                                           |
| Wheeling PTDF Threshold               | -      | 0.05          | >= 0                           | Minimum absolute value of PTDF as coefficient in wheeling definitions.                                                   |
| Write Kron-reduced Model              | Yes/No | 0             | In (0,-1)                      | If write Kron-reduced model is enabled.                                                                                  |
| Zero Limit Treatment                  | -      | 0             | In (0,1)                       | Treatment of AC elements with zero limits                                                                                |
