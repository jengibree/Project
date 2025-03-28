Group members: Xinyuan Hu, Jingyao Wang Wu, Lyla Wu 

Our emails: xhu36@u.rochester.edu, ywu143@u.rochester.edu, jwangwu@u.rochester.edu

Submitter: Jingyao Wang Wu

To avoid discrepancies, a TA told us that only one person should submit everything, while the other two group members
can just submit the README. 

# Overview
This program is a Bayesian Network Inference Tool designed to compute posterior probabilities using two methods: exact inference and approximate inference. It reads a Bayesian network structure and its associated conditional probability tables (CPTs) from an XML file. Users can input evidence and query variables to calculate probabilities based on the Bayesian network model.

The Bayesian network is represented by a variable class, where each variable has a name, a set of possible values, a list of parent variables, and its conditional probability table (CPT). The parse_table function processes the CPTs and organizes them into a usable format, handling cases both with and without parent variables.

# How to Run Our Code
We used Pycharm to do this project. In the Pycharm terminal, for example, to run aima-alarm.xml, input "Python main.py aima-alarm.xml". Then the code will prompt you to enter the query variable, then the evidence variables, and then ask you with inference you want to implement. If you want to implement exact inference, enter 1, otherwise, enter 2. If you enter 1, it will calculate the exact inference values, but if you enter 2, it will prompt you to enter the sample size, and then calculate the approximate inference values.

# Our Exact Inference Code
Exact inference employs the enumeration algorithm to compute posterior probabilities accurately. This method is computationally efficient for small or moderately complex networks but can become resource-intensive for larger networks. 

The enumeration_ask function calculates the posterior probabilities of the query variable given the evidence by iterating through all possible values of the query variable. It uses the enumerate_all function to recursively compute probabilities for all variables in the network while distinguishing between observed and hidden variables. Results are normalized using the normalize function to make sure they sum to one.

# Our Approximate Inference Code
Approximate inference uses rejection sampling to estimate posterior probabilities by generating samples and filtering those consistent with the given evidence. This method is faster for large networks but provides approximate results that improve in accuracy with more samples.

We chose to implement Rejection Sampling.

The rejection_sampling function generates a set number of samples from the prior distribution using the prior_sample function, which simulates values for all variables based on their probability distributions. Samples that match the evidence are counted, and their frequencies are normalized to estimate posterior probabilities. 

The is_consistent function verifies whether a sample is consistent with the evidence, while the weighted_sample function ensures values are drawn according to their respective probabilities.

The topological_sort function organizes the variables in the Bayesian network into a topological order based on their dependencies. This is what allowed dog-problem.xml to work with our rejection sampling. The function uses a queue-based approach to identify nodes with zero parents and iteratively removes them, appending them to the sorted order. This ensures that any variable appears in the order only after its parents. If a cycle is detected, the function raises an error, as cycles are not allowed in Bayesian networks.

# Our main function
The main function puts everything together. It begins by parsing the Bayesian network structure and CPTs from the provided XML file, using code provided by Read.py. The code prompts the user to input a query variable, evidence, and the inference method. Depending on what the user chooses, the program executes either exact inference or rejection sampling and displays the results in a clear, formatted output.

# Evaluation
We used aima-alarm.xml to test our approximate inference code. The results were very inconsistent with sample amount under 1,000,000.

It does take a little bit of time to run, so please be patient if you run it since the sample size is so large.

So, we ran it a few times with sample number of 1,000,000. Here are the results:

We first used exact inference on P(B=true | J=true, M=true) to get {true: 0.2842, false: 0.7158}, which matches the values in the textbook.

1st run of Approximate Inference: P(B | J=true, M=true): {'true': 0.2797, 'false': 0.7203}
2nd run of Approximate Inference: P(B | J=true, M=true): {true: 0.2809, false: 0.7191}
3rd run of Approximate Inference: P(B | J=true, M=true): {true: 0.2834, false: 0.7166}
4th run of Approximate Inference: P(B | J=true, M=true): {true: 0.2845, false: 0.7155}
5th run of Approximate Inference: P(B | J=true, M=true): {true: 0.2877, false: 0.7123}

The sample size needed for our code to be within 1% of the exact value is 1,000,000.


