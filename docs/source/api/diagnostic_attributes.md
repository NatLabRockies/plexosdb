# Diagnostic Attributes Reference

This page documents the PLEXOS Diagnostic class attributes and their default
values, validation rules, and descriptions.

To look at the open access PLEXOS documentation, go to
[PLEXOS Diagnostic Index](https://portal.energyexemplar.com/unified-help/plexos-desktop/index.htm#t=Index.Diagnostic.html&rhsearch=diagnostic).

Use this reference when setting configuration values through PlexosDB
attributes, for example with `add_attribute`, `get_attribute`, and
`list_attributes`.

## Diagnostic Attributes

| Name                              | Units  | Default Value | Validation Rule | Description                                                                                                 |
| --------------------------------- | ------ | ------------- | --------------- | ----------------------------------------------------------------------------------------------------------- |
| Algebraic                         | Yes/No | 0             | In (0,-1)       | Write LP files in algebraic format                                                                          |
| Annuities                         | Yes/No | 0             | In (0,-1)       | Write diagnostics for annuity calculations                                                                  |
| ATC Reports                       | Yes/No | 0             | In (0,-1)       | Write ATC min, ATC max, and most limiting elements for ATC to diagnostic files.                             |
| Bertrand Pricing                  | Yes/No | 0             | In (0,-1)       | Write diagnostics for the Bertrand pricing algorithm                                                        |
| Bid-Cost Mark-up                  | Yes/No | 0             | In (0,-1)       | Write diagnostics for RSI bid cost markup calculations                                                      |
| Binary Files                      | Yes/No | 0             | In (0,-1)       | Write math programs to disk in binary format                                                                |
| Binding Contingencies             | Yes/No | 0             | In (0,-1)       | Write diagnostics for binding Contingency constraints                                                       |
| Clear Existing                    | Yes/No | -1            | In (0,-1)       | Clear (delete) existing diagnostic files from the solution folder.                                          |
| Computer Information              | Yes/No | -1            | In (0,-1)       | Output computer information.                                                                                |
| Congestion Charges                | Yes/No | 0             | In (0,-1)       | Write diagnostics for Node.[Congestion Charge] calculations                                                 |
| Constraint Decomposition          | Yes/No | 0             | In (0,-1)       | Write diagnostics for constraint decomposition in MT Schedule                                               |
| Constraint Rollover               | Yes/No | 0             | In (0,-1)       | Write diagnostics for constraint RHS carry-over in ST Schedule                                              |
| Data File Read                    | Yes/No | 0             | In (0,-1)       | Output data file information to log file.                                                                   |
| Database Load                     | Yes/No | 0             | In (0,-1)       | Output the database loading process to log file.                                                            |
| Decimal Places LP                 | -      | 6             | >= 0            | Generic writer decimal places for LP file writing                                                           |
| Decimal Places SOL                | -      | 6             | >= 0            | Generic writer decimal places for SOL file writing                                                          |
| Embedded Losses                   | Yes/No | 0             | In (0,-1)       | Write diagnostics for embedded loss iterations                                                              |
| Feasibility Repair Weight         | Yes/No | 0             | In (0,-1)       | Write the weights used in feasibility repair for each variable/constraint class                             |
| Future Cost Function              | Yes/No | 0             | In (0,-1)       | Write diagnostics for the future cost function.                                                             |
| Generic Names                     | Yes/No | 0             | In (0,-1)       | Use generic names in math program files                                                                     |
| Heat Rate                         | Yes/No | 0             | In (0,-1)       | Write diagnostics for Generator Heat Rate curve fitting and non-convex corrections.                         |
| Historical Sampling               | Yes/No | 0             | In (0,-1)       | Write the historical samples.                                                                               |
| IIS                               | Yes/No | 0             | In (0,-1)       | Compute the irreducibly inconsistent set (IIS) for each infeasibility and write to disk in text format      |
| Infeasibility LP Files            | Yes/No | 0             | In (0,-1)       | Write infeasible and repaired math programs to disk in text format                                          |
| Infeasibility MPS Files           | Yes/No | 0             | In (0,-1)       | Write infeasible and repaired math programs to disk in MPS format                                           |
| Interleaved                       | Yes/No | 0             | In (0,-1)       | Write diagnostics for Model Interleaved run mode                                                            |
| Interruption Sharing              | Yes/No | 0             | In (0,-1)       | Write diagnostics for interruption sharing                                                                  |
| Levelized Company Costs           | Yes/No | 0             | In (0,-1)       | Write diagnostics for LT Plan Company Levelized Costs                                                       |
| Licensing                         | Yes/No | 0             | In (0,-1)       | Writes details of licenses checked out                                                                      |
| LP Files                          | Yes/No | 0             | In (0,-1)       | Write math programs to disk in LP text format                                                               |
| LP Progress                       | Yes/No | 0             | In (0,-1)       | Show progress messages from the LP/QP solver                                                                |
| Marginal Expansion Increment      | MW     | 1000          |                 | Increment used for load in the region marginal expansion unit diagnostic.                                   |
| Marginal Expansion Unit           | Yes/No | 0             | In (0,-1)       | Run algorithm to calculate the marginal generating unit for expansion (LT Plan).                            |
| Marginal Loss Charges             | Yes/No | 0             | In (0,-1)       | Write diagnostics for Node.[Marginal Loss Charge] calculations                                              |
| Marginal Unit                     | Yes/No | 0             | In (0,-1)       | Execute region marginal unit diagnostic (this is an active diagnostic)                                      |
| Marginal Unit Increment           | MW     | -1            |                 | Increment used for load in the marginal unit diagnostic.                                                    |
| Marginal Unit Transmission Detail | -      | 0             | In (0,1)        | Transmission area for marginal unit diagnostic                                                              |
| Max Infeasibility Log Lines       | -      | -1            | >= -1           | Maximum number of infeasibility diagnostic lines written to the screen and log file.                        |
| MIP Progress                      | Yes/No | 0             | In (0,-1)       | Show progress messages from the MIP solver                                                                  |
| Monitored Iterations              | Yes/No | 0             | In (0,-1)       | Print messages for every iteration of row/column monitoring                                                 |
| Monitored Iterations Summary      | Yes/No | 0             | In (0,-1)       | Print a summery message after iterations of row/column monitoring                                           |
| MPS Files                         | Yes/No | 0             | In (0,-1)       | Write math programs to disk in MPS text format                                                              |
| Network Traversal                 | Yes/No | 0             | In (0,-1)       | Invokes network reduction algorithm which can improve performance on large-scale networks.                  |
| New Entry                         | Yes/No | 0             | In (0,-1)       | Write diagnostics for MT Schedule new entry calculations                                                    |
| NPV                               | Yes/No | 0             | In (0,-1)       | Write diagnostics for LT Plan NPV of optimal plan                                                           |
| Objective Function                | Yes/No | 0             | In (0,-1)       | Write diagnostics for non-zero terms in the objective function.                                             |
| Outages                           | Yes/No | 0             | In (0,-1)       | Write diagnostics for generator and line outages                                                            |
| Performance Summary               | Yes/No | -1            | In (0,-1)       | Print performance summary at the completion of each simulation phase.                                       |
| Random Number Seed                | Yes/No | 0             | In (0,-1)       | Write out the Random Number Seed used for each Generator and Line                                           |
| Region Supply                     | Yes/No | 0             | In (0,-1)       | Execute region supply diagnostic (this is an active diagnostic)                                             |
| Revenue Recovery                  | Yes/No | 0             | In (0,-1)       | Write diagnostics for the LRMC recovery algorithm                                                           |
| Sample From                       | -      | 1             | >= 1            | Limit diagnostic file writing to sample numbers starting at this number.                                    |
| Sample Reduction                  | Yes/No | 0             | In (0,-1)       | Write diagnostics for reduced sample periods and periods mapping by sampled chronology.                     |
| Sample Summary                    | Yes/No | 0             | In (0,-1)       | Print summary for each sample of a multi-sample run.                                                        |
| Sample To                         | -      | -1            | >= -1           | Limit diagnostic file writing to sample numbers ending at this number (-1 means infinity).                  |
| Sample Weights                    | Yes/No | 0             | In (0,-1)       | Write diagnostics for the sample weights                                                                    |
| Scenario Tree                     | Yes/No | 0             | In (0,-1)       | Write diagnostics for the scenario tree                                                                     |
| SDDP Convergence                  | Yes/No | 0             | In (0,-1)       | Write SDDP convergence diagnostic file                                                                      |
| Shift Factors                     | Yes/No | 0             | In (0,-1)       | Write the computed shift factors (PTDF) to a diagnostic file                                                |
| Skip Zero Values                  | Yes/No | 0             | In (0,-1)       | Generic writer will print only non-zero valued primal and dual variables in SOL files                       |
| Solution Files                    | Yes/No | 0             | In (0,-1)       | Write math program solutions to disk in text format                                                         |
| Solution Status                   | Yes/No | 0             | In (0,-1)       | Status of the solution to each mathematical programming problem.                                            |
| Solver Summary                    | Yes/No | 0             | In (0,-1)       | Print a summary of the solution status, objective function value, etc for each mathematical program solved. |
| Sort Row Column Names             | Yes/No | 0             | In (0,-1)       | Generic writer will sort row and columns names                                                              |
| Standardize Names                 | Yes/No | 0             | In (0,-1)       | Generic writer will standardize names in LP and SOL files                                                   |
| Step From                         | -      | 1             | >= 1            | Limit diagnostic file writing to step numbers starting at this number.                                      |
| Step Summary                      | Yes/No | 0             | In (0,-1)       | Print summary for each step of a multi-step run.                                                            |
| Step To                           | -      | -1            | >= -1           | Limit diagnostic file writing to step numbers ending at this number (-1 means infinity).                    |
| Storage Decomposition             | Yes/No | 0             | In (0,-1)       | Write diagnostics for storage decomposition                                                                 |
| Strip Model Name                  | Yes/No | 0             | In (0,-1)       | Generic writer will strip out the Model name from LP and SOL files                                          |
| Summary Exact Conditioning        | Yes/No | 0             | In (0,-1)       | Report exact basis condition number (if available) in the solver summary.                                   |
| Task Components                   | Yes/No | 0             | In (0,-1)       | Print a summary of the formulation elements by class.                                                       |
| Task Size                         | Yes/No | 0             | In (0,-1)       | Print the size of the optimization task.                                                                    |
| Times                             | Yes/No | -1            | In (0,-1)       | Print the time taken for each activity.                                                                     |
| Transmission Losses               | Yes/No | 0             | In (0,-1)       | Write diagnostics for convergence of the quadratic loss method                                              |
| Transmission Topology             | Yes/No | 0             | In (0,-1)       | Write a summary of the transmission topology to the log                                                     |
| Uniform Pricing                   | Yes/No | 0             | In (0,-1)       | Write diagnostics for uplift and Uniform Pricing                                                            |
| Unit Commitment                   | Yes/No | 0             | In (0,-1)       | Write diagnostics for the Rounded Relaxation unit commitment algorithm                                      |
| Unserved Energy                   | Yes/No | 0             | In (0,-1)       | Write diagnostics each time USE occurs at a node                                                            |
| Use Generic Writer                | Yes/No | 0             | In (0,-1)       | Use generic writer for LP and solution files                                                                |
| Zero Tolerance LP                 | -      | 0             | >= 0            | Generic writer zero value tolerance for LP file writing                                                     |
| Zero Tolerance SOL                | -      | 0             | >= 0            | Generic writer zero value tolerance for SOL file writing                                                    |
