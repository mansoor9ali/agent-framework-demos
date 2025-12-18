# Table of contents

- [1. What is an AI Agent?](#1. What is an AI Agent?)
- [2. What are the mainstream design patterns for AI agents?](#2. What are the mainstream design patterns for AI agents?)
- [3. What is a function call in an AI Agent?](#3. What is a function call in an AI Agent?)
- [4. What is the MCP (Model Context Protocol) in an AI Agent?](#4. What is the MCP (Model Context Protocol) in an AI Agent?)
- [5. What is the difference between function call and MCP in AI Agent?](#5. What is the difference between function call and MCP in AI-Agent?)
- [6. Agent2Agent (A2A) in AI Agent?](#6. Agent2Agent (A2A) in AI Agent?)
- [7. What is the difference between A2A and MCP in AI Agent?](#7. What is the difference between A2A and MCP in AI-Agent?)
- [8. What are the mainstream core models in current AI agents?](#8. What are the mainstream core models in current AI agents?)
- [9. What are the functions of the system prompts in the AI ​​Agent?](#9. What are the functions of the system prompts in the AI-Agent?)
- [10. How to build powerful system prompts in AI Agent?](#10. How to build powerful system prompts in AI-Agent?)
- [11. How does System Prompt work internally within the AI ​​Agent?](#11. How does System-Prompt work internally within the AI-Agent?)
- [12. What's the difference between AI Search and regular Search?](#12. What's the difference between AI Search and regular Search?)
- [13. What is DeepSearch?](#13. What is DeepSearch?)
- [14. What is the difference between AI Agent and AI Workflow?](#14. What is the difference between AI-Agent and AI-Workflow?)
- [15. In AI Agents, how do function calls transform external tools into a way that large models can understand?](#15. In AI Agents, how do function calls transform external tools into a way that large models can understand?)
- [16. In AI Agents, how do large models learn Function Calling capabilities?](#16. In AI Agents, how do large models learn Function Calling capabilities?)
- [17. What are the limitations of current AI agents?](#17. What are the limitations of current AI-Agents?)
- [18. What are the mainstream evaluation metrics for current AI agents?](#18. What are the mainstream evaluation metrics for current AI-Agents?)
- [19. How do AI agents possess long-term memory capabilities?](#19. How do AI-Agents possess long-term memory capabilities?)
- [20. Introduce the principle and function of the memory mechanism in AI Agent](#20. Introduce the principle and function of the memory mechanism in AI Agent)
- [21. Introduce the principle of context engineering in AI agents](#21. Introduce the principle of context engineering in AI agents)
- [22. What are the mainstream AI agent frameworks currently available?](#22. What are the mainstream AI-Agent frameworks currently available?)
- [23. What are the core modules included in mainstream AI agents?](#23. What are the core modules included in mainstream AI agents?)
- [24. What are the differences between Memory and RAG in AI Agent?](#24. What are the differences between Memory and RAG in AI Agent?)


<h2 id="1. What is an AI Agent?">1. What is an AI Agent?</h2>

In the era of AIGC, Rocky believes that AI Agents are a very important direction and an inevitable trend in the development of AIGC technology.

So, what exactly is an AI Agent?

Rocky will first explain the operating logic of the non-AI agent, that is, the regular AIGC large model, and then we will have an epiphany from the comparison between the two.

Taking classic text content creation as an example 🌰, **the workflows of non-intelligent agents, intelligent agents, and human creators show significant differences:**

| **Subject Type** | **Execution Characteristics** | **Process Analysis** |
|----------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **Non-Agent** | Linear single-output | User input prompts → large model directly generates final version (no iteration process) |
| **AI Agent (Intelligent Agent)** | Multi-stage Cognitive Loop | Outline Planning → Resource Retrieval → Draft Generation → Self-Check and Revision → Iterative Optimization → Final Draft Output (Simulating Human Creative Thinking) |
| **Human Creator** | Cognitive-Driven Workflow | Conceptualization → Information Gathering → Content Filling → Cross-Review → Iterative Polishing (Highly Isomorphic to Agent-Based Workflow) |


We can see that the core of AI Agents is to achieve a digital twin of human work paradigms through a cognitive loop of task deconstruction-execution-reflection.

![Agent Diagram](imgs/Agent Diagram.png)

**AI industry expert Andrew Ng believes that the ultimate evolution of AI agents is to build digital entities with complete cognitive capabilities, and its technical architecture can be broken down into four core capabilities:**

1. **Reflection:** The AI ​​Agent simulates human self-correction behavior, much like a student checking their work after completion. It overcomes the limitations of single-step reasoning by establishing a reinforced loop of error detection-feedback-correction. This enables a leap in quality in high-precision scenarios such as code generation and legal document processing.
2. **Tool use:** The AI ​​Agent determines its own capability boundaries and selects appropriate AI tools (AI services/search engines/professional databases, etc.) to enhance the capability boundaries of the large model.
3. **Planning:** The ability of an AI Agent to develop a reasonable action plan to achieve a goal when solving complex problems, thereby breaking down the task.
4. **Multi-agent collaboration:** The combined application of multiple AI agents allows us to envision a scenario where each user can configure their own dedicated AI team (product manager agent + engineer agent + testing agent + business marketing agent, etc.), which will restructure traditional production models.

![Multi-Agent System](imgs/Multi-Agent System.png)

We all know that the field of autonomous driving distinguishes between L1 and L5 levels of technology, with higher levels indicating a closer approach to fully autonomous driving. In the AIGC era, we can similarly classify the evolution path of AIGC technology capabilities into five levels:

| **Levels** | **Capability Positioning** | **Human-Machine Collaboration Paradigm** | **Evolutionary Status** |  
|----------|--------------------|---------------------------------------------------------------------------------|---------------------|  
| **L1** | Basic Tools | Users complete the entire process independently; the system has no explicit AI capabilities | Technology replacement in progress |  
| **L2** | Chatbot | User-led execution, AI provides information references (such as knowledge retrieval and suggestion generation) | Basic application form |  
| **L3** | Collaborative Creation (Copilot) | Human-Computer Task Sharing: User sets goals → AI generates initial draft → User corrects and confirms | Current Core Value Area |  
| **L4** | Intelligent Agent | User-defined goals and resources; AI autonomously achieves a closed loop of task decomposition, tool scheduling, and process control | Near the general AGI tipping point |  
| **L5** | General Intelligence | The system autonomously completes goal definition, resource acquisition, tool invocation, and result delivery | Theoretical Development Stage |  

Currently, the core of AI agents is still based on large LLM models and deep learning prompts. **Rocky believes that future AI agents will have more depth, for example:**
1. The core large model in the AI ​​Agent may be built based on the AIGC multimodal large model.
2. AI Agents will include more modal capabilities, such as images, videos, audio, and digital humans.
3. There will be blockbuster AIGC products based on AI Agents.
4. AI algorithm solutions based on AI agents will be implemented in various industries, reshaping their business models.


2. What are the mainstream design patterns for AI agents?

Currently mainstream AI agents (Manus, Deep Research, etc.) are all built on a large LLM model plus a complete AIGC algorithm solution (Prompts project, Function Call, MCP, AI engineering strategy, AI function service, etc.), and their connotation will continue to be expanded and extended in the future.

Based on the above framework, five mainstream AI Agent design patterns were then developed:

1. **Reflection pattern:** The core mechanism of this pattern is to build a self-checking and error-correcting iterative loop. The AI ​​Agent reviews its work to find errors and iterates until the final output is generated.

![Agent reflection pattern](imgs/Agent reflection pattern.gif)

2. **Tool use pattern:** The AI ​​Agent allows large LLM models to obtain more information by using external tools, including calling APIs, using AI services, querying vector databases, and executing Python scripts. **This allows large LLM models to expand their knowledge boundaries not only by relying on their internal knowledge but also by accessing the vast real-time data streams of the internet.**

![Agent tool usage pattern](imgs/Agent tool usage pattern.gif)

3. **ReAct Mode (Reason and Act):** The ReAct mode combines reflection and tool usage, making it one of the most powerful modes currently used by AI agents. AI agents can both think for themselves and correct their own errors, and also use tools to interact with the world.

![Agent-ReAct mode](imgs/Agent-ReAct mode.gif)

4. **Planning Pattern:** In this pattern, the AI ​​Agent designs a task planning process based on the complexity of the task, subdivides the task, and then processes the subdivided subtasks using the ReAct pattern. This pattern can be considered a strategic thinking approach, capable of more effectively solving strategically complex tasks.

![Agent Planning Pattern](imgs/Agent Planning Pattern.gif)

5. **Multi-agent pattern:** In this pattern, the AI ​​Agent system contains multiple sub-agents, each assigned a specific role and task. Each sub-agent can also access external tools for comprehensive work. Finally, all sub-agents collaborate to provide the final result, while delegating further subdivisions to other sub-agents as needed, forming a complex "AI Agent collaborative community."

![Agent Multi-Agent Mode](imgs/Agent Multi-Agent Mode.gif)


<h2 id="3. What is a function call in an AI Agent?">3. What is a function call in an AI Agent?</h2>

In the AI ​​Agent architecture, **Function Call is essentially a closed-loop process in which an intelligent agent calls external capabilities (APIs, AI services, AI tools, databases, search engines, etc.) through the LLM large model and integrates and processes them.**

Next, Rocky will give a vivid example to help us understand the entire process of a Function Call in a simple and easy-to-understand way.

Suppose we already have an AI Agent system, whose core LLM models are DeepSeek and GPT-4o. We want to design an AI service that can quickly help our girlfriends buy stockings - "Stocking Selection Service", to enable the AI ​​Agent to flexibly help our girlfriends select stockings.

At this point, the overall process of a Function Call is as follows:
1. Demand Analysis Phase: We input the question of purchasing stockings. The LLM model (DeepSeek/GPT-4o) first parses the user's natural language request (e.g., "Buy polka dot black stockings for my girlfriend") and identifies the core parameters:
```python  
{"Category": "Stockings", "Style": "Polka Dots", "Color": "Black", "User Identity": "Gift"}  
``` 
2. Tool Orchestration Phase: If the question involves selecting stockings, the LLM model analyzes and generates the necessary functions for calling the stockings selection service, along with the parameters to be passed to these functions, generating structured JSON commands for the call.
```json  
     {  
       "function": "hosiery_selection_service",  
       "parameters": {  
         "material": "nylon-spandex",  
         "opacity": "sheer",   
         "color": "black",  
         "purpose": "gift"  
       }  
     }  
```  
3. Service Execution Phase: Next, the stockings purchasing service function is invoked, returning a structured result:
```json  
     {  
       "recommendations": [  
         {"brand": "Wolford", "price": 189, "features": ["anti-snagging", "slightly transparent"]},  
         {"brand": "Calzedonia", "price": 89, "features": ["Simple Shaping", "Breathable"]}  
       ],  
       "delivery_time": "same-day delivery"  
     }  
 ```  
5. Response Synthesis Stage: Finally, the content returned by the function is appended to the input prompts and fed into the larger model. This allows the model to summarize and refine the answer, and then generate a response for us.
 
"Two high-quality black stockings are recommended:"  
1. **Wolford Sheer Style** (189 RMB): Top-tier anti-snagging technology, semi-transparent design enhances comfort.  
2. **Calzedonia Shaping Model** (89 RMB): Simple and slimming while highly breathable.  
> ⚡️All items can be delivered today. For gifts, we recommend Wolford gift box packaging.”  

### **Full-Process Visualization Charts**
```mermaid
graph TB
    A [User input: "Recommendations for polka dot black stockings for girlfriend"] --> B {Requirement Analysis}
    B -->|DeepSeek/GPT-4o| C [Parameter Structured Extraction<br>▪ Material: Nylon-Spandex<br>▪ Style: Polka Dot<br>▪ Color: Black<br>▪ Scene: Gift Giving]
    C --> D{Instrumental Decision}
    D -->|Function matching| E[Calls hosiery_selection_service<br>material='nylon-spandex', opacity='sheer', ...]
    E --> F [Real-time e-commerce API query<br>▪ Brand inventory<br>▪ Price range<br>▪ Logistics timeliness]
    F --> G{Result Integration}
    G -->|LLM Contextual Restructuring| H[Natural Language Response<br>▪ Product Comparison<br>▪ Gift Suggestions<br>▪ Delivery Information]
```

At this point, you should have a clear understanding of AI Agent Function Calls. Next, let's summarize the essential differences between Function Calls and traditional API calls:

   | **Dimensions** | Traditional API Call | Agent Function Call |  
   |------------------|--------------------------|------------------------------|  
   Input Format | Structured Parameters (JSON/XML) | Natural Language Commands |  
   | **Caller** | Developer hard-coded trigger | Agent autonomous decision-making trigger |  
   Error Handling | Explicit Exception Handling | Reflection-based Automatic Retry/Replacement Tool |  
   | **Protocol Dependencies** | Fixed communication protocols (REST/gRPC) | Supports adaptive protocols such as MCP |  


### Key Stage Analysis:
1. **Intent Recognition**  
   - The large model analyzes the semantics of "query the weather" and locates the tool category.  
2. **Parameter Extraction**  
   - Extract structured parameters from natural language (`Material`: `Nylon-Spandex`, `Style`: `Polka Dot`, `Color`: `Black`, `Scenario`: `Gift`)  
3. **Protocol Conversion**  
   - The calling format required by the generation tool (such as the OpenAI Function Calling specification).  
4. **Results Integration**  
   - Convert the data returned by the tool into a natural language response  

**Technological Philosophy Implications:** As Function Call evolves from a technological component into a universal interface between AI Agents and reality, humanity is granting artificial intelligence the "power to act." This is not only an efficiency revolution but also a shift in cognitive paradigms—we no longer need to understand the structure of a screwdriver; we can simply say, "Please hang the picture on the wall."


<h2 id="4. What is the MCP (Model Context Protocol) in AI Agent?">4. What is the MCP (Model Context Protocol) in AI Agent?</h2>

On November 25, 2024, Anthropic released a technical white paper, "Model Context Protocol: A Standardized Interface for AI Integration," which first proposed the concept of MCP (Model Context Protocol framework).

MCP (Model Context Protocol) establishes a specification for context exchange between large AI models and external applications. This allows AI developers to connect various real-time data sources, AI tools, and add-ins to the AIGC large model using a consistent standard, much like Type-C allows different devices to connect to a host through the same interface. The goal of MCP is to create a universal standard that makes the development and integration of AI applications simpler and more unified.

Before MCP, function calling when AIGC large models interacted with external functions could vary widely. This resulted in a large number of applications and diverse AIGC large models, but they were not necessarily compatible and combinable. MCP provides a more standardized way for AIGC large models to use different external tools, as long as these external tools define their input and output specifications according to the MCP protocol.

MCP consists of three core components: Host, Client, and Server. Let's understand how these components work together through a practical example:

Let's say we're using an AI agent to ask, "Want me to buy some stockings for my girlfriend?"

Host: The AI ​​Agent acts as the host, responsible for receiving our questions and interacting with the AIGC large model within it.
Client: When the AIGC large model needs to determine a stocking purchase plan, the built-in MCP Client in the Host will be activated. This Client is responsible for establishing a connection with the appropriate MCP Server.
Server: In this example, the stocking purchase scheme MCP Server will be invoked. It is responsible for performing the actual stocking purchase scheme determination operation, accessing the corresponding e-commerce API, and returning the found stocking purchase scheme.

The entire process is as follows: Our question → AI Agent (Host) → AIGC large model → Requires stocking purchase information → MCP Client connection → Stocking purchase MCP Server → Execute operation → Return result → AIGC large model generates answer → Display on AI Agent.

This architecture design allows the AIGC large model in the AI ​​Agent to flexibly call various application tools and data sources in different scenarios, while AIGC developers only need to focus on developing the corresponding MCP Server, without having to worry about the implementation details of Host and Client.

![MCP Protocol Diagram.png](imgs/MCP%E5%8D%8F%E8%AE%AE%E7%A4%BA%E6%84%8F%E5%9B%BE.png)


5. What is the difference between function call and MCP in AI Agent?

From the perspective of the AI ​​Agent field, **MCP can be seen as a further extension and encapsulation of function calls**.

Function calls solve the problem of interaction between AIGC large models and external application tools; while MCP standardizes the entire interaction process on this basis, thereby solving the "island" problem between massive data, AIGC large models, and AI application tools.


<h2 id="6. AI-Agent in Agent2Agent(A2A)?"">6. AI Agent in Agent2Agent(A2A)?</h2>

The **Agent2Agent (A2A) protocol** is the core communication framework driving the multi-agent ecosystem. Its essence is a **standardized protocol between AI Agents**, and also a "social contract" between Agents.

Before the A2A protocol, different Agent A (DeepSeek) and Agent B (GPT-4o) had different output formats, making it impossible for them to cooperate and creating many isolated AI Agents.

Therefore, the A2A protocol provides a common language for interoperability and interaction between heterogeneous AI agents:

   ```mermaid
   graph LR
       A [Agent A] --> |Native JSON| B [A2A Protocol Layer]
       C[Agent B] -->|Native XML| B
       B --> D [Unified Communication Format]
       D --> E [Consensus Decision Engine]
   ```

### Core Working Mechanism
#### 1. **Distributed Consensus Process**
   **Case Study: Collaborative Report Writing by Multiple Agents**
   ```mermaid
   graph TB
       A [Researcher Agent] --> | Submit Initial Draft | B [Consensus Pool]
       C [Data Analysis Agent] --> | Add Chart | B
       D [Compliance Agent] --> |Legal Review | B
       B --> E {Has a consensus been reached?}
       E -->|Yes| F [Final Draft Released]
       E -->|No| G [Start Modify Agreement]
   ```
   - **Practical Byzantine Fault Tolerance (PBFT)**: Consensus can still be reached even with 1/3 of the nodes failing.

#### 2. **Cross-platform identity authentication**
   - **Agent Passport System**:
     ```json
     {
       "id": "agent://medical/diag-009",
       "issuer": "Huawei_A2A_Cert",
       "public_key": "0x23a7...",
       "scope": ["diagnosis", "report_gen"],
       "expiry": 1735689600
     }
     ```
   - **Verification Process**:  
     JWT signature verification → Permission scope check → Expiration verification

### Industrial Application Scenarios
#### 1. **Smart Manufacturing: Flexible Production Line Scheduling**
   ```mermaid
   graph LR
       O[Order Agent] -->|Demand Command| P[Plan Agent]
       P --> M1 [Machine Tool Agent]
       P --> M2 [Robotic Arm Agent]
       M1 -->|Completion Notice| Q[Quality Inspection Agent]
       M2 --> Q
       Q -->|Quality Report| S[Warehouse Agent]
   ```
   **Results:** After deployment at a factory in Dongguan, changeover time was reduced by 76%.

#### 2. **Smart Cities: Emergency Response Alliance**
   | **Agent Types** | **Disaster Response Actions** | **Coordination Rules** |
   |---------------|------------------------|--------------------------|
   Traffic Agent | Close damaged road sections | Prioritize rescue access |
   | Medical Agent | Dispatch Ambulances | Response Based on Injury Severity Level |
   | Power Grid Agent | Cut off power to hazardous areas | Synchronize with firefighting agent actions |
   - **Real Event: Hangzhou Asian Games Rainstorm Coordination Response Speeded Up 3 Times**

#### 3. **Financial Transactions: Cross-border Payment Networks**
   - **SWIFT Alternatives**:
     ```python
     def cross_border_payment(sender, receiver, amount):
         # Multi-Agent Collaborative Verification
         AML_Agent.check_suspicion(sender) # Anti-money laundering audit
         FX_Agent.convert_currency(amount) # Real-time currency exchange
         Settlement_Agent.execute(receiver) # On-chain liquidation
     ```
   - **Advantages:** The traditional 3-day process is reduced to 8 minutes, and costs are reduced by 60%.

### Technological Philosophy Implications  
When a medical agent sends `{"action": "compound_design", "target": "EGFR_L858R"}` to a drug development agent via the A2A protocol, humanity witnesses **the first trade of machine civilization**. The A2A protocol is not merely a technical standard, but also a "Code of Hammurabi" for intelligent agent societies—it defines the boundaries of rights with code, establishes trust mechanisms with algorithms, and will ultimately give rise to a **revolution in production relations for silicon-based civilization**.


What is the difference between A2A and MCP in AI Agent?

The MCP protocol addresses the interaction between AI Agents and various external tools/resources. It can be viewed as an AI application store protocol, primarily focusing on how individual AI Agents can better utilize external tools.

The A2A protocol addresses the interaction between AI Agents, focusing primarily on how different AI Agents collaborate.

In summary, they are complementary and work together to build the AI ​​Agent ecosystem.


8. What are the mainstream core models in current AI agents?

Rockyu has summarized the mainstream core models in current AI Agents. As the field of AI Agents continues to develop, it is believed that more core models will emerge in the future, and Rocky will continue to update this Q&A.
1. Claude - 3.7/4 - Sonnet
2. DeepSeek-R1/V3
3. gemini-2.5 series
4. qwen2.5 series
5. In the future, more LLM large models and AIGC multimodal large models will be able to serve as the core large models for AI agents.


<h2 id="9. What are the functions of the system prompts in AI Agent?">9. What are the functions of the system prompts in AI Agent?</h2>

In the AI ​​Agent architecture, the **System Prompt** is the core control center of the AI ​​Agent, and its design quality directly determines the Agent's reliability, security, and execution performance.

### The Four Core Functions of System Prompt Keywords
#### 1. **Role Definition and Personality Modeling**
   ```python
   # Example of a Legal Counsel Agent
   """
   Position: Senior Partner at Global Law Firm (15 years of practice)
   Areas of expertise: cross-border mergers and acquisitions, intellectual property litigation
   Language style: Rigorous and professional; citations of legal provisions must be properly attributed.
   """
   ```
   - **Effect**:  
     - By restricting the model's tendency to play freely, the rate of hallucinations decreased by 40%.  
     - Build user trust in the agent's professionalism

#### 2. **Capability Boundary Locking**
   ```python
   # Tool access whitelist
   """
   Available tools:
     - contract_review: Contract review (input PDF → output risk report)
     - clause_search: Clause database search (keywords → similar cases)
   Prohibited behavior:
     - Generate a legally valid commitment
     - Explanation of the draft that has not yet come into effect
   """
   ```
   - **Safety Value**:  
     - Avoid unauthorized operations (such as medical agents blocking diagnosis).  
     - Complies with GDPR/Cyberspace Administration of China regulatory requirements

#### 3. **Cognitive Framework Implantation**
   | **Task Type** | **Preset Mindset** |
   |--------------|--------------------------------|
   | Contract Review | Entity Verification → Rights and Responsibilities Analysis → Breach of Contract Clause Assessment |
   | Legal Consultation | Fact Extraction → Legal Provision Matching → Solution Generation |
   - **Performance Improvement**:  
     - 3x faster processing speed for complex tasks  
     - Results are 92% predictable.

#### 4. **Dynamic Context Management**
   ```python
   """
   Memory rules:
     - Retain core entities (company name/amount/time point)
     - Discard emotional expressions (such as user complaints).
     - Persistence critical date (contract expiration date)
   """
   ```
   - **Technological Innovation**:  
     - Achieve 10x information density in a 4K context window


<h2 id="10. How to build powerful system prompts in AI Agent?">10. How to build powerful system prompts in AI Agent?</h2>

Currently, mainstream AI Agent systems need to follow eight key design and construction principles for their prompts:

1. Clear Goals, Roles, and Scope: Clearly defining the AI ​​Agent's identity, core functions, and operational domain effectively anchors its behavioral patterns, sets user expectations, and prevents uncontrolled expansion of its functional scope or the generation of meaningless feedback. This is equivalent to establishing an identity and boundaries of responsibility for the AI ​​Agent.
2. Structured instruction and task decomposition: The structured use of headings, lists, code blocks, or custom tags helps maintainers of the AI ​​Agent to understand clearly and also assists the AI ​​Agent in more accurately parsing and distinguishing the priority of different rules or information sets, reducing ambiguity.
3. Clearly define tool integration and usage guidelines: For the behavior of the AI ​​Agent, it's necessary to clearly describe to the AI ​​Agent what they are, what they do, how to invoke them (syntax, parameters), the required format (e.g., XML, JSON), and, crucially, when not to use them. This requires detailed descriptions, clear patterns, and explicit rules.
4. Step-by-step reasoning and planning: Complex tasks need to be broken down. The AI ​​agent needs to be guided to think systematically, plan actions, and execute iteratively. Before moving to the next task, it should wait for user feedback or results to reduce errors and improve consistency.
5. Environment and Context: The AI ​​Agent runs in various specific environments (such as operating systems, integrated development environments, browser sandboxes, and specific libraries). Providing this contextual information allows the AI ​​Agent to generate compatible code, use appropriate commands, and understand the limitations of the environment.
6. Domain-Specific Expertise and Constraints: The AI ​​Agent needs to be informed of the specific domain it needs to handle (e.g., web development, data analysis). Domain-specific expertise, best practices, style guidelines, and constraints should be included in the prompts to ensure the output is both high-quality and context-appropriate.
7. Safety, Alignment, and Rejection Protocols: A responsible AI agent needs clear boundaries. Cue words need to define negative requests and specify how the AI ​​agent should reject such requests. It's also important to ensure that things are done correctly and safely.
8. Establish tone and interaction style: Establishing a consistent persona (e.g., a friendly expert, a witty assistant, a straightforward engineer) creates a more predictable and engaging user experience. In practice, this can range from broad guidelines to very specific stylistic instructions.


<h2 id="11. How does System Prompt work internally within the AI ​​Agent?">11. How does System Prompt work internally within the AI ​​Agent?</h2>

In the mainstream AI Agent framework design, three core message types are defined: System Prompt (System Message), Assistant Prompt (Assistant Message), and User Prompt (User Message), with clearly distinguishable functions among them.

1. **User Prompt**: Represents the question directly entered by the user.
2. **Assistant Prompt**: Represents the response content generated by the large model.
3. **System Prompt**: Used to set core configurations for large models, such as roles, basic commands (e.g., identity definition, security constraints).

So, how does **System Prompt work in the AI ​​Agent**?

In AI Agents, System Prompt primarily serves as a silent prompt, typically placed before user input, and combined with Assistant Prompt and User Prompt for input into the larger model.

The key difference between System Prompt and User Prompt lies in their position and priority: System Prompt is always placed at the beginning of the input text sequence. Due to the nature of attention mechanisms (information at the beginning and end of a sequence is usually given more attention), content at this position is more easily recognized and followed by the model. Therefore, a complete multi-turn dialogue prompt is typically constructed using the following pattern:

```python
System Prompt -> User Prompt -> Assistant Prompt -> User Prompt ... -> Assistant Prompt
```

In this structure, the main role of Assistant Prompt is to show the large model the historical dialogue record and clearly label which parts of it originated from user input. The large model, pre-trained and fine-tuned with data using this structure, can understand that these are not immediate user inputs, but rather dialogue history. This helps the large model better grasp contextual information, thus responding more accurately to subsequent questions.

So, some readers might ask, why not merge System Prompt and User Prompt? A key consideration is security and controllability. Differentiating message types during the fine-tuning phase helps defend against attacks such as prompt injection. Specifically:

1. Place the core role definitions and rules in the System Prompt.
2. User interaction content is placed in User Prompt.

This separation mechanism effectively prevents certain simple prompt attacks or information leakage risks. Especially in practical applications, the System Prompt is usually invisible to the user. Its defined rules and roles are fully trained and therefore enjoy the highest priority in the model. This significantly increases the likelihood that the large model will follow the developer's intent and reduces the risk of output deviating from expectations due to changes in user input.

Of course, relying solely on the System Prompt cannot completely defend against attacks (for example, there have been cases of System Prompt being leaked through manipulation in GPT-4). Therefore, performing secondary validation on user input or model output is a more robust security enhancement solution.

Next, Rocky will give a detailed example to help everyone understand more clearly how the three Prompts are combined with the user question and used as context input to the large model:

![Concatenation of System prompt, Assistant Prompt, and User Prompt](imgs/System-prompt, Assistant-Prompt, User-Prompt concatenation.png)


<h2 id="12. What's the difference between AI-Search and regular Search?"">12. What's the difference between AI-Search and regular Search?</h2>

The core difference between AI-Search (intelligent search) and traditional search (such as keyword search) lies in **whether it possesses semantic understanding, dynamic decision-making, and proactive reasoning capabilities**. The following is an in-depth comparative analysis:

---

### **I. Essential Differences**
| **Dimensions** | **Traditional Search** | **AI-Search (Intelligent Search)** |
|------------------|----------------------------------------|----------------------------------------|
| **Technical Foundations** | Keyword Matching + Inverted Index | Large Language Model (LLM) + Knowledge Graph + Reinforcement Learning |
| **Interaction Methods** | User inputs explicit keywords → Returns matching results | Natural language question → Understands intent → Dynamically infers answer |
| **Output Format** | Link list (requires secondary user filtering) | Structured answer + multimodal results + source tracing evidence |
| **Objective** | Quickly retrieve existing information | **Solve problem** (or even perform actions) |

---

### **II. Differences in Core Competencies**
#### 1. **Semantic Understanding vs. Character Matching**
- **Traditional Search**  
  - Relies on the TF-IDF/BM25 algorithm to match the frequency of keyword occurrences.  
  - Example: Search *“Apple phone overheating”* → Returns web pages containing “Apple”, “phone”, and “overheating”.  
- **AI-Search**  
  - Understand the context and implicit needs (e.g., "apple" refers to the brand rather than the fruit).  
  - Example: Question *“What should I do if my phone gets hot while playing games?”* → Analyze possible causes (CPU overload/insufficient heat dissipation) and provide solutions.

#### 2. **Static Search vs. Dynamic Reasoning**
- **Traditional Search**  
  - It only aggregates existing content and cannot combine information.  
  - Limitations: Unable to answer *"Comparison of the representative works of the 2025 Nobel Prize in Literature laureates with Mo Yan's style"* (requires real-time data + literary analysis).  
- **AI-Search**  
  - **Chain of Reasoning (CoT) Technology**: Decompose the problem → Retrieve evidence → Logically synthesize the answer.  
  - Dynamic tool invocation: Search for Nobel Prize results online → Extract features of works → Invoke style analysis model.

#### 3. **One-way response vs. task execution**
- **Traditional Search**  
  - The ultimate goal is to provide information (such as displaying airfare prices).  
- **AI-Search**  
  - **Agent Mode**:  
    - Understand *“Book the cheapest flight from Beijing to Shanghai next Monday”* → Automatic price comparison → Fill in the order → Payment (authorization required).  
  - To achieve "search as a service".

---

### **III. Technology Stack Comparison**
| **Hierarchy** | Traditional Search | AI-Search |
|------------------|----------------------------------|------------------------------------|
| **Index Layer** | Inverted Index + PageRank | Vector Database (Similarity Semantic Embedding) |
| **Understanding Layer** | Stemming + Synonym Expansion | LLM Fine-Tuning (LoRA/P-Tuning) + Knowledge Graph |
| **Execution Layer** | None | Tool Calling (Python/API/Plugin) |
| **Optimization Mechanism** | Click-through Rate (CTR) Ranking | RAG + Reinforcement Learning (PPO/DAPO) Feedback Optimization |

> 💡 **Key Innovation**: AI-Search solves the illusion problem by injecting external knowledge into LLM through **RAG (Retrieval Enhanced Generation)**.

---

### **IV. Performance and Limitations**
| **Metrics** | Traditional Search | AI-Search |
|------------------|----------------------------------|------------------------------------|
| **Response Speed** | ⭐⭐⭐⭐⭐ (Milliseconds) | ⭐⭐ (Seconds, requires inference) |
| **Complex Problem Solving** | ⭐ (Basic Retrieval Only) | ⭐⭐⭐⭐⭐ (Cross-Domain Reasoning) |
| **Data Real-Time Performance** | ⭐⭐⭐ (Depends on crawler frequency) | ⭐⭐⭐⭐ (Can be searched online) |
| **Result Interpretability** | ⭐⭐⭐ (Clear Source) | ⭐⭐ (Black-box reasoning requires tracing its source) |

**Current Challenges of AI-Search:**  
- Real-time bottleneck (high inference latency)  
- Error propagation in complex tasks (such as errors in automatic coding).  
- Insufficient stability of multi-hop inference (requires manual verification)

<h2 id="13. What is DeepSearch?"">13. What is DeepSearch?</h2>

DeepSearch's core idea is to iterate through three stages—searching, reading, and reasoning—until the optimal answer is found. The searching stage uses search engines to explore the internet, while the reading stage focuses on detailed analysis of specific web pages (e.g., using Jina Reader). The reasoning stage assesses the current state and decides whether to break the original problem down into smaller sub-problems or try different search strategies.

Unlike the RAG system in 2024, which typically runs a search-generate process only once, DeepSearch performs multiple iterations and requires explicit stopping conditions. These conditions could be based on token usage limits or the number of failed attempts.


## Principle: From Static Retrieval to Dynamic Reasoning
**The fundamental difference from traditional search/RAG**
| **Dimensions** | Traditional Search/RAG | DeepSearch | Advantages Analysis |
|------------------|---------------------------|--------------------------------|------------------------------|
| **Trigger Mechanism** | Single search after user input of keywords | AI proactively identifies knowledge gaps and dynamically initiates multiple rounds of searches | Solves the problem of information fragmentation in complex problems |
| **Deep Reasoning** | No Contextual Reasoning Ability | Iterative Reasoning Based on New Information After Each Round of Retrieval | Implements Multi-hop Reasoning |
| **Content Integration** | Directly return to the original document fragment | Periodically refine information (Reason-in-Documents) | Avoid model failure caused by excessively long context |
| **Respond to Objectives** | Quickly return to the link list | Generate accurate conclusions or structured reports | Reduce users' secondary processing costs |

From another perspective, DeepSearch can be viewed as an LLM agent equipped with various web tools (such as search engines and web readers). This agent analyzes current observations and past operation records to determine the next course of action: whether to directly provide an answer or continue exploring the web. This constructs a state machine architecture, where the LLM controls the transitions between states. At each decision point, you have two options: you can carefully design prompts to have a standard generative model generate specific action instructions; or you can use a specialized inference model like Deepseek-r1 to naturally deduce the next action. However, even when using r1, you need to periodically interrupt its generation process, inject the tool's output (such as search results or web page content) into the context, and prompt it to continue the inference process.

Ultimately, these are all just implementation details. Whether you carefully design your prompts or use a reasoning model directly, they all follow DeepSearch's core design principle: a continuous cycle of searching, reading, and reasoning.


<h2 id="14. What is the difference between AI Agent and AI Workflow?"">14. What is the difference between AI Agent and AI Workflow?</h2>

Rocky believes that AI Agent is an evolution of AI Workflow, and both AI Agent and AI Workflow can be broadly referred to as Agent.

The AI ​​Workflow's operation process is predefined and designed, while the AI ​​Agent can make autonomous decisions during runtime.

![Difference between Agent and Workflow](imgs/Agent and Workflow Difference.png)

In the AIGC era, the concept of AI Agent is very popular. When we determine which category a system belongs to, we mainly look at whether it can make dynamic decisions during operation, rather than how long the prompt words such as System Prompt are.

| **Dimensions** | AI Agent | AI Workflow |
|------------------|---------------------------|--------------------------------|
| **Essence** | Intelligent entities with autonomous decision-making capabilities | Automated task processes with pre-defined steps |
| **Analogy** | Thoughtful "employees" | Factory "assembly line" |
| **Decision-making timeline** | Design phase | Operation phase |
| **Decision-making power** | Autonomous decision-making | Execution according to preset rules |
| **Reproducibility** | Stable and reproducible | Requires real-time recording of action logs |
Operating costs can be accurately estimated, but are subject to fluctuations.

However, this does not mean that AI Agent will always be better than AI Workflow. We still need to choose the appropriate AIGC algorithm solution based on the actual application scenario.

In general, many B2B scenarios have clear requirements and demand stability and controllability. In these cases, AI Agents that make autonomous decisions are not necessarily better than AI Workflows in terms of controllability.

However, AI Workflow can only execute on pre-defined and fixed tasks, while AI Agent can perform creative execution on more open and uncertain tasks.

With the continued development of the AIGC era, AI Agent systems are more likely to adopt a hybrid architecture of Agent + Workflow. The AI ​​Agent is the "thinker" that solves the question of what to do (What); while the AI ​​Workflow is the "executor" that solves the question of how to do it (How).  

Therefore, there is no distinction between the two. Black cat or white cat, as long as it catches mice in the appropriate situation, it is a good cat.


<h2 id="15. In AI Agents, how do function calls transform external tools into a way that large models can understand?">15. In AI Agents, how do function calls transform external tools into a way that large models can understand?</h2>

**The core mechanism for transforming external tools into a way that is understandable to large models: Standardized interface descriptions and seamless execution logic.**

The core of enabling large LLM/AIGC models to understand and call external tools, plugins, or APIs lies in **establishing a standardized interface description mechanism** and building a reliable execution bridge. This process involves two key steps:

1. **Standardized Interface Description:**
    * **Define a Structured Description (Schema):** Design a structured interface definition for each tool that conforms to a specific calling format (commonly such as JSON/XML Schema). This schema must clearly contain the following elements:
        * **Unique Name:** Used to accurately identify the external tools that need to be invoked.
        * **Functional Description:** Use natural, accurate, and unambiguous language to detail the tool's core function, required input parameters, expected output, and applicable scenarios. This is crucial for the larger model to understand the external tool's functionality and match user intent. Avoid using overly technical or vague terminology.
        * **Parameter Specification:** Clearly lists every parameter required for the tool to run, including the parameter name, data type, whether it is mandatory (required), and a detailed explanation of the parameter's meaning.

2. **Execution Bridging:**
    * **Providing Tool Directory to LLM Model:** During each model interaction, standardized descriptions of all currently available tools are integrated as contextual information and passed to the large model as a specific part of the prompt message.
    * **Parsing Model Output:** The application continuously listens for the model's output responses. Once a function call conforming to a predefined format (such as a specific JSON/XML structure) is detected, it is immediately parsed.
    * **Locate and execute the target tool (Invoking the Actual Tool):** Based on the parsed tool identifier (Name), locate the corresponding external tool/plugin/API implementation.
    * **Parameter Mapping & Validation:** Extracts parameter values ​​from the argument list of the calling command, performs necessary type conversions and validity checks, and **finally calls the actual tool's interface.**
    * **Result Handling:** Captures the results returned after the tool is executed (whether it's a success response or an error message).
    **Feeding Back Results to Model:** The results of the tool's execution are formatted as text information and then input back into the larger model. This allows the larger model to generate subsequent responses or determine the next steps (such as calling other tools) based on this information.

**Essential Summary:** The core of this mechanism is to create a clear and easy-to-understand "natural language instruction manual" (i.e., schema/description) for each external tool, enabling the model to understand its functionality. Simultaneously, a "translation and execution layer" is established, responsible for translating the "operation instructions" (JSON/XML calls) generated by the large model based on the instruction manual into specific calls to the actual tools, and translating the tool's "operation result reports" back into information that the large model can process.

**Note:** The core function of MCP (Model Control Plane) is to achieve the connection between the **standardized interface** description and execution logic mentioned above.


<h2 id="16. How do large models learn function-calling capabilities in AI agents?">16. How do large models learn function-calling capabilities in AI agents?</h2>

Function calling capability is not a native feature of large LLM/AIGC models. How can we enable large LLM/AIGC models to learn function calling capability?

The current mainstream approach in the AI ​​industry is to enable large LLM/AIGC models to learn function calling capabilities through supervised fine-tuning (SFT), rather than training them from scratch during the pre-training phase. Large AI models with function calling capabilities currently include DeepSeek, GPT-4o, Claude, Qwen, and Gemini.

Meanwhile, before fine-tuning the training, the LLM/AIGC basic large model needs to have good instruction compliance and code/structured data generation capabilities.

The core idea of ​​fine-tuning training for Function Calling ability:
1. Ability to acquire intent recognition: Understanding whether a user's request requires the use of external tools/functions to complete, rather than directly generating a text response.
2. Argument Extraction & Formatting Capabilities: If a function needs to be called, the required parameters can be correctly extracted from the user request and the function call instructions can be generated according to a predefined format (JSON, XML, etc.).

Next, let's review the fine-tuning process of Function Calling:

1. Dataset Creation: Dataset preparation is arguably the most crucial step in the entire fine-tuning process. We need to build a fine-tuning dataset containing function calling scenarios, allowing the base model to fully learn its parameters and formatting. Each data sample typically includes the following:

**User Input/Query**: A user request, which may or may not include a function call. For example: "How much has Tencent stock risen or fallen today?" or "Write me a magnificent poem."
**Available Functions/Tools Description:** A structured description that informs the large model what functions are currently available, the purpose of each function, its required parameters and their types, and a description. This description is usually text and needs to be in a clear format (JSON, XML, etc.).
**Desired Output**: (1) If a function needs to be called: A string in a specific format, typically a JSON or XML object containing the function name and extracted parameters. (2) If a function does not need to be called: The large model directly generates a text response. For example: "Okay, I wrote a magnificent poem:..."
**Overall Dataset Quality Requirements**: (1) Data Diversity: Sufficient high-quality data covering various scenarios (needing/not needing to call a Function, calling different Functions, Function parameter changes, ambiguous expressions, etc.) is required. (2) Clarity of Function Description: The quality of the function description directly affects whether the model can correctly understand and use the function. (3) Negative Samples: Sufficient samples that clearly do not require calling a Function are required to prevent the model from "over-triggering" Function calls.

Below is an example of the structured format for Function parameters:
```python
{
  "name": "get_stock_change",
  "arguments": {
    "stock_name": "Tencent Stock",
  }
}
```

Below is a sample dataset format:

```python
{
    "conversations": [
        {
            "from": "human",
            "value": "Could you please check today's stock price changes?"
        },
        {
            "from": "gpt",
            "value": "Of course, I can help. Which stock are you interested in?"
        },
        {
            "from": "human",
            "value": "Tencent stock"
        },
        {
            "from": "gpt",
            "value": "{\n\"function\": \"get_stock_change\",\n\"arguments\": {\n\"stock_name\": \"Tencent Stock\"\n}\n}"
        }
    ]
}
```

2. Select a base model: Choose a pre-trained LLM/AIGC large model with strong instruction following capabilities (such as DeepSeek).

3. Formatting Training Data: Combine each data sample into a format that the large model can understand. Typically, this involves concatenating the "user input" and "description of available functions/tools" from the dataset as the model's input (Prompt), and the "expected output" (whether JSON, XML function calls, or text responses) as the target output (Completion/Target/Label). Specific delimiters or templates are needed to distinguish between the different parts.

4. Fine-tuning Training: Fine-tune the training on a specific dataset using standard SFT methods (full parameter fine-tuning or training LoRA). The optimization objective of the large model is to minimize the difference between the predicted output and the expected output (e.g., using cross-entropy loss). By learning from these samples, the large model learns to decide whether to directly answer or generate a function call in a specific format (JSON, XML) based on user input and available function descriptions.

After the above fine-tuning training process, we can obtain a large LLM/AIGC model with Function Calling capabilities.


<h2 id="17. What are the limitations of current AI agents?">17. What are the limitations of current AI agents?</h2>

1. Hallucination problem in AI Agents: The core LLM/AIGC large model in AI Agents may generate inaccurate information.
2. Context length and planning deficiencies: The limited context window of large LLM/AIGC models makes it difficult for AI agents to handle long-term task planning and self-reflection.
3. Immature multimodal processing capabilities: Whether in B2B or B2C scenarios, many needs require processing heterogeneous data such as images, text, video, and audio, but most AI agents still mainly use text as the single modality.
4. Difficulty in Industry Adaptation: Enterprise-level scenarios require "zero errors," but general-purpose AI agents, while having high fault tolerance, are insufficient to meet the needs of high-risk fields such as healthcare and finance. Vertical industries have complex business logic, requiring deep integration of data and processes.
5. Computational costs remain high: The reasoning process of the AI ​​Agent still consumes a lot of computing resources.


<h2 id="18. What are the mainstream evaluation metrics for current AI agents?">18. What are the mainstream evaluation metrics for current AI agents?</h2>

1. Task Completion Rate: Hierarchical task completion rate, process trajectory accuracy, long-term strategy stability, etc.
2. Tool Usage Accuracy
3. Reasoning Quality
4. User Satisfaction


<h2 id="19. How does an AI agent possess long-term memory capabilities?">19. How does an AI agent possess long-term memory capabilities?</h2>

To enable AI agents to have long-term memory capabilities, it is necessary to address the inherent "context window limitations" and "statelessness defects" of large LLM/AIGC models.

AI agents with long-term memory need to adopt a "hierarchical storage + intelligent retrieval" architecture, the core of which is to break the context window limitation through **vectorization, summary compression, and hybrid databases**.

### 🔧 I. Architecture Design of Long-Term Memory
1. **Hierarchical Memory System**  
   The AI ​​Agent's memory needs to simulate the structure of the human brain, and it works in three layers:  
   - **Short Memory (STM):** Maintains the coherence of the current conversation through a context window (such as the token limit of a Transformer), but has a limited capacity (typically 4K-128K tokens).  
   - **Midterm Memory (MTM)**: Compresses key dialogue information into summaries or embedded vectors, stores them in vector databases (such as FAISS, Pinecone), and supports semantic retrieval.  
   - **Long-Term Memory (LTM):** Persistently stores structured data such as user profiles and behavioral habits, using SQL/NoSQL databases or knowledge graphs to achieve cross-session memory.

2. **Hybrid Storage Engine**  
   - **Vector Database**: Handles similarity searches for unstructured text (such as user preferences for "likes science fiction movies").  
   - **Time-series database**: Records event chains (such as "the user inquired about airfare prices last week").  
   - **Graph Databases**: Construct knowledge-related networks (e.g., "User A is a programmer → may be interested in algorithm updates").

### ⚙️ II. Key Implementation Technologies
1. **Memory Generation and Compression**  
   - **Summarization**:  
     After each dialogue, a summary is generated using a dedicated LLM (e.g., a dual LLM architecture that separates the dialogue and summary models).  
   - **Embedding**:  
     Text can be converted into vectors using BERT or OpenAI Embeddings for efficient retrieval.

2. **Memory Retrieval and Update**  
   - **Multimodal retrieval**: Combining semantic search (vector similarity) + time filtering (prioritizing recent events) + rule-based filtering (such as importance scoring).  
   - **Conflict Resolution**: When old and new memories conflict (such as changes in user tastes), the LLM makes the decision or sets a decay weight.

3. **Memory Integration into the Agent**  
   Dynamically inject the search results into the Prompt:  
   ```python
   # Mem0 API Example: Adding and Searching Memories
   m.add(user_query, user_id="Alice") # Store memory
   related_memories = m.search("Recommended Movies", user_id="Alice") # Search related memories
   prompt = f"User's historical preferences: {related_memories}. Current query: {new_query}"
   response = llm.generate(prompt)
   ```


<h2 id="20. Introducing the Principle and Function of the Memory Mechanism in AI Agents">20. Introducing the Principle and Function of the Memory Mechanism in AI Agents</h2>

### I. Why Do We Need Memory? — Starting with the "Goldfish Brain"

Imagine you have a chat assistant based on a large language model (like a typical ChatGPT). You have a conversation with it:

**You:** My name is Xiaoming, and I like playing basketball.
**AI: Hello Xiaoming! Playing basketball is a great sport.**
**You:** My best friend is named Xiao Wang.
* **AI**: Xiao Wang sounds like a good friend.
**You:** So what do Xiao Wang and I usually do together on weekends?

At this point, the AI ​​will most likely get stuck, or give you a vague, guessed answer (such as "maybe go out and play together"). This is because it's like a goldfish with only a 7-second memory; it doesn't remember **you said you liked playing basketball**, let alone **Xiao Wang is your good friend**.

The core problem is that standard LLMs are "stateless." In each conversation, it generates a response based solely on the prompts you currently input; once the conversation ends, this contextual information is lost.

A true AI agent needs to perform complex, multi-step tasks (such as planning your entire travel itinerary, handling a complete customer complaint as a customer service representative, or interacting with you as a game character over a long period). If it has no memory, each step is like starting from scratch, which is undoubtedly inefficient and foolish.

Therefore, **the memory mechanism is designed to enable AI agents to continuously learn, accumulate experience, and make decisions based on complete context.**

### II. The "Principles" of the Memory Mechanism: How Does It Work?

The AI ​​agent's memory system is very similar to our human brain, and can be divided into several key parts:

#### 1. Types of memory (like different functional areas of the brain)

* **Short-term memory**
    **What it is:** It's equivalent to the agent's "workbench" or "currently active area of ​​the brain." It stores the most recent information directly related to the current task.
    * **Technical Implementation**: This typically involves **dialogue context**. When you chat with the Agent, the N sentences you've spoken previously (such as the last 10 rounds of conversation) are sent to the model as cue words, letting it know "what we just talked about".
    **Example:** When planning a trip, you say "I want to go to Tokyo," and then ask "What are some recommended attractions?" Short-term memory allows the AI ​​to know that "Tokyo" is the destination.

* **Long-term memory**
    **What it is:** Essentially an agent's "personal diary" or "knowledge base." It stores important information that needs to be retained long-term, such as your personal preferences, experiences learned from past tasks, and facts about the world.
    * **Technical Implementation:** An **external vector database**. This is the core of the memory system.
        * **Step 1: Encoding**: When AI deems a piece of information important (such as "User Xiaoming likes to play basketball"), it will use a model to convert this text into a string of numbers (called a "vector" or "embedding").
        **Step 2: Storage**: Store this string of numbers along with the corresponding original text into the database.
        * **Step 3: Retrieval**: When memory is needed (for example, when the user mentions "friend"), the AI ​​will also convert the current question into a vector, and then search the database for the **semantically most relevant** vector fragment.
    * **Example**: Even after a long time, if you log back in and tell the Agent, "Help me choose a suitable birthday gift," it can retrieve information from its long-term memory, such as "likes playing basketball," and recommend basketball shoes or NBA tickets.

#### 2. The Flow of Memory: A Complete Closed Loop

An AI agent equipped with a memory mechanism works as follows:

The cycle of **perception -> thinking -> action -> memory**.

1. **Perception**: The agent receives new information (such as the user inputting "What do Xiao Wang and I usually do together on weekends?").
2. **Search:** The agent automatically searches for relevant memories in the **long-term memory bank** (searching for keywords such as "Xiao Wang", "me", and "together", finding two records: "Xiao Wang is a good friend" and "I like playing basketball").
3. **Thinking**: The agent combines the new input, the retrieved long-term memory, and the current short-term memory into a rich set of prompts, which is then fed into the large language model for reasoning.
4. **Action:** The large language model generates the answer based on the complete context: "You and your good friend Xiao Wang often play basketball together on weekends."
5. **Memory:** The agent decides whether to store valuable information from this interaction (such as "Xiaoming and Xiaowang often play basketball on weekends") in **long-term memory** for future use. Simultaneously, this dialogue itself enters the context window of **short-term memory**.

### III. The “Function” of the Memory Mechanism: What Does It Bring?

The memory mechanism fundamentally raises the ceiling of AI agent capabilities, enabling it to evolve from a "tool" to a "partner".

1. **Achieving Continuity and Personalization**
    **Function:** Enables the agent to remember the user's identity, preferences, habits, and historical interactions. You don't need to repeat yourself in every conversation.
    * **Example:** A fitness coach agent might remember that you mentioned a knee injury last time, thus avoiding recommending squat-type exercises.

2. **Accumulation and Learning Ability**
    **Function:** Agents can learn from past successes and failures. They can store solved problems and methods in memory, and directly invoke them when encountering similar situations again, improving efficiency.
    **Example:** After a programming agent helps you solve a specific bug, it can store the solution in its memory. When another user encounters a similar bug, it can quickly provide a solution.

3. **Maintaining State and Context**
    **Function:** In complex, multi-step tasks (such as games and software development), the memory mechanism helps the agent maintain the task's state, knowing "which steps I have completed" and "what the next step should be."
    * **Example:** In a game, an NPC agent remembers whether you have helped it, and thus decides whether to be friendly or hostile towards you.

4. **Supports complex reasoning and planning**
    **Function:** Only with rich background knowledge (memory) can one perform deep, context-based reasoning and long-term planning.
    * **Example:** A research assistant agent can remember the core ideas of all the literature you have read before and organically integrate them when writing new chapters.

### IV. A vivid analogy: The librarian

You can think of the AI ​​agent's memory mechanism as a **super librarian**:

* **Large Language Model:** This refers to the administrator's own knowledge and eloquence. He is intelligent and capable of impromptu speaking.
* **Short-term memory**: It's the books he's currently reading. The content is limited, but readily available.
* **Long-term memory**: This is like the entire **vast library collection**. The content is vast, but it takes time to find what you're looking for.
* **Search Function:** This is a **highly efficient book retrieval system** controlled by the administrator. When answering a complex question, the administrator first uses their verbal skills (LLM), combined with readily available books (short-term memory), and simultaneously uses the retrieval system (search) to find the most relevant books in the library (long-term memory) to corroborate their answer, ultimately providing a perfect response.

### Summarize

**The memory mechanism is the "soul archive" of an AI agent, transforming the one-off, isolated intelligence of a large language model into continuous, evolving, context-aware intelligence.** Without memory, AI is merely an "encyclopedia" that answers every question; with memory, AI can become a truly understanding, accompanying, and complex "intelligent assistant" that helps you.

Currently, frameworks such as GPT-4 with Memory and LangChain/LlamaIndex are actively developing and improving this memory system, which is the core foundation for building the next generation of truly practical AI applications.


<h2 id="21. Introduction to the Principles of Context Engineering in AI Agents">21. Introduction to the Principles of Context Engineering in AI Agents</h2>

### I. What is context engineering?

In simple terms, **context engineering** refers to a set of methods, strategies, and techniques for carefully designing, organizing, and managing the information (i.e., "context" or "background") that an AI agent can access, enabling it to complete tasks more accurately, coherently, and efficiently.

We can think of it as preparing a perfect "work memo" for a very intelligent assistant who suffers from "short-term amnesia." This memo contains:
What does it need to do? (Task instructions)
* **What it did before** (historical dialogue and actions)
* **What does it know?** (Related knowledge base)
* **What can it use?** (List of available tools)
What should it pay attention to? (Code of conduct and constraints)

Context engineering is the science and art of how to write, update, and maintain this "memorandum".

### II. Why is context so important? — The core of the principle

To understand its principles, one must first understand how large language models work: **it is a context-based autoregressive prediction model**.

1. **Statelessness:** LLMs are inherently "stateless." They function like an extremely erudite "transient reactor," with each invocation independent of the others. You give it input text, it predicts the next most likely word/token based on that text, and so on. It **has no** built-in memory to remember what you said to it last time.
2. **The context window is the only "working memory":** All the information the model can "see" and process is the **context** carried by the current request. This context is its entire world, its entire working memory. **All the model's reasoning, decisions, and responses are entirely based on this context you provide.**

Therefore, the **fundamental principle** of context engineering is to **guide and constrain the model's **output behavior** by carefully controlling the model's **input information**, thereby simulating intelligent, coherent, and stateful agent behavior.

### III. Key Components of the Context

A high-quality context designed for an AI agent typically includes the following core components, which are also the modules that context engineering needs to carefully construct:

1. **System Prompt/Character Settings**
    * **Content**: Define the Agent's "persona", core responsibilities, goals, and behavioral norms.
    **Function:** To establish a stable "mental model" for the Agent at the start of a task, telling it "who you are," "what you should do," and "how you should behave."
    * **Example:** "You are a professional customer support assistant focused on resolving software installation issues. Your answers should be friendly, professional, and easy to understand. Please do not make promises to users that you cannot keep."

2. **Task Instructions and Objectives**
    **Content:** Clearly and specifically describe the task that needs to be completed.
    **Purpose:** To provide a clear direction for this interaction.
    * **Example**: "Please help user Zhang San reset his account password. His username is 'zhangsan@email.com'."

3. **History of Dialogue and Action**
    * **Content**: Records the complete history of multi-round conversations between the user and the agent, as well as the content and results of the agent's previous tool calls/actions.
    **Purpose:** To provide **coherence**. This allows the agent to reference previously stated statements, understand user referencing (e.g., "the method mentioned above"), and avoid redundant operations.
    **Principle:** This is key to simulating "memory" and "state." There is no history; each problem is entirely new to the agent.

4. **External Knowledge and Documentation**
    * **Content**: Information relevant to the current task, obtained from vector databases, knowledge bases, or networks through techniques such as retrieval-enhanced generation.
    * **Function**: To compensate for the lack of **timeliness** and **property** of LLM knowledge, and to provide factual basis for decision-making.
    * **Example**: When answering questions about the company's latest policies, include specific excerpts from policy documents in the context.

5. **Tools and Function Definitions**
    * **Content**: A list of external tools (such as APIs and functions) that the Agent can call, including their names, descriptions, parameter formats, etc.
    * **Function**: Extends the Agent's **action capabilities**, enabling it to go beyond text generation and perform specific operations (such as querying databases, sending emails, and performing calculations).
    * **Principle**: By providing tool descriptions, the model is guided to select and structurally invoke the correct tools when encountering specific situations (such as when real-time data is needed).

6. **Structured Output Requirements**
    * **Content:** The model is required to output its thought process or final answer in a specific format (such as JSON or XML).
    **Function:** Facilitates backend programs in parsing the model's output, enabling automated processes. This is crucial for the Agent's "think-act" cycle.
    **Example:** "Please output your thought process and final answer in the following JSON format: {'steps': [...], 'final_answer': '...'}"

### IV. Core Principles and Strategies of Context Engineering

#### Principle 1: Hierarchy and Priority

Context windows are a limited and valuable resource (e.g., 128K tokens). They must be used efficiently.

* **Strategy**:
    **System prompts take precedence and are stable:** System prompts are usually placed at the beginning and are kept as stable as possible throughout the session; they are the “cornerstone” of the agent.
    **Relevance Filtering:** Not all historical records and external knowledge are equally important. Using a **retrieval tool**, the most relevant fragments are dynamically extracted from massive amounts of information and placed into the context based on the current question. This is the core of RAG (Relevance Analysis).
    * **History Summary/Compression**: When conversations are long, compress distant conversation history into a concise summary instead of retaining all the original text, saving space. For example: "The user previously encountered login issues and was guided to clear their browser cache."

#### Principle 2: Thought Process Chain and Reasoning Framework

To enable an agent to complete complex tasks, it needs to be guided to reason step by step.

* **Strategy**:
    * **Provide a "thinking template" in context**: Explicitly instruct the Agent to work according to the "think-act-observe" steps in system prompts.
        * **Thinking**: Analyze the current situation and decide what to do next.
        **Action:** Call the tool or generate an answer.
        * **Observation**: Record the results of actions.
    * **Example** (ReAct mode):
        ```
        Thoughts: Users need to know the weather in Beijing to decide whether to bring an umbrella. I know the current date, but not the real-time weather. I need to call a weather query tool.
        Action: Invoke the tool [get_weather(city="Beijing")]
        Observation: Tool returned the following result: Beijing, sunny, temperature 25°C.
        Thinking: According to the weather information, it's sunny in Beijing, so there's no need to bring an umbrella. I can tell this information to the user.
        Answer: It's a sunny day in Beijing today, with a temperature of 25°C. You don't need to bring an umbrella!
        ```
    * By incorporating this structured thinking process into the context (often the model's output), we force the model to engage in deeper, more logical reasoning, rather than simply providing a final answer.

#### Principle 3: Dynamic Management and State Maintenance

Due to the limitations of the context window and the long-term nature of the task, the context must be dynamically changing.

* **Strategy**:
    * **Sliding window:** Only retains the most recent N rounds of dialogue, discarding the oldest. Simple, but may lose crucial long-term information.
    * **Smart Summary**: As mentioned above, past interactions are periodically summarized by an agent or a separate process, with summaries rather than full text placed in the context.
    **Vectorized Long-Term Memory:** This method stores important user information, task status, etc., in an external database (vector database or traditional database). When needed, it retrieves these details from the context. This achieves the separation of "long-term memory" and "working memory."

### V. A Complete Technical Process Example

Suppose an **e-commerce customer service agent** handles user complaints:

1. **Initial Context Construction**:
    **System Prompt:** "You are a customer service agent for XX e-commerce platform, responsible for handling orders and complaints. A patient and professional attitude is required. You have the right to inquire about orders, initiate refunds, and contact logistics companies."
    * **Tool Definitions**: Lists descriptions of functions such as `query_order(order_id)`, `initiate_refund(...)`, and `contact_logistics(...)`.

2. **User input:** “My order #12345 hasn’t moved for several days, what’s going on?”
3. **Contextual Retrieval and Enhancement**:
    The backend program identified the order number `#12345`.
    Call `query_order(12345)` to get the order details and tracking number.
    Call `contact_logistics(logistics number)` to get the latest logistics status: "The package is stuck at the transit station due to weather conditions".
    * Add these **tool execution results** as new context information.

4. **Organize the complete context** (before sending to the LLM):
    ```
    [System Prompt]: ...(Fixed roles and rules)...
    [Dialogue with History]:
    User: My order #12345 hasn't been moved for several days, what's going on?
    [Tool call result]:
    Order 12345 details: ..., tracking number: LD789.
    - Logistics tracking results: The package is at XX transit station and is stuck due to heavy snow. It is expected to be delayed for 2-3 days.
    ```
5. **LLM generates answers**:
    The model understands the entire situation based on the **complete context** above.
    It generated the following response: "We completely understand your feelings. We have found that your package is stuck at the XX transit station due to the blizzard and is expected to take another 2-3 days to resume delivery. We have recorded the situation for you and will continue to follow up. We sincerely apologize for any inconvenience caused!"

6. **Update Context**:
    * The user's question and the agent's final answer are added as new **dialogue history** to the context of the next interaction to ensure continuity.

### Summarize

The principle behind context engineering for AI agents is essentially that **"the information environment shapes intelligent behavior"**. By systematically designing, filtering, organizing, and updating the information (context) input to the model, we can build a stateful, knowledge-rich, tool-using, and complex reasoning-capable intelligent agent on top of a stateless LLM.

It is not a single technique, but a comprehensive engineering and technical field involving **cue engineering, information retrieval, memory management, and workflow design**, which is key to developing powerful AI applications in the real world.


<h2 id="22. What are the mainstream AI agent frameworks currently available?">22. What are the mainstream AI agent frameworks currently available?</h2>

The current mainstream AI agent framework ecosystem is rich and diverse, each with its own focus. Rocky has summarized the core features of several prominent frameworks in the table below.

| **Framework Name** | **Core Features** | **Typical Application Scenarios** |
| :--- | :--- | :--- |
**LangChain** | Modular components, rich ecosystem, chained orchestration workflow | Rapid prototyping, highly customizable single-agent applications, such as document Q&A and customer service automation |
| **LangGraph** | Graph-based workflow, powerful state management and loop control | Complex decision-making systems, multi-agent coordination, long-cycle tasks |
**CrewAI** | Role-driven, emphasizing structured division of labor and collaboration among agents | Collaborative tasks with clear division of labor, such as content creation, data analysis, and business planning |
| **AutoGen** | Dialogue-driven, enabling agent collaboration through multi-turn natural language dialogue | Research and exploration, code generation, scenarios requiring creative thinking |
| **Semantic Kernel** | Enterprise-grade integration, robust security and compliance, plug-in architecture | Intelligent transformation of existing systems (such as .NET and Java applications) |
**Dify** | Low-code/no-code, visual interface, rapid build and deployment | Quickly build knowledge base Q&A and rapid prototyping for SMEs |
**OpenAI Agents SDK** | Lightweight, supports multiple models, and includes built-in debugging tools | Build elegant multi-agent systems |

In general, there is no "one-size-fits-all" framework; the best choice is the one that best suits your current scenario and resources. It is recommended to validate your ideas on a small scale before deciding on the final technical route.


<h2 id="23. What are the core modules included in current mainstream AI agents?">23. What are the core modules included in current mainstream AI agents?</h2>

Here are Rocky's summary of the **five core modules of an AI Agent**.

### Five Core Modules

#### 1. Planning Module
This is the "brain" of the AI ​​Agent, responsible for thinking and decision-making. It also includes several sub-capabilities:
- **Task decomposition**: Breaking down complex user instructions into a series of executable subtasks.
  - *For example: If a user says, "Make a PowerPoint presentation about market analysis," the agent will break it down into "1. Gather the latest market data; 2. Generate an analysis outline; 3. Write the content for each section; 4. Design the slide layout."*
- **Strategy Formulation**: Plan the best path and sequence to complete the task, and handle the dependencies between subtasks.
- **Reflection and Calibration**: During or after an action, evaluate whether the current results meet the requirements and perform self-correction. This is crucial for accomplishing complex tasks.

#### 2. Tool Usage Module
These are the Agent's "hands and feet," enabling it to interact with the world.
- **Tool Library**: A collection of external tools, APIs, or functions that an agent can invoke.
  - *For example: search engines, calculators, code interpreters, database query APIs, image generation models, file system operations, etc.*
- **Invocation and Execution**: Based on the decision of the planning module, the Agent selects the correct tool, generates the correct parameters (such as JSON for API calls), and executes the invocation.
- **Result Processing**: Receives the results returned by the tool, standardizes them, and passes them to other modules.

#### 3. Memory Module
This is the Agent's "experience base," used to store and retrieve information, and is divided into:
- **Short-term memory:** Preserves the context of the current conversation or task chain, ensuring the continuity of the dialogue.
- **Long-term memory:** Utilizing technologies such as vector databases, long-term knowledge, user preferences, historical decisions, and outcomes across dialogues are stored for future task reference. This enables the agent to "learn" and "grow."

#### 4. Action Output Module
This is the Agent's "final expression," which translates internal decisions into outputs that are perceptible to the user.
- **Generate Final Answer**: Generate a natural language response without requiring the use of tools or completion of all steps.
- **Generate structured instructions**: Generate instructions for tool calls when interaction with the environment is required.
- **Deliverable final form:** For example, returning a completed article, a piece of generated code, a created file, etc.

#### 5. The “Soul” of the Serial Module: The Perception and Reasoning Loop

Having these modules alone is not enough; the most crucial element is the **core control flow** that makes them work, namely the "perception-thinking-action" cycle, which is usually driven by the reasoning capabilities of the larger model.

1. **Perception**: Receiving user input and feedback from the environment.
2. **Thinking**:
    - The **Planning Module**, combined with the **Memory Module** (historical context and knowledge), determines what to do next.
    - If external tools are needed, the **tools using the module** will be activated.
3. **Action**:
    - The tool uses a module to execute the call and write the result back to the memory module.
    - **Planning Module:** Based on the results, **reflect** to determine whether the task is completed. If not completed, return to step 2 to continue thinking; if completed, the **Action Output Module** provides the final result.

### A complete example: AI Agent booking airline tickets

**User input:** “Please help me find the cheapest early morning flight from Beijing to Shanghai next Saturday, and tell me if I need to bring an umbrella.”

1. **Planning**: The tasks are broken down into: ① Checking flight information; ② Checking Shanghai weather; ③ Providing a comprehensive response.
2. **Tool Usage & Actions**:
    - Call the **flight query API** with parameters `{departure: "Beijing", arrival: "Shanghai", date: "next Saturday", sort: "price_asc"}`.
    - Store the result (e.g., "China Eastern MU123, 7:00, ¥550") in **memory**.
    - Call the **weather query API**, with parameters `{city: "Shanghai", date: "next Saturday"}`.
    - Store the result (e.g., "Sunny, 25°C") in **memory**.
3. **Planning & Reflection**: Check if all required information is available and if the task has been completed.
4. **Action Output**: Extract information from **memory** and generate the final response: "The cheapest early morning flight is China Eastern Airlines MU123, departing at 7:00 AM, priced at 550 yuan. It will be sunny in Shanghai that day, so you don't need an umbrella."

### Summarize

| Module | Function | Analogy |
| :--- | :--- | :--- |
| **Planning** | Thinking, Breaking Down, Reflecting | **Brain** |
| **Tool Usage** | Calling External Capabilities | **Hands and Feet** |
| **Memory** | Storage Context and Knowledge | **Notebooks and Experience** |
| **Action Output** | Generate Final Result | **Mouth and Pen** |
| **Perception and Reasoning Loop** | Driving Module Collaboration | **Nervous System** |

Currently, whether it's AutoGPT, ChatGPT's Advanced Data Analysis, or Meta's CICERO, these cutting-edge agent projects are essentially different implementations and enhancements of these core modules. The intelligence of an AI agent depends not only on the capabilities of its core large model, but also on the sophistication of the design and the efficiency of collaboration among these modules.


<h2 id="24. What are the differences between Memory and RAG in AI Agent?">24. What are the differences between Memory and RAG in AI Agent?</h2>

## **The Fundamental Difference Between Memory and RAG in AI Agents**

| Dimensions | **Memory** | **RAG** ​​|
|------|----------------|---------------|
| **Core Objectives** | Maintain the continuity, personalization, and state awareness of the AI ​​Agent | Provide external knowledge retrieval to enhance generative capabilities |
| **Stored Content** | Session history, user preferences, activity patterns, internal state | Structured/unstructured documents, knowledge base, factual data |
| **Time Dimension** | Short-term + long-term memory, exhibiting time-series characteristics | Static knowledge, typically not changing frequently over time |
| **Update Frequency** | Real-time, high frequency (may update with every interaction) | Low frequency, batch updates |
| **Data Structures** | Graph structures, sequence data, key-value pairs, vectors | Documents, vectors, index structures |

## **Technical Architecture Comparison**

### **1. Memory Mechanism**
```python
# Typical Memory System Architecture
class AgentMemory:
    def __init__(self):
        # Short-term memory (conversational context)
        self.short_term = []  
        
        # Long-term memory (vector storage)
        self.long_term = VectorStore()  
        
        # Experience memory (reinforcement learning)
        self.experience = ExperienceReplay()  
        
        # Working memory (current task status)
        self.working = TaskState()  

# Key Components:
# - Dialogue on History Management
# - State tracker
# - Experience Replay Buffer Pool
# - Memory compression/forgetting mechanism
# - Memory retrieval and association
```

### **2. RAG System**
```python
# Typical RAG Architecture
class RAGSystem:
    def __init__(self):
        # Document processing pipeline
        self.doc_processor = DocumentProcessor()
        
        # Vectorized Model
        self.embedder = EmbeddingModel()
        
        # Vector Database
        self.vector_db = VectorDatabase()
        
        # Searcher
        self.retriever = Retriever()
        
        # Rearranger
        self.reranker = Reranker()

# Key Components:
# - Document splitting and cleaning
# - Vector index building
# - Similarity Search Algorithm
# - Context compression and reorganization
# - Multi-hop search capability
```

## **Detailed Analysis of Functional Differences**

### **Core Functions of Memory**
1. **Session Continuity**
   ```python
   # Maintaining the context of multi-turn conversations
   memory = [
       {"role": "user", "content": "I like science fiction movies"},
       {"role": "assistant", "content": "Recommends Interstellar"},
       {"role": "user", "content": "Anything similar?"} # This relies on memory.
   ]
   ```

2. **Personalized Adaptation**
   - Learn user preferences (dislike of horror movies, preference for Chinese content, etc.)
   - Adapt to different interaction styles (formal/casual)
   - Remember user-specific information (birthday, occupation, etc.)

3. **State Maintenance**
   ```python
   # Task Status Memory
   task_state = {
       "current_step": 3,
       "completed_steps": ["Gathering requirements", "Analyzing data", "Generating an outline"],
       "next_action": "Write the execution plan",
       "constraints": ["Budget limit: $1000", "Time limit: 7 days"]
   }
   ```

4. **Learning from Experience**
   Learn from success/failure
   - Optimize decision-making strategies
   - Forming "muscle memory"

### **RAG's Core Functions**
1. **Knowledge Retrieval**
   ```python
   # Retrieve relevant information from the knowledge base
   query = "How to fix PostgreSQL connection errors?"
   retrieved_docs = vector_db.similarity_search(
       query=query, 
       k=5, # Returns the 5 most relevant documents
       filter={"source": "Official Documentation"}
   )
   ```

2. **Factual Enhancement**
   - Provide up-to-date information (to prevent LLM knowledge from becoming outdated)
   - Provide detailed data (statistics, technical details, etc.)
   - Provide authoritative source citations

3. **Specialization in the field**
   ```python
   # Professional domain knowledge retrieval
   medical_rag = RAGSystem(
       documents=medical_textbooks,
       embedding_model="med-bert",
       retrieval_strategy="hybrid_search"
   )
   ```

4. **Hallucination Suppression**
   - Generate answers based on real documents
   - Provide verifiable references
   - Reduce the risk of fabricating information

## **Comparison of Storage and Retrieval Methods**

### **Memory Storage Method**
```python
# 1. Vector memory (semantic retrieval)
memory_vectors = embedder.encode([
    "Users prefer vegetarian food"
    "Users are software engineers"
    "The user last asked a Python question"
])

# 2. Graph memory (relational storage)
memory_graph = {
    "user": {"likes": ["scifi", "coding"], "dislikes": ["horror"]},
    "projects": {"current": "AI Agent", "completed": ["Web App"]},
    "conversations": {"today": 5, "total": 342}
}

# 3. Sequential Memory (Timeline)
memory_timeline = [
    {"timestamp": "10:00", "action": "started_task", "details": "..."},
    {"timestamp": "10:15", "action": "requested_data", "details": "..."},
    {"timestamp": "10:30", "action": "completed_step", "details": "..."}
]
```

### **RAG Storage Method**
```python
# Document chunking and vectorization
documents = [
    "PostgreSQL Installation Guide..."
    Database optimization techniques...
    "Common error solutions..."
]

# Create a vector index
vector_index = VectorIndex(
    documents=documents,
    chunk_size=500, # 500 characters per block
    overlap=50, # 50 characters of overlap between blocks
    embedding_model="text-embedding-ada-002"
)

# Supports multiple search modes
retrieval_methods = {
    "dense": vector_index.dense_retrieval,
    "sparse": vector_index.bm25_retrieval,
    "hybrid": vector_index.hybrid_retrieval,
    "multi_vector": vector_index.multi_vector_retrieval
}
```

## **Comparison of Update Mechanisms**

### **Memory Update Features**
```python
class MemoryUpdate:
    # 1. Incremental Update
    def add_experience(self, experience):
        self.experience_buffer.append(experience)
        if len(self.experience_buffer) > capacity:
            self.compress_memory() # Memory compression
    
    # 2. Importance Weighting
    def weight_by_importance(self, memory_item):
        # Weighted based on usage frequency, emotional intensity, and task relevance
        importance_score = (
            frequency * 0.3 +
            recency * 0.2 +
            emotional_intensity * 0.2 +
            task_relevance * 0.3
        )
        return importance_score
    
    #3. Selective forgetting
    def forget_less_important(self, threshold=0.5):
        for item in self.memories:
            if item.importance < threshold:
                self.archive(item) # Archive, not delete.
```

### **RAG Update Features**
```python
class RAGUpdate:
    # 1. Batch Update
    def update_knowledge_base(self, new_documents):
        # Reprocess the entire document set or perform incremental updates
        if self.incremental_update_supported:
            self.vector_db.add_documents(new_documents)
        else:
            # The entire index needs to be rebuilt
            self.rebuild_index(existing_docs + new_documents)
    
    # 2. Version Control
    def create_snapshot(self, version):
        self.snapshots[version] = {
            "documents": deepcopy(self.documents),
            "index": deepcopy(self.vector_index),
            "timestamp": datetime.now()
        }
    
    # 3. Quality Filtration
    def filter_by_quality(self, documents, min_quality_score=0.7):
        return [doc for doc in documents 
                if self.quality_scorer(doc) >= min_quality_score]
```

## **Differences in Search Strategies**

### **Memory Retrieval Strategy**
```python
# Context-based association retrieval
def retrieve_relevant_memories(self, current_context, top_k=3):
    # 1. Time correlation
    recent_memories = self.get_recent_memories(hours=24)
    
    # 2. Semantic Relevance
    context_embedding = self.embedder.encode(current_context)
    similar_memories = self.vector_memory.search(
        query_vector=context_embedding,
        k=top_k
    )
    
    # 3. Task Relevance
    task_related = self.get_task_memories(
        task_type=current_context.task_type
    )
    
    # Overall Rating
    scored_memories = self.rank_memories(
        recent_memories + similar_memories + task_related,
        weights={"recent": 0.4, "semantic": 0.4, "task": 0.2}
    )
    
    return scored_memories[:top_k]
```

### **RAG Search Strategy**
```python
# Knowledge Retrieval Based on Query
def retrieve_relevant_documents(self, query, top_k=5):
    # 1. Dense Vector Search
    dense_results = self.vector_db.similarity_search(
        query=query, 
        k = top_k * 2 # Get more candidates
    )
    
    # 2. Sparse Search (Keywords)
    sparse_results = self.bm25_retriever.search(
        query=query,
        k=top_k*2
    )
    
    # 3. Hybrid Search
    hybrid_results = self.hybrid_search(
        dense_results, sparse_results,
        dense_weight=0.7, sparse_weight=0.3
    )
    
    # 4. Reordering
    reranked_results = self.reranker.rerank(
        query=query,
        documents=hybrid_results
    )
    
    return reranked_results[:top_k]
```

## **Comparison of Real-World Application Scenarios**

### **Suitable Scenarios for Using Memory**
1. **Dialogue System**
   ```python
   # Need to remember conversation history
   chatbot_with_memory = ChatAgent(
       memory=ConversationMemory(max_turns=10),
       personality=PersonalityTrait(
           tone="friendly", 
           expertise_level="intermediate"
       )
   )
   ```

2. **Continuous learning of the agent**
   ```python
   # Agents that learn from experience
   learning_agent = RLAgent(
       memory=ExperienceReplayBuffer(size=10000),
       policy_network=PolicyNet(),
       update_frequency=100 # Update every 100 steps
   )
   ```

3. **Personalized Assistant**
   ```python
   # Assistant that remembers user preferences
   personal_assistant = Assistant(
       memory=UserProfileMemory(
           preferences=["vegetarian", "early riser", "tech news"],
           habits=["Daily exercise", "Weekend reading"],
           constraints=["Nut allergy", "Limited budget"]
       )
   )
   ```

### **Suitable Scenarios for Using RAG**
1. **Enterprise Knowledge Base Q&A**
   ```python
   # Q&A based on enterprise documents
   company_qa = RAGSystem(
       documents=[
           "Employee Handbook.pdf"
           "Technical Documentation"
           Project Report
           Meeting minutes
       ],
       retrieval_config={
           "chunk_size": 1000,
           "search_strategy": "hybrid",
           "reranker": "cross-encoder"
       }
   )
   ```

2. **Fact Check System**
   ```python
   # Verify the accuracy of the information
   fact_checker = FactCheckingSystem(
       knowledge_sources=[
           WikipediaDump(),
           NewsArticles(),
           AcademicPapers(),
           GovernmentReports()
       ],
       citation_required=True,
       confidence_threshold=0.8
   )
   ```

3. **Technical Documentation Assistant**
   ```python
   # Provide technical support and documentation search
   tech_support = TechDocAssistant(
       docs=["API documentation", "tutorials", "FAQ", "error code manual"],
       search_features={
           "code_search": True,
           "error_code_lookup": True,
           "version_specific": True
       }
   )
   ```

## **Performance and Scalability Considerations**

| Features | Memory | RAG |
|------|---------|-----|
| **Latency Requirement** | Extremely low (ms level) | Medium (100ms-1s) |
Storage Costs | Relatively Low (User Level) | Potentially High (Enterprise Level)
| **Scalability** | Horizontal scaling (by user) | Vertical/horizontal scaling (by data volume) |
| **Privacy** | Highly Sensitive (User Data) | Medium Sensitive (Enterprise Knowledge) |
| **Backup Requirement** | Important (Personalized Data) | Very Important (Knowledge Assets) |

Rocky believes that the two are not substitutes for each other, but rather complementary technologies. Modern AI agents typically possess both capabilities simultaneously, resulting in more intelligent and reliable systems.

