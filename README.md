# Project Work: Algorithms and Protocols for Security

## Description
This is the project carried out during the course of "Algorithms and Protocols for Security" in the A.Y. 2022-2023. The project was proposed by the owner of a virtual Bingo Hall who required the implementation of crucial functionalities for his software, including the continuous generation of random strings and the implementation of Green Pass 2.0 for access to virtual rooms.

## Project Structure
The project is divided into 4 work packages (WP), each with a specific objective:

### WP1: Model
- Definition of honest actors and potential adversaries.
- Identification of properties to be preserved.
- Creation of a threat model.

### WP2: Solution
- Designing the system to achieve a compromise between efficiency, transparency, confidentiality, and security.
- Detailed description of actions of the honest parties involved in the system.

### WP3: Analysis
- Analysis of the proposed solution compared to the model defined in WP1.
- Exhibition and justification of a radar chart to evaluate efficiency, confidentiality, integrity, and transparency of the system.

### WP4: Implementation and Performance
- Implementation of the designed system in a simulated environment.
- Evaluation of the system's performance, including response times and scalability.
- Detailed description of implementation choices and interaction processes.
- Utilization of OpenSSL commands for cryptographic functionalities.
- Performance evaluation table showcasing various execution phases.

## Implementation Details
### Release of GP 2.0
- Description of the chronological order of actions for users to obtain GP 2.0.
- Implementation details of user and Health Authority interaction.
- Utilization of cryptography commands from OpenSSL for implementation.

### Authentication at the Bingo Hall
- Description of the authentication process for players at the Bingo Hall.
- Interaction details between players, Bingo Hall, and Data Protection Authority.
- Implementation of TLS connection and client authentication.
- Utilization of Green Pass 2.0 for player authentication.

### Game at the Bingo Hall
- Implementation details of the Bingo game, supporting both blockchain and non-blockchain versions.
- Description of player-server interactions during the game rounds.
- Utilization of temporary keys for blockchain integration.
- Introduction of a Blockchain class for block management.

### Blockchain Integration
- Utilization of State Channels for blockchain integration.
- Implementation details of Blockchain class for block creation, verification, and appending.
- Introduction of various block types (PreGame, Commit, Reveal, PostGame, Dispute).
- Explanation of the Blockchain class's role in ensuring secure and transparent game operations.

## Performance Evaluation
The performance of the implemented system was evaluated during the experimentation phase. The collected data is presented in the performance evaluation table, showcasing the time taken for various phases of execution.

## Group Members
| Last Name, First Name | E-Mail                                                                   | ID          |
|-----------------------|--------------------------------------------------------------------------|-------------|
| Cerasuolo Cristian    | [c.cerasuolo2@studenti.unisa.it](mailto:c.cerasuolo2@studenti.unisa.it)  | 0622701899  |
| Ferrara Grazia        | [g.ferrara75@studenti.unisa.it](mailto:g.ferrara75@studenti.unisa.it)    | 0622701901  |
| Guarini Alessio       | [a.guarini7@studenti.unisa.it](mailto:a.guarini7@studenti.unisa.it)      | 0622702042  |

