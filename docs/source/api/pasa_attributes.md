# PASA Attributes Reference

This page documents the PLEXOS PASA class attributes and their default values,
validation rules, and descriptions.

To look at the open access PLEXOS documentation, go to
[PLEXOS PASA Index](https://portal.energyexemplar.com/unified-help/plexos-desktop/index.htm#t=Index.PASA.html&rhsearch=lt%20plan).

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## PASA Attributes

| Name                                   | Units  | Default Value | Validation Rule   | Description                                                                                                             |
| -------------------------------------- | ------ | ------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Compute Multi-area Reliability Indices | Yes/No | 0             | In (0,-1)         | Master switch for computation of reliability indices LOLP, LOLE, etc across multiple areas.                             |
| Compute Reliability Indices            | Yes/No | 0             | In (0,-1)         | Master switch for computation of reliability indices LOLP, LOLE, etc.                                                   |
| Constraints Enabled                    | Yes/No | -1            | In (0,-1)         | If transmission line constraints are enabled in PASA.                                                                   |
| Energy Objective                       | %      | 0             | Between 0 And 100 | Relative contribution of energy margins to PASA objective function                                                      |
| Include Contract Generation            | Yes/No | 0             | In (0,-1)         | Include physical contract generation capacity in PASA                                                                   |
| Include Contract Load                  | Yes/No | 0             | In (0,-1)         | Include physical contract load capacity in PASA                                                                         |
| Include Demand Bids                    | Yes/No | 0             | In (0,-1)         | Include demand bids are load in PASA                                                                                    |
| Include DSP                            | Yes/No | -1            | In (0,-1)         | Include demand-side participation in PASA                                                                               |
| Include Market Purchases               | Yes/No | 0             | In (0,-1)         | Include market purchases as generation capacity in PASA                                                                 |
| Interface Constraints Enabled          | Yes/No | -1            | In (0,-1)         | If transmission interface constraints are enabled in PASA.                                                              |
| Maintenance Sculpting                  | %      | 0             | Between 0 And 100 | Level of sculpting of maintenance outages: Higher sculpting means outages are more concentrated in high reserve periods |
| Reliability Criterion                  | -      | 0             | In (0,1)          | Criterion used to select periods for Monte Carlo reliability analysis                                                   |
| Reliability LOLP Tolerance             | -      | 0.01          | >= 0              | For reliability-based sampled chronology using LOLP criterion select intervals with LOLP at or above this level         |
| Reliability Max Samples                | h      | 1E+30         | >= 1              | For reliability-based sampled chronology select no more than this many hours per year                                   |
| Step Type                              | -      | 1             | In (0,1,2)        | PASA step type: One period is modelled for each period of this type in horizon.                                         |
| Stochastic Method                      | -      | 0             | In (0,1,2,3)      | Stochastic optimization method for PASA.                                                                                |
| Transmission Detail                    | -      | 0             | In (0,1,2)        | Definition of maintenance area for PASA.                                                                                |
| Write Outage Text Files                | Yes/No | 0             | In (0,-1)         | If outage patterns should be written to text files                                                                      |
| Write Reliability Text Files           | Yes/No | 0             | In (0,-1)         | If the periods selected for Monte Carlo reliability analysis should be written to text files                            |
