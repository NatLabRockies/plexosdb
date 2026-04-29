# Model Attributes Reference

This page documents the PLEXOS Model class attributes and their default values,
validation rules, and descriptions.

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## Model Attributes

| Name                         | Units  | Default Value | Validation Rule          | Description                                                                                                          |
| ---------------------------- | ------ | ------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| Enabled                      | Yes/No | 0             | In (0,-1)                | If the model is ready to be executed                                                                                 |
| Execution Order              | -      | 0             | >= 0                     | Order in which to execute the Model when running in a batch.                                                         |
| Load Custom Assemblies       | Yes/No | -1            | In (0,-1)                | If the Model should run custom OpenPLEXOS assemblies.                                                                |
| Make Unique Name             | -      | 0             | In (-1,0,1)              | If model output should be written to a unique filename for each execution                                            |
| Objective Absolute Tolerance | -      | 0             | >= 0                     | Allowable degradation for the objective when doing hierarchical multi-objective optimization for MIP models          |
| Objective Priority           | -      | 1             | >= 0                     | Priority of the objective when doing hierarchical multi-objective optimization                                       |
| Objective Relative Tolerance | -      | 0             | Between 0 And 1          | Allowable relative degradation for the objective when doing hierarchical multi-objective optimization for MIP models |
| Objective Weight             | -      | 1             |                          | Weight of the objective when doing blended multi-objective optimization                                              |
| Output to Folder             | Yes/No | -1            | In (0,-1)                | If model output should be written to a folder under the source directory, or into the source folder itself           |
| Random Number Seed           | -      | 0             | Between 0 And 2147483647 | Random number seed for this model                                                                                    |
| Run Mode                     | -      | 0             | In (0,1)                 | Switches between Normal and Dry run modes                                                                            |
| Write Input                  | Yes/No | 0             | In (0,-1)                | If Model input should be written to the output location along with the solution.                                     |
