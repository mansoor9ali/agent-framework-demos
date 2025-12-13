from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.workflow.agent_state import AgentState
from src.llm_client import LLMClient
from src.workflow.evaluation.evaluator import Evaluator


class GroundednessEvaluator(Evaluator):
    """Evaluates how well responses are grounded in retrieved context documents.
    
    This evaluator assesses the factual grounding of generated responses by
    analyzing how well each claim or statement in the response is supported
    by the retrieved nutritional context. It provides a quantitative score
    that measures the degree to which the response avoids hallucinations
    and stays faithful to the source documents.
    
    The evaluator uses sophisticated prompt engineering to break down responses
    into discrete claims, verify each claim against the context, and calculate
    a comprehensive groundedness score from 0 to 10. This scoring helps the
    workflow determine whether response refinement is needed.
    
    Key evaluation criteria include:
    - Verification of factual claims against context
    - Detection of hallucinations or unsupported statements
    - Assessment of reasonable inferences from context
    - Identification of contradictions with source material
    - Evaluation of appropriate uncertainty expression
    
    The groundedness evaluation is crucial for maintaining reliability and
    trustworthiness in nutrition care applications where accuracy is paramount.
    
    Attributes:
        system_message (str): Comprehensive instructions for groundedness evaluation.
        groundedness_prompt (ChatPromptTemplate): Template for evaluation prompts.
        chain: Processing pipeline for generating groundedness scores.
    """
    
    def __init__(self):
        self.system_message = """
        You are a specialized evaluation system designed to assess and quantify the
        groundedness of a response based on retrieved context.

        Your task is to analyze how well a response is supported by the provided context and assign a numerical groundedness score.

        #Evaluation Process
        For each evaluation request, you will:

        - Analyze the retrieved context provided
        - Examine the response being evaluated
        - Break down the response into distinct claims or statements
        - Verify each claim against the context
        - Calculate a numerical groundedness score from 0 to 10

        #Score Calculation
        Determine the ratio of supported claims (direct + reasonable inferences) to total claims
        Apply the scoring guidelines while considering:

          - The severity of any hallucinations (minor vs. major)
          - The centrality of unsupported claims to the overall response
          - The presence of contradictions with the context
          - The appropriate expression of uncertainty for ambiguous information

        #Output
        You should only return a numerical groundedness score and nothing else.
        """

        self.groundedness_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            ("user", "Context: {context}\nResponse: {response}\n\nGroundedness score:")
        ])

        self.chain = self.groundedness_prompt | LLMClient.get_llm_client() | StrOutputParser()

    def evaluate(self, state: AgentState) -> AgentState:
        """Evaluate the groundedness of a response against retrieved context.
        
        This method assesses how well the generated response is supported by the
        retrieved nutritional context documents. It analyzes each claim in the
        response, verifies support from the context, and calculates a numerical
        groundedness score from 0 to 10.
        
        The evaluation process includes:
        1. Breaking down the response into discrete claims and statements
        2. Verifying each claim against the provided context documents
        3. Identifying direct support, reasonable inferences, and unsupported claims
        4. Calculating a comprehensive groundedness score
        5. Updating the iteration count for workflow control
        
        Higher scores indicate better grounding in the source material, while
        lower scores suggest the presence of hallucinations or unsupported
        statements that require response refinement.
        
        Args:
            state (AgentState): The current workflow state containing:
                               - 'response': The generated response to evaluate
                               - 'context': List of retrieved documents with content
                               - 'groundedness_loop_count': Current iteration count
        
        Returns:
            AgentState: The updated state with:
                       - 'groundedness_score': Numerical score (0-10) indicating
                         how well the response is grounded in context
                       - 'groundedness_loop_count': Incremented iteration count
        
        Raises:
            KeyError: If required state keys are missing.
            ValueError: If the LLM output cannot be parsed as a float.
            Exception: If there are issues with the evaluation process.
        
        """
        groundedness_score = float(self.chain.invoke({
            "context": "\n".join([doc["content"] for doc in state['context']]),
            "response": state['response']
        }))
        
        state['groundedness_loop_count'] += 1
        state['groundedness_score'] = groundedness_score

        return state
