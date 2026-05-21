# ST Schedule Attributes Reference

This page documents the PLEXOS ST Schedule attributes and their default values,
validation rules, and descriptions.

To look at the open access PLEXOS documentation, go to
[PLEXOS ST Schedule Index](https://portal.energyexemplar.com/unified-help/plexos-desktop/index.htm#t=Index.STSchedule.html&rhsearch=lt%20plan).

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## ST Schedule Attributes

| Name                           | Units  | Default Value | Validation Rule  | Description                                                                                                          |
| ------------------------------ | ------ | ------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| Discount Period Type           | -      | 2             | In (1,2,3,4,6,7) | A unique discount factor will be computed for each of these periods.                                                 |
| Discount Rate                  | %      | 0             | >= 0             | Discount rate.                                                                                                       |
| Discount Rate Reset            | Yes/No | 0             | In (0,-1)        | Flag if discount factor resets at the beginning of each ST Schedule step.                                            |
| End Effects Method             | -      | 1             | In (0,1)         | Method used to account for end of horizon discounting.                                                               |
| Sequential Steps               | -      | 1             | >= 1             | Number of steps run in each sequential block when running in parallel Step Link Mode.                                |
| Step Link Mode                 | -      | 0             | In (0,1,2)       | Controls how the solutions of each step are linked together.                                                         |
| Step Relink Count              | -      | 1             | >= 1             | Number of steps that require relinking of initial conditions in parallel Step Link Mode, where 1 means no relinking. |
| Stochastic Method              | -      | 1             | In (0,1,2,3)     | Stochastic optimization method for ST Schedule.                                                                      |
| Storage Formulate Head Effects | Yes/No | -1            | In (0,-1)        | If storage head effects should be formulated in ST Schedule.                                                         |
